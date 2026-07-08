#!/usr/bin/env python3
"""Reconcile a governed repo to the toolkit's shipped artifact set.

Pull-based, per-repo, no registry: run it while standing in (or pointing it
at) a governed repo. It syncs the local toolkit clone from its canonical
remote, then reconciles the target repo to tools/shipped-set.json:

  - replace-whole   (AGENTS.md): replaced only when the existing file matches
                    the current or a formerly-shipped template version
                    (newline-normalized). Anything else is flagged, never
                    overwritten - a content-bearing foreign AGENTS.md is a
                    migration, not a refresh.
  - replace-if-unmodified: missing -> install; matches a formerly-shipped
                    version -> update to current; anything else ->
                    owner-modified: flagged, never overwritten.
  - retired:        formerly-shipped paths are removed only when they match a
                    formerly-shipped version; otherwise flagged. A modified
                    file is never deleted by machine.

Repo-owned files (.agents/state.md, decisions.md, repo-guidance.md,
push-policy.md, plans, review trails, archives) are never touched.

Committability follows the recorded custody rules: git check-ignore per
target path; a blanket harness-adapter-dir ignore (.claude/ etc.) gets the
established narrow repair with the .gitignore edit included in the same
commit; a path ignored by an unrecognized rule is flagged and skipped;
git add -f is never used.

Default mode stages the reconciled paths and makes one scoped commit whose
message records the toolkit commit it synced to. --stage-only stages and
stops (the bootstrap procedure then stages the approved judgment drafts and
makes the single scoped commit covering both groups). Neither mode pushes.

Python 3.9+, stdlib only.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CANONICAL_URLS = [
    # Order: LAN mirror first (faster when reachable), GitHub is canon.
    # ls-remote against GitHub decides the target head; the mirror only
    # serves bytes. Offline -> proceed on the local copy with a flag.
    "http://q:3000/michael/AgentGovernanceBootstrap.git",
    "https://github.com/roethlar/AgentGovernanceBootstrap.git",
]

ADAPTER_DIRS = (".claude", ".codex", ".gemini", ".grok")


def norm(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def nhash(data: bytes) -> str:
    return hashlib.sha256(norm(data)).hexdigest()


def git(repo: Path, *args: str, check: bool = True) -> "subprocess.CompletedProcess[str]":
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            "git {} failed in {}: {}".format(" ".join(args), repo, proc.stderr.strip())
        )
    return proc


def is_git_repo(path: Path) -> bool:
    return git(path, "rev-parse", "--is-inside-work-tree", check=False).returncode == 0


def sync_toolkit(toolkit: Path) -> str:
    """Fast-forward the toolkit clone from a canonical remote. Never blocks:
    offline or diverged -> proceed on the local copy, returning a flag note."""
    for url in CANONICAL_URLS:
        live = git(toolkit, "ls-remote", "--exit-code", url, "HEAD", check=False)
        if live.returncode != 0:
            continue
        fetched = git(toolkit, "fetch", url, check=False)
        if fetched.returncode != 0:
            continue
        ff = git(toolkit, "merge", "--ff-only", "FETCH_HEAD", check=False)
        if ff.returncode != 0:
            return "toolkit clone has local work not on {} (no fast-forward); proceeding on the local copy".format(url)
        return ""
    return "no canonical remote reachable; proceeding on the local toolkit copy (may be stale)"


def load_shipped_set(toolkit: Path) -> dict:
    return json.loads((toolkit / "tools" / "shipped-set.json").read_text(encoding="utf-8"))


class Plan:
    def __init__(self) -> None:
        self.install = []   # (target, source_path)
        self.update = []    # (target, source_path)
        self.remove = []    # target
        self.current = []   # target
        self.flags = []     # (target, reason)
        self.gitignore_repairs = []  # (line_no, old_line, new_lines)


def classify(target_repo: Path, toolkit: Path, shipped: dict) -> Plan:
    plan = Plan()
    for art in shipped["artifacts"]:
        src = toolkit / art["source"]
        src_bytes = src.read_bytes()
        src_hash = nhash(src_bytes)
        tgt = target_repo / art["target"]
        if not tgt.exists():
            plan.install.append((art["target"], src))
            continue
        tgt_hash = nhash(tgt.read_bytes())
        if tgt_hash == src_hash:
            plan.current.append(art["target"])
        elif tgt_hash in art.get("formerly", []):
            plan.update.append((art["target"], src))
        elif art["class"] == "replace-whole":
            plan.flags.append((
                art["target"],
                "does not match any known template version - hand-edited or a foreign "
                "governance file; refusing to replace. If this repo has never been "
                "bootstrapped by the toolkit, run the bootstrap procedure instead.",
            ))
        else:
            plan.flags.append((art["target"], "owner-modified; left untouched"))
    for ret in shipped.get("retired", []):
        tgt = target_repo / ret["target"]
        if not tgt.exists():
            continue
        if nhash(tgt.read_bytes()) in ret.get("formerly", []):
            plan.remove.append(ret["target"])
        else:
            plan.flags.append((ret["target"], "retired artifact, but modified locally; remove by hand if intended"))
    return plan


def check_committability(target_repo: Path, plan: Plan, shipped: dict) -> None:
    """check-ignore each path we would add; repair known blanket adapter-dir
    ignores in the repo's root .gitignore; flag-and-skip anything else."""
    paths = [t for t, _ in plan.install + plan.update]
    exclusions = shipped.get("machine_local_exclusions", {})
    gitignore = target_repo / ".gitignore"
    for path in list(paths):
        probe = git(target_repo, "check-ignore", "--verbose", "--", path, check=False)
        if probe.returncode != 0:
            continue  # not ignored
        # format: <source>:<linenum>:<pattern>\t<path>
        head = probe.stdout.strip().split("\t")[0]
        source, lineno, pattern = head.rsplit(":", 2)
        pat = pattern.strip().strip("/")
        if source == ".gitignore" and pat in ADAPTER_DIRS:
            repl = exclusions.get(pat, [])
            plan.gitignore_repairs.append((int(lineno), pattern, repl))
        else:
            for lst in (plan.install, plan.update):
                lst[:] = [(t, s) for t, s in lst if t != path]
            plan.flags.append((path, "ignored by '{}' ({}:{}) - unrecognized rule; skipped, never force-added".format(pattern, source, lineno)))
    # dedupe repairs (several paths may hit the same blanket line)
    plan.gitignore_repairs = sorted(set(
        (ln, old, tuple(new)) for ln, old, new in plan.gitignore_repairs
    ))


