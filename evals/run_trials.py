#!/usr/bin/env python3
"""Run a matrix of agent-driven trials across fixtures and governance profiles, record
each result, and summarize pass rates per (fixture, profile).

This is the baseline-measurement entry point: once a driver exists, comparing `none`
vs `current-template` (and later candidate profiles) on the same fixtures is how we tell
whether governance helps. Real runs are expensive (one agent trial can take minutes), so
this is invoked deliberately, e.g.:

    python3 evals/run_trials.py --driver codex --profiles none,current-template \
        --n 3 evals/fixtures/ts_qbit_confirmdelete_gold

Results land under evals/results/ (scores + hashes only; never repo contents).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
import run_fixture  # noqa: E402

RESULTS_DIR = REPO_ROOT / "evals" / "results"


def run_matrix(
    fixtures: list[Path], profiles: list[str], n: int,
    driver: Callable[..., dict[str, Any]] | None, run_id_prefix: str = "trial",
    record: bool = False,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for fx in fixtures:
        for profile in profiles:
            for i in range(n):
                run_id = f"{run_id_prefix}-{profile}-{i}"
                r = run_fixture.score_fixture(Path(fx), profile=profile, run_id=run_id, driver=driver)
                results.append(r)
                if record:
                    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
                    out = RESULTS_DIR / f"{r['id']}-{profile}-{run_id}.json"
                    out.write_text(json.dumps(r, indent=2), encoding="utf-8")
    return results


def summarize(results: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    agg: dict[tuple[str, str], dict[str, Any]] = {}
    for r in results:
        key = (r["id"], r["profile"])
        a = agg.setdefault(key, {"runs": 0, "passes": 0})
        a["runs"] += 1
        a["passes"] += 1 if r.get("functional_pass") else 0
    for a in agg.values():
        a["pass_rate"] = round(a["passes"] / a["runs"], 3) if a["runs"] else 0.0
    return agg


def _print_summary(agg: dict[tuple[str, str], dict[str, Any]]) -> None:
    print(f"{'fixture':40} {'profile':20} {'pass/runs':>10} {'rate':>6}")
    for (fid, profile), a in sorted(agg.items()):
        print(f"{fid:40} {profile:20} {a['passes']:>4}/{a['runs']:<5} {a['pass_rate']:>6}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run a matrix of eval trials.")
    p.add_argument("fixtures", nargs="+", help="fixture directories")
    p.add_argument("--profiles", default="none", help="comma-separated profiles")
    p.add_argument("--driver", default=None, help="agent driver (e.g. 'codex'); omit to score as-is")
    p.add_argument("--n", type=int, default=1, help="runs per (fixture, profile)")
    p.add_argument("--run-id", default="trial", help="run id prefix")
    p.add_argument("--no-record", action="store_true", help="do not write result JSON")
    args = p.parse_args(argv)

    driver = None
    if args.driver:
        import drivers
        driver = drivers.get_driver(args.driver)
    results = run_matrix(
        [Path(f) for f in args.fixtures], args.profiles.split(","), args.n,
        driver, run_id_prefix=args.run_id, record=not args.no_record,
    )
    _print_summary(summarize(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
