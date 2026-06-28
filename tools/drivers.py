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


def read_task_prompt(fixture_dir: Path, manifest: dict[str, Any]) -> str:
    """Return the agent-facing task text: the fixture's TASK file up to the harness-only
    '## Oracle' section (which would leak the verify command and solution paths)."""
    task_file = manifest.get("task", "TASK.md")
    text = (fixture_dir / task_file).read_text(encoding="utf-8")
    marker = text.find("## Oracle")
    return (text[:marker] if marker != -1 else text).strip()


def _changed_files(workdir: Path) -> list[str]:
    """Files the agent changed relative to the trial-base commit."""
    out = subprocess.run(["git", "-C", str(workdir), "status", "--porcelain"],
                         capture_output=True, text=True).stdout
    return [line[3:] for line in out.splitlines() if line.strip()]


def codex_driver(workdir: Path, fixture_dir: Path, manifest: dict[str, Any],
                 env_extra: dict[str, str] | None = None, timeout: int = 1800) -> dict[str, Any]:
    prompt = PROMPT_WRAPPER.format(task=read_task_prompt(fixture_dir, manifest))
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
    prompt = PROMPT_WRAPPER.format(task=read_task_prompt(fixture_dir, manifest))
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


_DRIVERS: dict[str, Callable[..., dict[str, Any]]] = {
    "codex": codex_driver,
    "claude": claude_driver,
}


def get_driver(name: str) -> Callable[..., dict[str, Any]]:
    if name not in _DRIVERS:
        raise ValueError(f"unknown driver: {name} (have: {', '.join(sorted(_DRIVERS))})")
    return _DRIVERS[name]