def touched_paths(plan: Plan) -> list:
    paths = [t for t, _ in plan.install + plan.update] + list(plan.remove)
    if plan.gitignore_repairs:
        paths.append(".gitignore")
    return paths


def dirty_conflicts(target_repo: Path, plan: Plan) -> list:
    paths = touched_paths(plan)
    if not paths:
        return []
    out = git(target_repo, "status", "--porcelain", "--", *paths).stdout
    return [line for line in out.splitlines() if line.strip()]


def apply_plan(target_repo: Path, plan: Plan) -> None:
    for target, src in plan.install + plan.update:
        dest = target_repo / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read_bytes())
    for target in plan.remove:
        (target_repo / target).unlink()
    if plan.gitignore_repairs:
        gitignore = target_repo / ".gitignore"
        lines = gitignore.read_text(encoding="utf-8").splitlines()
        # apply bottom-up so line numbers stay valid
        for lineno, _old, repl in sorted(plan.gitignore_repairs, reverse=True):
            lines[lineno - 1:lineno] = list(repl)
        gitignore.write_text("\n".join(lines) + "\n", encoding="utf-8")


def stage(target_repo: Path, plan: Plan) -> None:
    paths = touched_paths(plan)
    if paths:
        git(target_repo, "add", "--", *paths)


def summarize(plan: Plan, sync_note: str) -> str:
    lines = []
    for label, items in (
        ("installed", [t for t, _ in plan.install]),
        ("updated", [t for t, _ in plan.update]),
        ("removed", plan.remove),
    ):
        for t in items:
            lines.append("  {}: {}".format(label, t))
    for lineno, old, _repl in plan.gitignore_repairs:
        lines.append("  .gitignore: repaired blanket rule '{}' (line {})".format(old, lineno))
    for t, reason in plan.flags:
        lines.append("  FLAG {}: {}".format(t, reason))
    if not lines:
        lines.append("  nothing to do - repo is current")
    if sync_note:
        lines.append("  NOTE: {}".format(sync_note))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?", default=".", help="governed repo (default: cwd)")
    ap.add_argument("--toolkit", default=None, help="toolkit root (default: this script's repo)")
    ap.add_argument("--stage-only", action="store_true", help="stage reconciled paths, do not commit (first-bootstrap mode)")
    ap.add_argument("--no-sync", action="store_true", help="skip syncing the toolkit clone")
    args = ap.parse_args(argv)

    toolkit = Path(args.toolkit).resolve() if args.toolkit else Path(__file__).resolve().parent.parent
    target = Path(args.target).resolve()

    if not is_git_repo(target):
        print("refresh: {} is not a git repository".format(target), file=sys.stderr)
        return 2
    if not (toolkit / "tools" / "shipped-set.json").exists():
        print("refresh: {} does not look like the toolkit (no tools/shipped-set.json)".format(toolkit), file=sys.stderr)
        return 2

    sync_note = "" if args.no_sync else sync_toolkit(toolkit)
    toolkit_sha = git(toolkit, "rev-parse", "--short", "HEAD").stdout.strip()

    shipped = load_shipped_set(toolkit)
    plan = classify(target, toolkit, shipped)
    check_committability(target, plan, shipped)

    conflicts = dirty_conflicts(target, plan)
    if conflicts:
        print("refresh: refusing to run over uncommitted changes on paths it would touch:", file=sys.stderr)
        for line in conflicts:
            print("  " + line, file=sys.stderr)
        return 3

    changed = bool(plan.install or plan.update or plan.remove or plan.gitignore_repairs)
    if changed:
        apply_plan(target, plan)
        stage(target, plan)
        if not args.stage_only:
            git(target, "commit", "-m",
                "governance refresh: toolkit {}\n\n{}".format(toolkit_sha, summarize(plan, "")))

    print("governance refresh against toolkit {}".format(toolkit_sha))
    print(summarize(plan, sync_note))
    if changed and args.stage_only:
        print("  (staged only - the bootstrap procedure makes the single scoped commit)")
    policy = target / ".agents" / "push-policy.md"
    if policy.exists():
        print("push policy: {}".format(policy.read_text(encoding="utf-8").strip().splitlines()[-1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
