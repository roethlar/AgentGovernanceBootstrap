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
        exit_code, err = proc.returncode, proc.stderr[-500:]
    except subprocess.TimeoutExpired:
        exit_code, err = 124, f"TIMEOUT after {timeout}s"
    return {
        "driver": "codex",
        "exit": exit_code,
        "duration_sec": round(time.monotonic() - started, 1),
        "changed_files": _changed_files(workdir),
        "error_tail": err if exit_code != 0 else "",
    }


def claude_driver(workdir: Path, fixture_dir: Path, manifest: dict[str, Any],
                  env_extra: dict[str, str] | None = None, timeout: int = 1800) -> dict[str, Any]:
    prompt = PROMPT_WRAPPER.format(task=agent_prompt(fixture_dir, manifest))
    env = dict(os.environ)
    env.update(env_extra or {})
    started = time.monotonic()
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--permission-mode", "acceptEdits"],
            cwd=str(workdir), capture_output=True, text=True, timeout=timeout, env=env,
        )
        exit_code, err = proc.returncode, proc.stderr[-500:]
    except subprocess.TimeoutExpired:
        exit_code, err = 124, f"TIMEOUT after {timeout}s"
    return {
        "driver": "claude",
        "exit": exit_code,
        "duration_sec": round(time.monotonic() - started, 1),
        "changed_files": _changed_files(workdir),
        "error_tail": err if exit_code != 0 else "",
    }


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
        exit_code, err = proc.returncode, proc.stderr[-500:]
    except subprocess.TimeoutExpired:
        exit_code, err = 124, f"TIMEOUT after {timeout}s"
    return {
        "driver": "grok",
        "exit": exit_code,
        "duration_sec": round(time.monotonic() - started, 1),
        "changed_files": _changed_files(workdir),
        "error_tail": err if exit_code != 0 else "",
    }


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
                 "--model", model, "--settings",
                 '{"env":{"ANTHROPIC_BASE_URL":"' + base_url + '"}}'],
                cwd=str(workdir), capture_output=True, text=True, timeout=timeout, env=env,
            )
            exit_code, err = proc.returncode, proc.stderr[-500:]
        except subprocess.TimeoutExpired:
            exit_code, err = 124, f"TIMEOUT after {timeout}s"
        return {
            "driver": f"ollama:{model}",
            "exit": exit_code,
            "duration_sec": round(time.monotonic() - started, 1),
            "changed_files": _changed_files(workdir),
            "error_tail": err if exit_code != 0 else "",
        }

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
    if name not in _DRIVERS:
        raise ValueError(f"unknown driver: {name} (have: {', '.join(sorted(_DRIVERS))})")
    return _DRIVERS[name]
