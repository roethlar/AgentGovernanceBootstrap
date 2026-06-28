#!/usr/bin/env python3
"""Aggregate recorded trial results into a cross-profile comparison.

Reads evals/results/*.json (written by run_trials.py) and prints, per fixture, the
pass rate under each governance profile plus a tamper count (trials where the agent
edited a test file — which would invalidate a "pass"). This is how a baseline is read:
does current-template / candidate-loop-first change the pass rate vs none?
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "evals" / "results"

# Filenames that look like test files across the toolchains we use.
_TEST_RX = re.compile(r"(^|/)(test_[^/]+\.py|[^/]+_test\.[a-z]+|[^/]+\.test\.[a-z]+|"
                      r"[^/]+\.spec\.[a-z]+|[^/]+\.Tests\.ps1)$", re.I)


def is_test_file(path: str) -> bool:
    return bool(_TEST_RX.search(path))


def load_results(results_dir: Path) -> list[dict[str, Any]]:
    out = []
    for f in sorted(results_dir.glob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return out


def aggregate(results: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    agg: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {"runs": 0, "passes": 0, "sec_runs": 0, "sec_passes": 0,
                 "tampered": 0, "durations": []})
    for r in results:
        key = (r.get("id", "?"), r.get("profile", "?"))
        a = agg[key]
        a["runs"] += 1
        a["passes"] += 1 if r.get("functional_pass") else 0
        if r.get("security_pass") is not None:
            a["sec_runs"] += 1
            a["sec_passes"] += 1 if r.get("security_pass") else 0
        changed = (r.get("driver") or {}).get("changed_files") or []
        if any(is_test_file(p) for p in changed):
            a["tampered"] += 1
        if r.get("duration_sec"):
            a["durations"].append(r["duration_sec"])
    for a in agg.values():
        a["pass_rate"] = round(a["passes"] / a["runs"], 3) if a["runs"] else 0.0
        a["sec_rate"] = round(a["sec_passes"] / a["sec_runs"], 3) if a["sec_runs"] else None
        a["avg_sec"] = round(sum(a["durations"]) / len(a["durations"]), 1) if a["durations"] else 0.0
    return agg


def format_table(agg: dict[tuple[str, str], dict[str, Any]]) -> str:
    lines = [f"{'fixture':40} {'profile':22} {'func':>7} {'rate':>6} {'sec':>7} {'tamper':>7} {'avg_s':>7}"]
    for (fid, profile), a in sorted(agg.items()):
        flag = "  TAMPER" if a["tampered"] else ""
        sec = f"{a['sec_passes']}/{a['sec_runs']}" if a["sec_runs"] else "-"
        lines.append(f"{fid:40} {profile:22} {a['passes']:>3}/{a['runs']:<3} "
                     f"{a['pass_rate']:>6} {sec:>7} {a['tampered']:>7} {a['avg_sec']:>7}{flag}")
    # Per-fixture delta vs the 'none' baseline.
    by_fix: dict[str, dict[str, float]] = defaultdict(dict)
    for (fid, profile), a in agg.items():
        by_fix[fid][profile] = a["pass_rate"]
    lines.append("")
    lines.append("delta vs none (pass_rate):")
    for fid, profiles in sorted(by_fix.items()):
        base = profiles.get("none")
        if base is None:
            continue
        deltas = " ".join(f"{p}={profiles[p] - base:+.3f}" for p in sorted(profiles) if p != "none")
        lines.append(f"  {fid:40} {deltas}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Aggregate trial results into a comparison.")
    p.add_argument("results_dir", nargs="?", default=str(RESULTS_DIR))
    p.add_argument("--run", default=None, help="only include trials whose run_id starts with this")
    args = p.parse_args(argv)
    results = load_results(Path(args.results_dir))
    if args.run:
        results = [r for r in results if str(r.get("run_id", "")).startswith(args.run)]
    if not results:
        print(f"no results in {args.results_dir}" + (f" for run '{args.run}'" if args.run else ""))
        return 0
    label = f" (run '{args.run}')" if args.run else ""
    print(f"{len(results)} trials in {args.results_dir}{label}\n")
    print(format_table(aggregate(results)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
