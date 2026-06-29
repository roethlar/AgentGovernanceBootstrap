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
import hashlib
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


TRANSCRIPTS_DIR = RESULTS_DIR / "transcripts"

# Env var a hook reads to find the external firing sentinel. The sentinel lives
# OUTSIDE the trial worktree, so a hook writing it never reappears in the agent's
# changed_files (which would re-create the S1 contamination this harness fixes).
HOOK_SENTINEL_ENV = "AGB_HOOK_SENTINEL"

# Driver bases whose harness honors the hooks we overlay (.claude/ hooks). Claude
# Code and ollama-via-Claude-Code do; codex/grok have their own hook systems that do
# not read .claude/, so an overlaid Claude hook is inert there.
_HOOK_SUPPORTING_DRIVER_BASES = {"claude", "ollama"}


def _hooks_present(profile_files: list[str]) -> bool:
    """True if the overlaid profile installed a Claude-style hook (settings.json that
    can declare hooks, or a hook script). Structural, no runtime needed."""
    for rel in profile_files:
        p = rel.replace("\\", "/")
        if p.endswith(".claude/settings.json") or p == ".claude/settings.json":
            return True
        if "/hooks/" in p or p.startswith("hooks/") or p.endswith("-hook.sh"):
            return True
    return False


def _hooks_supported_by_driver(driver_name: "str | None") -> "bool | None":
    """Whether the driver's harness honors an overlaid .claude/ hook. None when no
    driver ran (can't attribute support to a harness that wasn't exercised)."""
    if not driver_name:
        return None
    return driver_name.split(":", 1)[0] in _HOOK_SUPPORTING_DRIVER_BASES


def _store_transcript_and_redact(driver_result: dict[str, Any], fixture_id: str,
                                 profile: str, run_id: str) -> None:
    """Write the driver's raw stdout/stderr to a gitignored transcript file and remove
    the raw keys from the result dict in place. Records `transcript_path` (relative to
    the repo root) and `transcript_bytes`. If the driver supplied no raw streams, both
    are None. This is the redaction step that makes the gitignored-transcript design
    actually protect tracked results JSON (see the Phase 0 plan, R2-#1)."""
    raw_out = driver_result.pop("_stdout", None)
    raw_err = driver_result.pop("_stderr", None)
    if raw_out is None and raw_err is None:
        driver_result.setdefault("transcript_path", None)
        driver_result.setdefault("transcript_bytes", None)
        return
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    # Sanitize the filename components (profile/run_id are caller-controlled labels).
    safe = lambda s: "".join(c if (c.isalnum() or c in "-_.") else "_" for c in str(s))
    fname = f"{safe(fixture_id)}-{safe(profile)}-{safe(run_id)}.txt"
    path = TRANSCRIPTS_DIR / fname
    body = ((raw_out or "") + ("\n--- STDERR ---\n" + raw_err if raw_err else ""))
    path.write_text(body, encoding="utf-8")
    driver_result["transcript_path"] = str(path.relative_to(REPO_ROOT))
    driver_result["transcript_bytes"] = len(body.encode("utf-8"))


def _sha(parts: list[str]) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8", errors="replace"))
        h.update(b"\0")
    return h.hexdigest()[:16]


def fixture_hash(fixture_dir: Path, manifest: dict[str, Any]) -> str:
    """Stable identity of the fixture inputs (manifest + task), so trial results are
    comparable across reruns and detect a fixture that changed under them."""
    task = manifest.get("task", "TASK.md")
    task_text = ""
    if (fixture_dir / task).exists():
        task_text = (fixture_dir / task).read_text(encoding="utf-8", errors="replace")
    return _sha([json.dumps(manifest, sort_keys=True), task_text])


