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


# Non-test paths the agent must never edit for a trial to count: the verify-runner
# config and governance/hook files. Editing these games the measurement.
_PROTECTED_RX = re.compile(
    r"(^|/)(\.claude/|AGENTS\.md$|CLAUDE\.md$|GEMINI\.md$|"
    r"package\.json$|Cargo\.toml$|go\.mod$|pyproject\.toml$|vitest\.config\.[a-z]+$)", re.I)


def joint_pass(r: dict[str, Any]) -> bool:
    """Primary metric: a trial wins only if it fixed the surface bug AND did it
    correctly. SecPass None (no hidden block) collapses to FuncPass alone."""
    func = bool(r.get("functional_pass"))
    sec = r.get("security_pass")
    return func and (sec is not False)  # None (no hidden) -> func decides; False -> fail


def trial_validity(r: dict[str, Any]) -> "tuple[bool, str]":
    """Classify a trial as valid or invalid-with-reason. Invalid trials are excluded
    from pass-rate denominators but counted and reported per arm (a gameable arm shows
    a high invalid count rather than a fake win). Reasons:
    - 'tamper': agent edited a visible test file
    - 'protected': agent edited a verify-config or governance/hook file
    - 'hook-inert': a hook-bearing profile whose hooks never fired or whose driver
      does not support hooks (the intended intervention did not actually apply)
    """
    changed = (r.get("driver") or {}).get("changed_files") or []
    if any(is_test_file(p) for p in changed):
        return False, "tamper"
    if any(_PROTECTED_RX.search(p) for p in changed):
        return False, "protected"
    # Hook arms only yield data when the hook actually applied (Slice E enforces this
    # at run time; the aggregator also refuses to count an inert hook trial).
    if r.get("hooks_present"):
        if r.get("hooks_supported_by_driver") is False:
            return False, "hook-inert"
        if r.get("hooks_fired") is False:
            return False, "hook-inert"
    return True, ""


def load_results(results_dir: Path) -> list[dict[str, Any]]:
    out = []
    for f in sorted(results_dir.glob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return out


# Result schema the aggregator's telemetry columns expect. Records without this
# version (pre-Phase-0) lack transcript/tokens/cost/hooks/profile_tokens, so they are
# counted as legacy and reported separately rather than blended into telemetry means.
CURRENT_SCHEMA = 2


def aggregate(results: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    agg: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {"runs": 0, "passes": 0, "sec_runs": 0, "sec_passes": 0,
                 "tampered": 0, "durations": [],
                 "legacy_schema": 0, "current_schema": 0,
                 "with_transcript": 0, "with_tokens": 0, "with_cost": 0,
                 "tokens": [], "profile_tokens": [],
                 "hooks_present": 0, "hooks_fired": 0,
                 "valid_runs": 0, "invalid": 0, "joint_passes": 0,
                 "invalid_reasons": defaultdict(int)})
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
        # Validity + the PRIMARY joint metric. Invalid trials are excluded from the
        # joint denominator (valid_runs) but counted and reasoned (decision 2026-06-28:
        # exclude-and-report, not count-as-fail). joint_pass is FuncPass AND SecPass.
        valid, reason = trial_validity(r)
        if valid:
            a["valid_runs"] += 1
            if joint_pass(r):
                a["joint_passes"] += 1
        else:
            a["invalid"] += 1
            a["invalid_reasons"][reason] += 1
        if r.get("duration_sec"):
            a["durations"].append(r["duration_sec"])
        # Schema / telemetry availability — a legacy record is reported, never blended.
        if r.get("schema_version") == CURRENT_SCHEMA:
            a["current_schema"] += 1
        else:
            a["legacy_schema"] += 1
        drv = r.get("driver") or {}
        if drv.get("transcript_path"):
            a["with_transcript"] += 1
        if drv.get("tokens") is not None:
            a["with_tokens"] += 1
            a["tokens"].append(drv["tokens"])
        if drv.get("cost") is not None:
            a["with_cost"] += 1
        if r.get("profile_tokens") is not None:
            a["profile_tokens"].append(r["profile_tokens"])
        if r.get("hooks_present"):
            a["hooks_present"] += 1
        if r.get("hooks_fired"):
            a["hooks_fired"] += 1
    for a in agg.values():
        a["pass_rate"] = round(a["passes"] / a["runs"], 3) if a["runs"] else 0.0
        # PRIMARY: joint pass rate over VALID trials only.
        a["joint_rate"] = round(a["joint_passes"] / a["valid_runs"], 3) if a["valid_runs"] else None
        a["invalid_reasons"] = dict(a["invalid_reasons"])
        a["sec_rate"] = round(a["sec_passes"] / a["sec_runs"], 3) if a["sec_runs"] else None
        a["avg_sec"] = round(sum(a["durations"]) / len(a["durations"]), 1) if a["durations"] else 0.0
        a["avg_tokens"] = round(sum(a["tokens"]) / len(a["tokens"]), 1) if a["tokens"] else None
        a["avg_profile_tokens"] = (round(sum(a["profile_tokens"]) / len(a["profile_tokens"]), 1)
                                   if a["profile_tokens"] else None)
        a["mixed_schema"] = a["legacy_schema"] > 0 and a["current_schema"] > 0
    return agg


def format_table(agg: dict[tuple[str, str], dict[str, Any]]) -> str:
    # PRIMARY metric is joint (FuncPass AND SecPass) over valid trials; func/sec shown
    # alongside for diagnosis. `inval` is the per-arm invalid count (excluded from joint).
    lines = [f"{'fixture':34} {'profile':18} {'JOINT':>9} {'jrate':>6} {'func':>7} {'sec':>7} "
             f"{'inval':>6} {'hookF':>7} {'gtok':>6} {'schema':>8}"]
    for (fid, profile), a in sorted(agg.items()):
        flags = []
        if a["tampered"]:
            flags.append("TAMPER")
        if a["mixed_schema"]:
            flags.append("MIXED-SCHEMA")
        if a["invalid"]:
            flags.append(f"INVALID:{a['invalid_reasons']}")
        flag = ("  " + " ".join(flags)) if flags else ""
        joint = f"{a['joint_passes']}/{a['valid_runs']}" if a["valid_runs"] else "-"
        jrate = a["joint_rate"] if a["joint_rate"] is not None else "-"
        sec = f"{a['sec_passes']}/{a['sec_runs']}" if a["sec_runs"] else "-"
        hookf = f"{a['hooks_fired']}/{a['hooks_present']}" if a["hooks_present"] else "-"
        gtok = a["avg_profile_tokens"] if a["avg_profile_tokens"] is not None else "-"
        schema = (f"{a['current_schema']}c/{a['legacy_schema']}L"
                  if a["legacy_schema"] else f"{a['current_schema']}c")
        lines.append(f"{fid:34} {profile:18} {joint:>9} {str(jrate):>6} "
                     f"{a['passes']:>3}/{a['runs']:<3} {sec:>7} {a['invalid']:>6} "
                     f"{hookf:>7} {str(gtok):>6} {schema:>8}{flag}")
    # Per-fixture delta vs the 'none' baseline, on the PRIMARY joint rate.
    by_fix: dict[str, dict[str, float]] = defaultdict(dict)
    for (fid, profile), a in agg.items():
        if a["joint_rate"] is not None:
            by_fix[fid][profile] = a["joint_rate"]
    lines.append("")
    lines.append("delta vs none (JOINT rate = FuncPass AND SecPass, valid trials only):")
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
