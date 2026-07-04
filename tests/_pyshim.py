"""Ensure a working `python3` on PATH for tests that execute declared shell
commands (fixture `verify` strings, hook verify commands) via the real host
shell.

On stock Windows, `python3` on PATH is the Microsoft Store App Execution
Alias stub: it exists, runs nothing, and exits 9009 — the exact pitfall the
product handles in the discovery probe (2026-06-10 decision) and the shipped
hook commands (2026-07-02 decision). Fixture data declares `python3` as its
interpreter contract; rather than rewriting frozen fixtures per-platform,
this helper makes the contract hold: if `python3` cannot run Python, prepend
a scratch shim that execs `sys.executable`. A no-op wherever `python3`
already works, so POSIX runs are unchanged.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

_installed = False


def _python3_works() -> bool:
    try:
        p = subprocess.run(
            ["python3", "-c", "print('ok')"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return p.returncode == 0 and p.stdout.strip() == "ok"


def ensure_python3() -> None:
    """Idempotent: probe once; shim only if `python3` is absent or a stub."""
    global _installed
    if _installed or _python3_works():
        _installed = True
        return
    shim_dir = tempfile.mkdtemp(prefix="agb-pyshim-")
    if os.name == "nt":
        # shell=True on Windows is cmd.exe; PATHEXT resolves .bat from PATH.
        with open(os.path.join(shim_dir, "python3.bat"), "w", encoding="utf-8") as f:
            f.write(f'@"{sys.executable}" %*\n')
    else:
        shim = os.path.join(shim_dir, "python3")
        with open(shim, "w", encoding="utf-8") as f:
            f.write(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
        os.chmod(shim, 0o755)
    os.environ["PATH"] = shim_dir + os.pathsep + os.environ.get("PATH", "")
    _installed = True