def estimate_profile_tokens(workdir: Path, overlaid: list[str]) -> int:
    """Estimate the governance token weight injected by a profile, summed over the
    overlaid files' contents. This is a transparent, dependency-free heuristic
    (~4 chars/token, the common English rule of thumb), NOT a real tokenizer — it is
    used for cross-profile PROPORTIONALITY comparison (e.g. did a heavier governance
    profile collapse a weak model's FuncPass?), where a consistent estimate suffices.
    Billed token cost, where a harness reports it, comes from the driver telemetry."""
    chars = 0
    for rel in sorted(overlaid):
        f = workdir / rel
        if f.exists():
            chars += len(f.read_text(encoding="utf-8", errors="replace"))
    # ceil(chars / 4)
    return (chars + 3) // 4


def overlaid_hash(workdir: Path, overlaid: list[str]) -> str:
    """Hash the governance actually injected (the overlaid files' contents), so two
    trials under 'the same profile' are provably the same governance."""
    parts: list[str] = []
    for rel in sorted(overlaid):
        f = workdir / rel
        parts.append(rel)
        parts.append(f.read_text(encoding="utf-8", errors="replace") if f.exists() else "")
    return _sha(parts)


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

    source=None       -> empty workdir; copy fixture's inline `files/` payload if present.
    source.copy_dir   -> copy a local directory (e.g. a benchmark exercise), excluding
                         named entries (the reference solution); no source commit.
    source.repo_path  -> local git clone at a pinned commit with remotes stripped.
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

    if source.get("copy_dir"):
        src_dir = Path(source["copy_dir"]).expanduser().resolve()
        if not src_dir.is_dir():
            raise FileNotFoundError(f"source.copy_dir is not a directory: {src_dir}")
        excludes = set(source.get("exclude", []))
        for item in sorted(src_dir.iterdir()):
            if item.name in excludes:
                continue
            dest = workdir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*excludes) if excludes else None)
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


def isolate_history(workdir: Path) -> None:
    """Replace the scaffolded clone's history with a single trial-base commit.

    A gold fixture is cloned from the source repo, whose history still contains the
    fix-commit — a driven agent could `git show` it and copy the answer. Re-initializing
    at the post-scaffold (parent + injected test) state removes all ancestry, so the
    agent starts from a clean checkpoint with nothing to crib, and the agent's edits are
    diffable against `trial-base`. Also used for synthetic fixtures (no prior .git) so
    their trials are tamper-evident too."""
    if (workdir / ".git").exists():
        shutil.rmtree(workdir / ".git")
    subprocess.run(["git", "-C", str(workdir), "init", "--quiet"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(workdir), "add", "-A"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(workdir), "-c", "user.email=eval@local", "-c", "user.name=eval",
                    "commit", "--quiet", "-m", "trial-base"], check=True, capture_output=True, text=True)


# Deletion-safe governance subset. This is intentionally NARROWER than
# tools/discover.py's GOVERNANCE_MARKER_PATTERNS (which is a *detection* list and
# includes generic doc names — state.md, decisions.md, devlog.md, review.md,
# docs/agent/* — that a product repo may legitimately ship as its own
# documentation). We only auto-delete the unambiguous agent-instruction artifacts:
# a `none`-profile trial must begin from a repo with no governance steering the
# agent, but we must never corrupt a fixture by deleting its product/docs. Detection
# is deliberately a superset of deletion. Each entry below is a session-governance
# file/dir, not product. Patterns are matched against workdir-relative POSIX paths;
# `*` is a single-segment glob, a trailing `/*` matches anything under that dir.
_GOVERNANCE_STRIP_PATTERNS = [
    "AGENTS.md", "agents.md",
    "CLAUDE.md", "claude.md",
    "GEMINI.md", "gemini.md",
    ".cursorrules",
    ".cursor/rules/*",
    ".aider*",
    ".claude/*",
    ".antigravitycli/*",
    ".github/copilot-instructions.md",  # Copilot's AGENTS.md equivalent (not in discover's list)
]


def _match_governance(rel: str, patterns: list[str]) -> bool:
    """True if a workdir-relative POSIX path is matched by a strip pattern. A trailing
    `/*` pattern matches the whole subtree (any depth) under that directory."""
    from fnmatch import fnmatch
    for pat in patterns:
        if pat.endswith("/*"):
            base = pat[:-2]
            if rel == base or rel.startswith(base + "/"):
                return True
        elif fnmatch(rel, pat):
            return True
    return False


