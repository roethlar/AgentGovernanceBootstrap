#!/usr/bin/env python3
"""Agent drivers for eval trials.

A *driver* runs a coding agent headless inside an already-scaffolded fixture workspace
(parent state + injected failing test, optionally with a governance profile overlaid).
The agent edits files in place; `run_fixture.score_fixture` then runs the fixture's own
verify command to score the outcome. Drivers are best-effort and harness-specific — they
are how the eval measures one native harness against another.

Each driver is a callable `(workdir, fixture_dir, manifest, env_extra) -> dict` returning
at least {"driver", "exit", "duration_sec", "changed_files"}.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

# The agent is told to fix the failing test by editing source only. We deliberately do
# NOT reveal the verify command's internals or the reference solution.
PROMPT_WRAPPER = """You are fixing a defect in the repository at your current working directory.
A test in this repository is currently failing. Make it pass.

Rules:
- Edit only source files. Do NOT modify, delete, disable, or weaken any test file, and do
  not change how tests are run.
- Make the smallest change that makes the failing test pass; do not delete assertions or
  add skips, and do not change unrelated behavior.

Task:
{task}
"""


def agent_prompt(fixture_dir: Path, manifest: dict[str, Any]) -> str:
    """Return the agent-facing prompt — and ONLY that.

    A driven fixture ships a dedicated, curated `PROMPT.md` containing just the task. We
    deliberately do NOT derive the prompt from TASK.md: TASK.md is harness documentation
    and carries provenance (source repo slug, base/fix SHAs, solution paths) that an
    agent could use to locate the source checkout on disk and read the reference fix.
    The prompt source is hardcoded to PROMPT.md (no manifest override) so a fixture
    cannot opt back into a provenance-bearing file. The prompt must name only workspace
    files, never the origin repo or its commits."""
    path = fixture_dir / "PROMPT.md"
    if not path.exists():
        raise FileNotFoundError(
            f"{fixture_dir.name}: no agent prompt (PROMPT.md); a driven fixture must "
            f"ship a curated PROMPT.md with no source/commit provenance")
    return path.read_text(encoding="utf-8").strip()


def _changed_files(workdir: Path) -> list[str]:
    """Files the agent changed relative to the trial-base commit."""
    out = subprocess.run(["git", "-C", str(workdir), "status", "--porcelain"],
                         capture_output=True, text=True).stdout
    return [line[3:] for line in out.splitlines() if line.strip()]


def _parse_claude_telemetry(stdout: str, stderr: str) -> dict[str, Any]:
    """Parse Claude Code's `--output-format json` result envelope (or a stream-json
    tail) for usage. Claude prints a final JSON object with `total_cost_usd` and a
    `usage` block; tool calls appear as `assistant` messages with `tool_use` content
    in stream-json. Missing field -> None (absence is data, not zero)."""
    tokens = cost = tool_calls = None
    # Final result envelope: the last well-formed JSON object on stdout.
    obj = _last_json_object(stdout)
    if obj:
        cost = obj.get("total_cost_usd", obj.get("cost_usd", cost))
        usage = obj.get("usage") or {}
        it, ot = usage.get("input_tokens"), usage.get("output_tokens")
        if it is not None or ot is not None:
            tokens = (it or 0) + (ot or 0)
        if obj.get("num_turns") is not None and tool_calls is None:
            # not tool calls per se, but a usable activity proxy when stream absent
            pass
    # Stream-json: count tool_use blocks across assistant events.
    tc = _count_stream_tool_uses(stdout)
    if tc is not None:
        tool_calls = tc
    return {"tokens": tokens, "cost": cost, "tool_calls": tool_calls}


def _parse_generic_telemetry(stdout: str, stderr: str) -> dict[str, Any]:
    """Best-effort for harnesses without a structured usage envelope (codex, grok):
    nothing reliably machine-readable today, so record explicit nulls. A later slice
    can add a real parser per harness; absence is recorded honestly meanwhile."""
    return {"tokens": None, "cost": None, "tool_calls": None}


def _last_json_object(text: str) -> "dict[str, Any] | None":
    """Return the last top-level JSON object found scanning lines bottom-up, or None.
    Tolerant of non-JSON log lines interleaved with a final JSON result."""
    import json
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
    return None


def _count_stream_tool_uses(text: str) -> "int | None":
    """Count tool_use content blocks in a Claude stream-json stdout. Returns None if
    the output is not stream-json (no parseable event lines at all)."""
    import json
    seen_any = False
    count = 0
    for line in text.splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        seen_any = True
        msg = evt.get("message") if isinstance(evt, dict) else None
        content = (msg or {}).get("content") if isinstance(msg, dict) else None
        if isinstance(content, list):
            count += sum(1 for c in content if isinstance(c, dict) and c.get("type") == "tool_use")
    return count if seen_any else None


_TELEMETRY_PARSERS = {
    "claude": _parse_claude_telemetry,
}


def parse_telemetry(driver_name: str, stdout: str, stderr: str) -> dict[str, Any]:
    """Dispatch to a per-harness telemetry parser by driver name prefix. Unknown /
    unstructured harnesses fall back to explicit nulls."""
    base = driver_name.split(":", 1)[0]
    parser = _TELEMETRY_PARSERS.get(base, _parse_generic_telemetry)
    return parser(stdout, stderr)


def _finalize(driver_name: str, exit_code: int, started: float, workdir: Path,
              stdout: str, stderr: str) -> dict[str, Any]:
    """Build the common driver result. Raw stdout/stderr are attached under the
    underscore-prefixed `_stdout`/`_stderr` keys — score_fixture writes them to the
    gitignored transcript file and then DELETES these keys before the result is
    recorded, so raw agent output (possibly carrying source/prompts/secrets) never
    lands in a tracked evals/results/*.json."""
    tele = parse_telemetry(driver_name, stdout, stderr)
    return {
        "driver": driver_name,
        "exit": exit_code,
        "duration_sec": round(time.monotonic() - started, 1),
        "changed_files": _changed_files(workdir),
        "tool_calls": tele["tool_calls"],
        "tokens": tele["tokens"],
        "cost": tele["cost"],
        "error_tail": stderr[-500:] if exit_code != 0 else "",
        "_stdout": stdout,
        "_stderr": stderr,
    }


def codex_driver(workdir: Path, fixture_dir: Path, manifest: dict[str, Any],
                 env_extra: dict[str, str] | None = None, timeout: int = 1800) -> dict[str, Any]:
    prompt = PROMPT_WRAPPER.format(task=agent_prompt(fixture_dir, manifest))
    env = dict(os.environ)
    env.update(env_extra or {})
    started = time.monotonic()
    try:
        # Prompt via stdin (codex's argv form hangs on stdin). workspace-write so the
        # agent can edit; the workspace was reinitialized to trial-base so there is no
        # source history to crib from.
        proc = subprocess.run(
            ["codex", "exec", "--sandbox", "workspace-write", "--skip-git-repo-check", "-"],
            cwd=str(workdir), input=prompt, capture_output=True, text=True,
            timeout=timeout, env=env,
        )
        exit_code, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code, out, err = 124, exc.stdout or "", f"TIMEOUT after {timeout}s"
    return _finalize("codex", exit_code, started, workdir, out, err)


def claude_driver(workdir: Path, fixture_dir: Path, manifest: dict[str, Any],
                  env_extra: dict[str, str] | None = None, timeout: int = 1800,
                  model: str | None = None) -> dict[str, Any]:
    """Drive Claude Code natively. `model` selects a specific Claude model (e.g. a weaker
    older one — haiku/sonnet — to expose margin where Opus/codex ceiling); None uses the
    session default. Native tool-use, no proxy."""
    prompt = PROMPT_WRAPPER.format(task=agent_prompt(fixture_dir, manifest))
    env = dict(os.environ)
    env.update(env_extra or {})
    # --output-format json emits a final result envelope carrying usage + cost, which
    # _parse_claude_telemetry reads; --verbose stream-json would add per-tool events
    # but the result envelope is enough for tokens/cost.
    cmd = ["claude", "-p", prompt, "--permission-mode", "acceptEdits",
           "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    started = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True,
                              timeout=timeout, env=env)
        exit_code, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code, out, err = 124, exc.stdout or "", f"TIMEOUT after {timeout}s"
    return _finalize(f"claude:{model}" if model else "claude", exit_code, started,
                     workdir, out, err)


def grok_driver(workdir: Path, fixture_dir: Path, manifest: dict[str, Any],
                env_extra: dict[str, str] | None = None, timeout: int = 1800) -> dict[str, Any]:
    prompt = PROMPT_WRAPPER.format(task=agent_prompt(fixture_dir, manifest))
    env = dict(os.environ)
    env.update(env_extra or {})
    started = time.monotonic()
    try:
        # grok -p: single-turn headless agent; --always-approve so it can edit files
        # without interactive approval. Runs in the workspace cwd.
        proc = subprocess.run(
            ["grok", "-p", prompt, "--always-approve", "--output-format", "plain"],
            cwd=str(workdir), capture_output=True, text=True, timeout=timeout, env=env,
        )
        exit_code, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code, out, err = 124, exc.stdout or "", f"TIMEOUT after {timeout}s"
    return _finalize("grok", exit_code, started, workdir, out, err)


def ollama_driver(model: str) -> Callable[..., dict[str, Any]]:
    """Drive a local/proxied ollama model through Claude Code, pointed at an
    Anthropic-compatible proxy (default the headroom router; override with
    AGB_OLLAMA_BASE_URL). Used to exercise weaker models that have margin where frontier
    models ceiling — and to test governance's effect on small/local models."""
    base_url = os.environ.get("AGB_OLLAMA_BASE_URL", "http://10.1.10.221:8788")

    def drive(workdir: Path, fixture_dir: Path, manifest: dict[str, Any],
              env_extra: dict[str, str] | None = None, timeout: int = 2400) -> dict[str, Any]:
        prompt = PROMPT_WRAPPER.format(task=agent_prompt(fixture_dir, manifest))
        env = dict(os.environ)
        env.update({"ANTHROPIC_AUTH_TOKEN": "ollama", "ANTHROPIC_API_KEY": ""})
        env.update(env_extra or {})
        started = time.monotonic()
        try:
            proc = subprocess.run(
                ["claude", "-p", prompt, "--permission-mode", "acceptEdits",
                 "--output-format", "json", "--model", model, "--settings",
                 '{"env":{"ANTHROPIC_BASE_URL":"' + base_url + '"}}'],
                cwd=str(workdir), capture_output=True, text=True, timeout=timeout, env=env,
            )
            exit_code, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            exit_code, out, err = 124, exc.stdout or "", f"TIMEOUT after {timeout}s"
        # ollama runs through Claude Code, so the Claude usage envelope applies; name
        # the result ollama:<model> but parse with the claude telemetry parser.
        r = _finalize("claude", exit_code, started, workdir, out, err)
        r["driver"] = f"ollama:{model}"
        return r

    return drive


_DRIVERS: dict[str, Callable[..., dict[str, Any]]] = {
    "codex": codex_driver,
    "claude": claude_driver,
    "grok": grok_driver,
}


def get_driver(name: str) -> Callable[..., dict[str, Any]]:
    # `ollama:<model>` builds a proxied-model driver on the fly (model names contain ':',
    # so split only on the first).
    if name.startswith("ollama:"):
        return ollama_driver(name.split(":", 1)[1])
    if name.startswith("claude:"):
        model = name.split(":", 1)[1]
        return lambda *a, **k: claude_driver(*a, model=model, **k)
    if name not in _DRIVERS:
        raise ValueError(f"unknown driver: {name} (have: {', '.join(sorted(_DRIVERS))})")
    return _DRIVERS[name]
