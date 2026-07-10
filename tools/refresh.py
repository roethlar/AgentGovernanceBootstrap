#!/usr/bin/env python3
"""Reconcile a governed repo to the toolkit's shipped artifact set.

Pull-based, per-repo, no registry: run it while standing in (or pointing it
at) a governed repo. It syncs the local toolkit clone from its canonical
remote, then reconciles the target repo to tools/shipped-set.json:

  - replace-whole   (AGENTS.md): replaced only when the existing file matches
                    the current or a formerly-shipped template version
                    (newline-equivalent). Anything else is flagged, never
                    overwritten - a content-bearing foreign AGENTS.md is a
                    migration, not a refresh.
  - replace-if-unmodified: missing -> install; matches a formerly-shipped
                    version -> update to current; anything else ->
                    owner-modified: flagged, never overwritten.
  - retired:        formerly-shipped paths are removed only when they match a
                    formerly-shipped version; otherwise flagged. A modified
                    file is never deleted by machine.

Matching is newline-equivalent: CRLF normalizes to LF, and content differing
only by at most one trailing final newline matches - a file touched by
insert-final-newline tooling is not an owner edit (issue #1).

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

Python 3.10+, stdlib only.
"""

import argparse
import hashlib
import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

CANONICAL_URLS = [
    # Order matters: GitHub is canon and is tried first whenever reachable;
    # the LAN gitea mirror is only a fallback when GitHub does not respond.
    # (Mirror-first would fast-forward to a lagging mirror head and silently
    # run a stale toolkit.) Offline -> proceed on the local copy with a flag.
    "https://github.com/roethlar/AgentGovernanceBootstrap.git",
    "http://q:3000/michael/AgentGovernanceBootstrap.git",
]

ADAPTER_DIRS = (".claude", ".codex", ".gemini", ".grok")