def strip_pre_existing_governance(workdir: Path, manifest: dict[str, Any]) -> list[str]:
    """Remove pre-existing agent-governance files the source repo carried, so a
    `none`-profile trial starts clean regardless of what the fixture repo shipped.
    Returns the sorted relpaths removed.

    Runs after scaffold and BEFORE any test/solution patch, so an injected fixture
    file can never be a strip target. The strip set is the deletion-safe subset above;
    a fixture may add paths via manifest['strip_governance'] (exact relpaths) or
    protect paths via manifest['keep_governance'] (exact relpaths) when a
    governance-named file is genuinely the fixture's subject. If a fixture's declared
    test/solution paths intersect the strip set without an explicit keep, that is a
    fixture-construction error and we fail loudly."""
    keep = set(manifest.get("keep_governance") or [])
    extra = list(manifest.get("strip_governance") or [])
    patterns = _GOVERNANCE_STRIP_PATTERNS + extra

    # Guard: a fixture's own test/solution files must never be governance-stripped.
    source = manifest.get("source") or {}
    declared = set(manifest.get("test_paths") or []) | set(manifest.get("solution_paths") or [])
    for d in sorted(declared):
        if _match_governance(d, patterns) and d not in keep:
            raise ValueError(
                f"fixture {manifest.get('id')!r}: declared path {d!r} matches the "
                f"governance strip set; add it to keep_governance if intended")

    removed: list[str] = []
    root = workdir.resolve()
    for path in sorted(workdir.rglob("*")):
        if not (path.is_file() or path.is_symlink()):
            continue
        try:
            rel = path.resolve().relative_to(root).as_posix()
        except ValueError:
            rel = path.relative_to(workdir).as_posix()
        if rel.startswith(".git/"):
            continue
        if rel in keep:
            continue
        if _match_governance(rel, patterns):
            path.unlink()
            removed.append(rel)
    return sorted(removed)


