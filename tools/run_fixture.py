#!/usr/bin/env python3
"""Language-agnostic eval fixture runner.

A *fixture* declares its own setup + verify commands (see evals/fixtures/*/fixture.json),
so this harness never assumes a language or test framework: it scaffolds an isolated
workspace, optionally overlays a governance profile, runs the fixture's own commands,
and scores the trial on the verify command's exit status.

This file is the Slice-1 instrument. It deliberately does NOT drive an agent (that is
the separate, optional driver layer); it scaffolds + scores, so the scoring is
deterministic and unit-testable on its own.

Safety: a real (source-repo) fixture is scaffolded into a throwaway temp clone with its
git remotes stripped, so neither this harness nor any later agent can push to or mutate
the owner's working repo. Trial results record scores + the source commit, never repo
contents.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = REPO_ROOT / "evals" / "governance_profiles"
RESULTS_DIR = REPO_ROOT / "evals" / "results"


def load_manifest(fixture_dir: Path) -> dict[str, Any]:
    manifest_path = fixture_dir / "fixture.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if "verify" not in data or not str(data["verify"]).strip():
        raise ValueError(f"{manifest_path}: 'verify' command is required")
    return data


def run_command(
    cmd: str, cwd: Path, env_extra: dict[str, str] | None = None, timeout: int = 1800
) -> tuple[int, str, str]:
    """Run a declared shell command. Returns (exit_code, stdout, stderr).

    exit_code 127 on timeout/launch failure (treated as a non-pass by callers).
    """
    import os

    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), env=env, shell=True,
            capture_output=True, text=True, timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", f"TIMEOUT after {timeout}s"


def scaffold(manifest: dict[str, Any], fixture_dir: Path, workdir: Path) -> str | None:
    """Materialize the fixture into workdir. Returns the resolved source commit, if any.

    source=None  -> empty workdir; copy fixture's inline `files/` payload if present.
    source=repo  -> local git clone at a pinned commit with remotes stripped.
    """
    source = manifest.get("source")
    if not source:
        files_sub = manifest.get("files")
        if files_sub:
            src = (fixture_dir / files_sub).resolve()
            for item in src.iterdir():
                dest = workdir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        return None

    repo_path = Path(source["repo_path"]).expanduser()
    base_commit = str(source["base_commit"])
    if not (repo_path / ".git").exists():
        raise FileNotFoundError(f"source repo not found or not a git repo: {repo_path}")
    # Local clone is cheap (hardlinks) and isolates us from the owner's working tree.
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(repo_path), str(workdir)],
                   check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(workdir), "checkout", "--quiet", base_commit],
                   check=True, capture_output=True, text=True)
    # Strip every remote so nothing in the trial can push back.
    remotes = subprocess.run(["git", "-C", str(workdir), "remote"],
                             capture_output=True, text=True).stdout.split()
    for r in remotes:
        subprocess.run(["git", "-C", str(workdir), "remote", "remove", r],
                       capture_output=True, text=True)
    return subprocess.run(["git", "-C", str(workdir), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def patch_from_commit(repo_path: Path, commit: str, paths: list[str]) -> str:
    """Derive a unified diff for `paths` introduced by `commit`, read live from the
    source repo. Gold fixtures store only the commit SHA + paths (metadata), never the
    diff text, so no source-repo code is vendored into this repo."""
    out = subprocess.run(
        ["git", "-C", str(repo_path), "show", commit, "--", *paths],
        check=True, capture_output=True, text=True,
    ).stdout
    if not out.strip():
        raise ValueError(f"empty patch from {commit} for paths {paths}")
    return out


def apply_patch_text(workdir: Path, patch_text: str) -> None:
    """Apply a derived diff into the scaffolded workdir.

    Gold fixtures inject the fix-commit's failing test onto the parent state; the
    solution diff is applied only by the oracle self-check."""
    subprocess.run(
        ["git", "-C", str(workdir), "apply", "--whitespace=nowarn"],
        input=patch_text, check=True, capture_output=True, text=True,
    )


def overlay_profile(profile: str, workdir: Path) -> list[str]:
    """Overlay a governance profile onto the workdir. Returns the list of files overlaid.

    'none' is a no-op. Other profiles copy their tree over the workdir. Harness-neutral
    files live at the profile root; harness adapters live under per-harness subdirs and
    are installed by a driver, not here.
    """
    if profile in ("", "none"):
        return []
    profile_dir = PROFILES_DIR / profile
    if not profile_dir.is_dir():
        raise FileNotFoundError(f"unknown governance profile: {profile} ({profile_dir})")
    overlaid: list[str] = []
    for item in sorted(profile_dir.rglob("*")):
        if item.is_file():
            rel = item.relative_to(profile_dir)
            dest = workdir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
            overlaid.append(str(rel))
    return overlaid


def score_fixture(
    fixture_dir: Path, profile: str = "none", workdir: Path | None = None,
    run_id: str = "manual", apply_solution: bool = False,
) -> dict[str, Any]:
    fixture_dir = fixture_dir.resolve()
    manifest = load_manifest(fixture_dir)
    cleanup = False
    if workdir is None:
        workdir = Path(tempfile.mkdtemp(prefix=f"evalfx-{manifest['id']}-"))
        cleanup = True

    started = time.monotonic()
    result: dict[str, Any] = {
        "run_id": run_id,
        "id": manifest["id"],
        "language": manifest.get("language", "unknown"),
        "profile": profile,
        "source_commit": None,
        "setup_ok": True,
        "verify_exit": None,
        "functional_pass": False,
        "duration_sec": None,
        "workdir": str(workdir),
    }
    try:
        result["source_commit"] = scaffold(manifest, fixture_dir, workdir)
        # Gold-standard fixtures inject the fix-commit's failing test onto the parent
        # state; the solution diff is applied only by the oracle self-check. Both diffs
        # are derived live from the source repo by commit SHA + paths.
        source = manifest.get("source") or {}
        if manifest.get("test_paths"):
            repo_path = Path(source["repo_path"]).expanduser()
            apply_patch_text(workdir, patch_from_commit(
                repo_path, source["fix_commit"], manifest["test_paths"]))
            if apply_solution and manifest.get("solution_paths"):
                apply_patch_text(workdir, patch_from_commit(
                    repo_path, source["fix_commit"], manifest["solution_paths"]))
        result["profile_files"] = overlay_profile(profile, workdir)
        env_extra = manifest.get("env") or {}

        for step in manifest.get("setup", []):
            exit_code, _out, err = run_command(step, workdir, env_extra)
            if exit_code != 0:
                result["setup_ok"] = False
                result["setup_failed_command"] = step
                result["setup_error_tail"] = err[-500:]
                result["duration_sec"] = round(time.monotonic() - started, 2)
                return result

        exit_code, _out, _err = run_command(manifest["verify"], workdir, env_extra)
        result["verify_exit"] = exit_code
        result["functional_pass"] = (exit_code == 0)
        result["duration_sec"] = round(time.monotonic() - started, 2)
        return result
    finally:
        if cleanup:
            shutil.rmtree(workdir, ignore_errors=True)


def check_oracle(fixture_dir: Path) -> dict[str, Any]:
    """Validate a gold-standard fixture: the verify command must FAIL on the parent
    state with the test patch applied, and PASS once the solution patch is also
    applied. A fixture that does not satisfy both has no usable oracle."""
    fixture_dir = fixture_dir.resolve()
    manifest = load_manifest(fixture_dir)
    source = manifest.get("source") or {}
    if not (manifest.get("test_paths") and manifest.get("solution_paths") and source.get("fix_commit")):
        raise ValueError("oracle check requires source.fix_commit, test_paths, and solution_paths")
    broken = score_fixture(fixture_dir)
    fixed = score_fixture(fixture_dir, apply_solution=True)
    # A real oracle requires the VERIFY command itself to discriminate: it must run
    # (setup ok, not skipped) and FAIL on the parent+test state, then run and PASS once
    # the solution is applied. A setup failure is NOT a valid oracle failure — otherwise
    # a fixture whose `setup` happens to fail on the broken state would masquerade as a
    # passing oracle even though `verify` never demonstrated the bug. (RF-001)
    broken_ran = broken["setup_ok"] and broken["verify_exit"] is not None
    fixed_ran = fixed["setup_ok"] and fixed["verify_exit"] is not None
    broken_fails = broken_ran and broken["verify_exit"] != 0
    fixed_passes = fixed_ran and fixed["verify_exit"] == 0
    return {
        "id": manifest["id"],
        "broken_fails": broken_fails,
        "fixed_passes": fixed_passes,
        "broken_setup_ok": broken["setup_ok"],
        "fixed_setup_ok": fixed["setup_ok"],
        "oracle_valid": broken_fails and fixed_passes,
        "broken_verify_exit": broken["verify_exit"],
        "fixed_verify_exit": fixed["verify_exit"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run and score an eval fixture.")
    parser.add_argument("fixture", help="path to a fixture directory (contains fixture.json)")
    parser.add_argument("--profile", default="none", help="governance profile to overlay")
    parser.add_argument("--run-id", default="manual", help="label recorded in the result")
    parser.add_argument("--record", action="store_true", help="write the result JSON under evals/results/")
    parser.add_argument("--check-oracle", action="store_true",
                        help="validate a gold fixture (broken fails, fixed passes) instead of scoring")
    args = parser.parse_args(argv)

    if args.check_oracle:
        oracle = check_oracle(Path(args.fixture))
        print(json.dumps(oracle, indent=2))
        return 0 if oracle["oracle_valid"] else 1

    result = score_fixture(Path(args.fixture), profile=args.profile, run_id=args.run_id)
    print(json.dumps(result, indent=2))
    if args.record:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out = RESULTS_DIR / f"{result['id']}-{result['profile']}-{args.run_id}.json"
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"recorded: {out.relative_to(REPO_ROOT)}", file=sys.stderr)
    return 0 if result["functional_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