def norm(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def _stem(data: bytes) -> bytes:
    """Equivalence stem: normalized bytes minus at most one trailing newline."""
    n = norm(data)
    return n[:-1] if n.endswith(b"\n") else n


def candidate_hashes(data: bytes) -> "set[str]":
    """The nhash values every byte-form equivalent to `data` can have
    recorded: the stem itself and the stem plus one final newline."""
    stem = _stem(data)
    return {hashlib.sha256(stem).hexdigest(),
            hashlib.sha256(stem + b"\n").hexdigest()}


def nhash(data: bytes) -> str:
    """The maintenance-rule hash: shipped-set.json formerly[] entries are
    nhash of the outgoing source bytes (see the manifest comment)."""
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
        tgt = target_repo / art["target"]
        if not tgt.exists():
            plan.install.append((art["target"], src))
            continue
        tgt_bytes = tgt.read_bytes()
        if _stem(tgt_bytes) == _stem(src_bytes):
            plan.current.append(art["target"])
        elif candidate_hashes(tgt_bytes) & set(art.get("formerly", [])):
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
        if candidate_hashes(tgt.read_bytes()) & set(ret.get("formerly", [])):
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


PATH_TOKEN = re.compile(r"`([^`\s]+)`")

# The toolkit's own designated create-on-first-use homes: the template and
# the decisions header name these before a repo's first rotation creates
# them, so their absence is expected in every fresh repo, not a dead
# reference (field finding, 2026-07-08).
LINT_EXEMPT_PATHS = frozenset({
    "docs/history",
    "docs/history/state-archive.md",
    "docs/history/decisions-archive.md",
})


def _lintable_repo_path(tok: str) -> bool:
    """True for backtick tokens that read as repo-relative file references.
    Conservative by design: commands, URLs, globs, placeholders, file:line
    cites, absolute/outside paths, and bare shorthand names are all skipped —
    a missed lint is cheap, a false LINT line erodes trust in the report."""
    if any(c in tok for c in ":<>*{}$\\(),"):
        return False
    if tok.startswith(("http", "..", "~", "/", "-", "@")):
        return False
    return "/" in tok


def _deletion_commit(target_repo, tok, _cache):
    """Short hash of the commit that deleted `tok`, or None. Git is the
    no-maintenance evidence that a missing path is historical rather than a
    typo: a deliberate deletion always left a commit behind, a typo never
    did (owner direction, 2026-07-09 — no allowlists, consult history,
    print the note). Any failure (never tracked, shallow clone, not a git
    repo) returns None and the caller keeps the loud warning: degradation
    is toward loud, never toward silent-wrong."""
    key = tok.rstrip("/")
    if key not in _cache:
        proc = git(target_repo, "log", "--diff-filter=D", "--format=%h",
                   "-1", "--", key, check=False)
        out = proc.stdout.strip().splitlines() if proc.returncode == 0 else []
        _cache[key] = out[0].strip() if out else None
    return _cache[key]


def lint_governance(target_repo: Path) -> list:
    """Read-only hygiene checks over the repo-authored governance prose
    (`.agents/*.md` — NOT `AGENTS.md`, whose text is the byte-verified
    template and whose references are template-intentional). Never blocks,
    never edits; emits LINT report lines only. Runs on every refresh —
    the field lesson is that checks nobody triggers rot, checks riding an
    existing touchpoint stay true."""
    findings = []
    files = []
    deleted_cache = {}
    agents_dir = target_repo / ".agents"
    if agents_dir.is_dir():
        files += sorted(agents_dir.glob("*.md"))
    for f in files:
        if not f.is_file():
            continue
        rel = f.relative_to(target_repo).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        seen = set()
        for m in PATH_TOKEN.finditer(text):
            tok = m.group(1)
            if tok in seen or not _lintable_repo_path(tok):
                continue
            seen.add(tok)
            if tok.rstrip("/") in LINT_EXEMPT_PATHS:
                continue
            if not (target_repo / tok.rstrip("/")).exists():
                dh = _deletion_commit(target_repo, tok, deleted_cache)
                if dh:
                    findings.append((rel, "historical: `{}` - deleted in {}".format(tok, dh), "note"))
                else:
                    findings.append((rel, "references missing path `{}`".format(tok), "warn"))
        if f.name == "decisions.md":
            entries = list(re.finditer(r"^### (.+)$", text, re.M))
            for i, em in enumerate(entries):
                end = entries[i + 1].start() if i + 1 < len(entries) else len(text)
                seg = text[em.end():end]
                sm = re.search(r"^Status:\s*(\w+)", seg, re.M)
                if sm and sm.group(1) in ("Adopted", "Superseded"):
                    findings.append((rel, "closed decision awaiting archive: {}".format(em.group(1)[:70]), "warn"))
    return findings


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


# Harness CLIs that can run the bootstrap procedure, with the interactive
# launch shape ("{prompt}" is the kickoff slot). Seeded from the recorded
# live behavior in docs/harness-capabilities.md; adding or changing an entry
# is a provenance-bearing change (2026-07-08 standing rule). gemini renamed
# agy per owner 2026-07-09.
HARNESSES = [
    ("claude", ("claude", "{prompt}")),
    ("codex", ("codex", "{prompt}")),
    ("agy", ("agy", "-i", "{prompt}")),
    ("grok", ("grok", "{prompt}")),
]


def detect_harnesses(which=shutil.which):
    """Harness CLIs actually installed right now - probed at offer time,
    never remembered between runs."""
    return [(name, shape) for name, shape in HARNESSES if which(name)]


def core_flags(plan: Plan, shipped: dict) -> list:
    """Flag targets in the replace-whole (core file) class - the one flag
    category that is never a legitimate steady state."""
    whole = {a["target"] for a in shipped["artifacts"]
             if a["class"] == "replace-whole"}
    return [t for t, _ in plan.flags if t in whole]


def banner_block(targets) -> str:
    bar = "=" * 66
    lines = [bar]
    for t in targets:
        lines.append("  ATTENTION: {} was NOT replaced.".format(t))
    lines.append("  It matches no known template version (hand-edited or foreign).")
    lines.append("  Hand-repair is not the fix. The fix is the bootstrap procedure.")
    lines.append(bar)
    return "\n".join(lines)


def bootstrap_prompt(toolkit: Path, target: Path) -> str:
    return ("Read {} in full, then run the bootstrap procedure against this "
            "repo ({}). Governance refresh refused to replace a core "
            "governance file here; the procedure owns recovery, including "
            "the legacy-governance carve-out.").format(
                toolkit / "procedures" / "bootstrap.md", target)


def launch_argv(shape, prompt: str) -> list:
    return [part.replace("{prompt}", prompt) for part in shape]


def non_tty_commands(candidates, prompt: str, target: Path, toolkit: Path) -> str:
    """The non-interactive fallback under the banner: never prompt, never
    hang - print the exact ready-to-paste launch command per detected
    harness (or the procedure path when nothing is installed)."""
    if not candidates:
        return ("  no known harness CLI found on PATH; the procedure is\n"
                "  {}".format(toolkit / "procedures" / "bootstrap.md"))
    lines = ["  to run bootstrap, launch one of these in {}:".format(target)]
    for _name, shape in candidates:
        lines.append("    " + shlex.join(launch_argv(shape, prompt)))
    return "\n".join(lines)


def offer_bootstrap(candidates, prompt: str, target: Path,
                    input_fn=input, launch_fn=None):
    """One question at a real TTY; a valid number launches that harness
    interactively in the target repo with the kickoff prompt; anything else
    (q, empty, EOF, out-of-range) declines and changes nothing. Returns the
    harness exit code, or None when declined. Callers gate on isatty - this
    function is never reached non-interactively."""
    menu = "  ".join("[{}] {}".format(i + 1, name)
                     for i, (name, _shape) in enumerate(candidates))
    try:
        choice = input_fn("Run bootstrap now? Installed harnesses: "
                          "{}  [q] no\n> ".format(menu)).strip()
    except EOFError:
        return None
    if not choice.isdigit() or not (1 <= int(choice) <= len(candidates)):
        return None
    _name, shape = candidates[int(choice) - 1]
    argv = launch_argv(shape, prompt)
    if launch_fn is None:
        launch_fn = lambda a: subprocess.call(a, cwd=str(target))
    return launch_fn(argv)


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
    for rel, msg, kind in lint_governance(target):
        print("  {} {}: {}".format("NOTE" if kind == "note" else "LINT", rel, msg))
    if changed and args.stage_only:
        print("  (staged only - the bootstrap procedure makes the single scoped commit)")
    policy = target / ".agents" / "push-policy.md"
    if policy.exists():
        print("push policy: {}".format(policy.read_text(encoding="utf-8").strip().splitlines()[-1]))

    core = core_flags(plan, shipped)
    if core:
        print(banner_block(core))
        prompt = bootstrap_prompt(toolkit, target)
        candidates = detect_harnesses()
        if candidates and sys.stdin.isatty() and sys.stdout.isatty():
            offer_bootstrap(candidates, prompt, target)
        else:
            print(non_tty_commands(candidates, prompt, target, toolkit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