def overlay_profile(profile: str, workdir: Path,
                    allow_overwrite: "set[str] | None" = None) -> list[str]:
    """Overlay a governance profile onto the workdir. Returns the relpaths overlaid.

    'none' is a no-op. A profile may carry literal files (overlaid as-is) and/or a
    `profile.json` with a `copies` list mapping product files into the workspace, e.g.
    {"copies": [{"from": "templates/AGENTS.template.md", "to": "AGENTS.md"}]}. The copy
    form keeps a single source of truth — `current-template` is generated from the
    shipped templates rather than duplicating them. `profile.json` and README files are
    metadata, not overlaid.

    Collision guard: because the overlay is committed into trial-base (so the agent's
    diff is measured against it), a profile that silently overwrote an existing
    product or test file would hide that mutation from `changed_files`. A destination
    that already exists in the workdir therefore raises ValueError (fail-closed) unless
    its relpath is in `allow_overwrite` — the set of paths the governance strip removed,
    which a profile is legitimately allowed to re-supply.
    """
    allow_overwrite = allow_overwrite or set()
    if profile in ("", "none"):
        return []
    profiles_root = PROFILES_DIR.resolve()
    profile_dir = (PROFILES_DIR / profile).resolve()
    if profiles_root not in profile_dir.parents:
        raise ValueError(f"profile name escapes the profiles dir: {profile!r}")
    if not profile_dir.is_dir():
        raise FileNotFoundError(f"unknown governance profile: {profile} ({profile_dir})")

    # Preflight: reject any symlink anywhere in the profile tree (including a symlinked
    # profile.json) BEFORE reading or copying anything, so a rejected profile has no
    # side effects.
    for item in profile_dir.rglob("*"):
        if item.is_symlink():
            raise ValueError(f"profile contains a symlink (not allowed): {item.relative_to(profile_dir)}")

    workdir_root = workdir.resolve()

    def _safe_dest(rel_to: str) -> Path:
        dest = (workdir / rel_to).resolve()
        if dest != workdir_root and workdir_root not in dest.parents:
            raise ValueError(f"profile destination escapes the workspace: {rel_to!r}")
        # Collision guard: overlaying onto an existing file would, once committed into
        # trial-base, mask that file's mutation from the agent's changed_files. Allow
        # only paths the strip removed (which the profile may re-supply).
        norm = Path(rel_to).as_posix()
        if dest.exists() and norm not in allow_overwrite:
            raise ValueError(
                f"profile would overwrite an existing workspace file not removed by the "
                f"governance strip: {rel_to!r} (add it to manifest keep/strip overrides "
                f"if this is intended)")
        return dest

    repo_root = REPO_ROOT.resolve()

    def _part_src(part: str) -> Path:
        # "repo:<path>" resolves under the repo; "profile:<path>" under the profile dir.
        kind, _, rel = part.partition(":")
        if kind == "repo":
            src = (REPO_ROOT / rel).resolve()
            if repo_root not in src.parents:
                raise ValueError(f"concat repo part escapes the repo: {part!r}")
        elif kind == "profile":
            src = (profile_dir / rel).resolve()
            if profile_dir not in src.parents:
                raise ValueError(f"concat profile part escapes the profile: {part!r}")
        else:
            raise ValueError(f"concat part must be 'repo:<path>' or 'profile:<path>': {part!r}")
        return src

    overlaid: list[str] = []
    spec_path = profile_dir / "profile.json"
    if spec_path.exists():
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        for copy in spec.get("copies", []):
            src = (REPO_ROOT / copy["from"]).resolve()
            if repo_root not in src.parents:
                raise ValueError(f"profile copy source escapes the repo: {copy['from']!r}")
            dest = _safe_dest(copy["to"])
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            overlaid.append(copy["to"])
        # concat composes a destination from ordered parts — e.g. the product AGENTS
        # template plus a candidate snippet — so a candidate profile adds governance
        # without committing a duplicated copy of the template.
        for cat in spec.get("concat", []):
            chunks = [_part_src(p).read_text(encoding="utf-8") for p in cat["parts"]]
            dest = _safe_dest(cat["to"])
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("\n".join(chunks), encoding="utf-8")
            overlaid.append(cat["to"])
    for item in sorted(profile_dir.rglob("*")):
        rel = item.relative_to(profile_dir)
        # `_parts/` holds concat fragments, not standalone overlays; skip them.
        if item.is_file() and item.name != "profile.json" and not item.name.startswith("README") \
                and "_parts" not in rel.parts:
            dest = _safe_dest(str(rel))
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
            overlaid.append(str(rel))
    return overlaid


