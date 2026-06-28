#!/usr/bin/env python3
"""Generate ephemeral eval fixtures from Aider polyglot-benchmark (Exercism) exercises.

The polyglot benchmark is the 225 hardest Exercism problems across 6 languages, chosen
because <=3 of 7 top models solved them — i.e. calibrated to the model's margin, which is
exactly where a governance effect can show (the baseline ceiling-effect run could not).

No Exercism content is committed to this repo. A generated fixture references the
benchmark by path (`source.copy_dir`) and EXCLUDES the reference solution (`.meta/`); the
only committed artifacts are this generator and a curated list of exercise IDs. Generate
fixtures into a scratch dir, then run them with run_fixture.py / run_trials.py.

Caveat: these exercises are public, so a model may recall a solution from training
(memorization). The reference is excluded from the workspace and history is isolated, but
training recall cannot be fully prevented — the calibrated-hard set mitigates it (hard
despite being public). Treat polyglot results as scaffold-specific, like Aider's own.

Usage:
    python3 tools/polyglot_fixture.py <bench_root> <out_dir> python:bowling rust:accumulate ...
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

LANG: dict[str, dict[str, Any]] = {
    "python": {
        "sub": "python/exercises/practice",
        "verify": "python3 -m unittest discover -p '*_test.py'",
        "setup": [],
        "exclude": [".meta", ".docs", ".exercism", "__pycache__"],
    },
    "javascript": {
        "sub": "javascript/exercises/practice",
        "verify": "npm test",
        "setup": ["npm install --no-audit --no-fund --silent"],
        "exclude": [".meta", ".docs", ".exercism", "node_modules"],
    },
    "rust": {
        "sub": "rust/exercises/practice",
        "verify": "cargo test --quiet",
        "setup": [],
        "exclude": [".meta", ".docs", ".exercism", "target"],
    },
}


def exercise_dir(bench_root: str | Path, language: str, exercise: str) -> Path:
    return Path(bench_root).expanduser().resolve() / LANG[language]["sub"] / exercise


def _files(ex_dir: Path) -> dict[str, list[str]]:
    cfg = json.loads((ex_dir / ".meta" / "config.json").read_text(encoding="utf-8"))
    return cfg.get("files", {})


def fixture_id(language: str, exercise: str) -> str:
    return f"poly_{language[:2]}_{exercise}".replace("-", "_")


def build(bench_root: str | Path, language: str, exercise: str, out_dir: str | Path) -> Path:
    if language not in LANG:
        raise ValueError(f"unsupported language: {language} (have {', '.join(LANG)})")
    spec = LANG[language]
    ex_dir = exercise_dir(bench_root, language, exercise)
    if not ex_dir.is_dir():
        raise FileNotFoundError(f"exercise not found: {ex_dir}")
    files = _files(ex_dir)
    solution = files.get("solution", [])
    tests = files.get("test", [])

    instr = (ex_dir / ".docs" / "instructions.md").read_text(encoding="utf-8")
    append = ex_dir / ".docs" / "instructions.append.md"
    if append.exists():
        instr += "\n\n" + append.read_text(encoding="utf-8")

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    prompt = (
        instr.strip() + "\n\n---\n\n"
        f"Implement the solution by editing only: {', '.join(solution) or 'the solution source file(s)'}.\n"
        f"Do not modify the test file(s): {', '.join(tests) or '(the tests)'}.\n"
        "Use only the standard library / the dependencies already present. "
        "Make the failing tests pass.\n"
    )
    (out / "PROMPT.md").write_text(prompt, encoding="utf-8")
    (out / "TASK.md").write_text(
        f"# Polyglot benchmark fixture — {language}/{exercise}\n\n"
        "> Harness documentation only. The agent prompt is PROMPT.md (Exercism instructions).\n\n"
        "Generated from the Aider polyglot benchmark (Exercism). Source referenced by path; "
        "the reference solution (`.meta/`) is excluded from the workspace. Public exercise — "
        "training-contamination caveat applies.\n", encoding="utf-8")
    fixture = {
        "id": fixture_id(language, exercise),
        "language": language,
        "kind": "benchmark",
        "source": {"copy_dir": str(ex_dir), "exclude": spec["exclude"]},
        "setup": spec["setup"],
        "verify": spec["verify"],
        "task": "TASK.md",
    }
    (out / "fixture.json").write_text(json.dumps(fixture, indent=2), encoding="utf-8")
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: polyglot_fixture.py <bench_root> <out_dir> <language:exercise> ...", file=sys.stderr)
        return 2
    bench_root, out_base = argv[0], argv[1]
    for spec in argv[2:]:
        language, _, exercise = spec.partition(":")
        out = build(bench_root, language, exercise, Path(out_base) / fixture_id(language, exercise))
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