def score_fixture(
    fixture_dir: Path, profile: str = "none", workdir: Path | None = None,
    run_id: str = "manual", apply_solution: bool = False,
    driver: "Callable[..., dict[str, Any]] | None" = None,
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
        # Strip any pre-existing agent governance the source repo carried, BEFORE
        # applying fixture patches (so an injected test/solution file is never a strip
        # target) — a `none`-profile trial must start from a repo with no governance
        # steering the agent, independent of what the fixture repo shipped.
        result["stripped_governance_files"] = strip_pre_existing_governance(workdir, manifest)
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
        # Overlay governance BEFORE isolating history, so the profile lands in the
        # trial-base commit rather than as untracked files the driver's
        # `git status` would later misattribute to the agent (the changed_files
        # artifact). Governance is environment, not agent work. A profile may re-supply
        # a path the strip just removed (allow_overwrite), but not clobber a surviving
        # product/test file (collision guard).
        result["profile_files"] = overlay_profile(
            profile, workdir, allow_overwrite=set(result["stripped_governance_files"]))
        result["profile_hash"] = overlaid_hash(workdir, result["profile_files"])
        result["profile_tokens"] = estimate_profile_tokens(workdir, result["profile_files"])
        result["hooks_present"] = _hooks_present(result["profile_files"])
        if source or manifest.get("files"):
            isolate_history(workdir)
        result["fixture_hash"] = fixture_hash(fixture_dir, manifest)
        env_extra = dict(manifest.get("env") or {})

        # Hook-firing sentinel (S4): an external file, OUTSIDE the trial worktree, that
        # an overlaid hook can append to when it fires. Kept external so writing it can
        # never reappear in the agent's changed_files (the S1 contamination class). The
        # path is exposed to the hook (and the agent's harness) via env.
        sentinel = Path(tempfile.mkdtemp(prefix="evalhook-")) / "fired.log"
        env_extra[HOOK_SENTINEL_ENV] = str(sentinel)

        for step in manifest.get("setup", []):
            exit_code, _out, err = run_command(step, workdir, env_extra)
            if exit_code != 0:
                result["setup_ok"] = False
                result["setup_failed_command"] = step
                result["setup_error_tail"] = err[-500:]
                result["duration_sec"] = round(time.monotonic() - started, 2)
                return result

        # Drive an agent (optional). It edits the workspace in place; the verify command
        # below then scores the outcome. The driver runs after setup so the agent can run
        # the project's own tests while working.
        if driver is not None:
            driver_result = driver(workdir, fixture_dir, manifest, env_extra)
            # Transcript storage + raw-stream redaction (S3): the driver returns raw
            # stdout/stderr under _stdout/_stderr; score_fixture (which knows
            # id/profile/run_id) writes them to a GITIGNORED transcript file and then
            # strips the raw keys, so raw agent output — possibly carrying workspace
            # source, prompts, or secrets — never lands in a tracked results JSON.
            _store_transcript_and_redact(driver_result, result["id"], profile, run_id)
            result["driver"] = driver_result
            result["hooks_supported_by_driver"] = _hooks_supported_by_driver(
                driver_result.get("driver"))
        else:
            result["hooks_supported_by_driver"] = None
        # hooks_fired: did the external sentinel get written? None when no hook could
        # have fired (none present) — absence of a present hook is not "didn't fire".
        if result["hooks_present"]:
            result["hooks_fired"] = sentinel.exists() and sentinel.stat().st_size > 0
        else:
            result["hooks_fired"] = None
        shutil.rmtree(sentinel.parent, ignore_errors=True)

        exit_code, _out, _err = run_command(manifest["verify"], workdir, env_extra)
        result["verify_exit"] = exit_code
        result["functional_pass"] = (exit_code == 0)

        # A `hidden` block is the security/property test the agent NEVER sees: it lives
        # outside the workspace during the agent's work and is injected only now, for
        # scoring. This separates FuncPass (the visible test the agent makes pass) from
        # SecPass (the hidden invariant) — the dimension where a strong agent has margin.
        hidden = manifest.get("hidden")
        if hidden:
            hsrc = (fixture_dir / hidden["files"]).resolve()
            for item in sorted(hsrc.iterdir()):
                dest = workdir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            h_exit, _o, _e = run_command(hidden["verify"], workdir, env_extra)
            result["hidden_exit"] = h_exit
            result["security_pass"] = (h_exit == 0)
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
    parser.add_argument("--driver", default=None,
                        help="drive an agent to attempt the fixture (e.g. 'codex'); omit to score as-is")
    args = parser.parse_args(argv)

    if args.check_oracle:
        oracle = check_oracle(Path(args.fixture))
        print(json.dumps(oracle, indent=2))
        return 0 if oracle["oracle_valid"] else 1

    driver = None
    if args.driver:
        import drivers
        driver = drivers.get_driver(args.driver)
    result = score_fixture(Path(args.fixture), profile=args.profile, run_id=args.run_id, driver=driver)
    print(json.dumps(result, indent=2))
    if args.record:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out = RESULTS_DIR / f"{result['id']}-{result['profile']}-{args.run_id}.json"
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"recorded: {out.relative_to(REPO_ROOT)}", file=sys.stderr)
    return 0 if result["functional_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
