#!/usr/bin/env python3
"""Reconcile a governed repo to the toolkit's shipped artifact set.

Pull-based, per-repo, no registry: run it while standing in (or pointing it
at) a governed repo. It syncs the local toolkit clone from its canonical
remote, then reconciles the target repo to tools/shipped-set.json:

  - replace-whole   (AGENTS.md): current or formerly-shipped versions update
                    normally. Divergent content forks on git evidence: if any
                    committed version of the file ever matched a shipped hash
                    the repo was governed, so the divergence is drift and the
                    file is RESTORED to current (reported with the commits
                    that introduced it); if no committed version ever matched,
                    it is a foreign governance file - flagged, never
                    overwritten, a migration rather than a refresh.
  - replace:        missing -> install; matches a formerly-shipped version ->
                    update to current; anything else -> drift: reported with
                    its introducing commits and RESTORED to current.
  - retired:        formerly-shipped paths are removed. Content matching no
                    shipped version is drift and is removed with a report.

Installed governance is toolkit-owned (owner ruling 2026-07-16): no
out-of-band edit to an installed artifact is legitimate, whoever made it, so
divergence is always drift and every run converges the repo to exactly the
shipped set. Nothing uncommitted is ever machine-destroyed: restores and
removes are touched paths, so the dirty-tree refusal fires first; committed
drift stays recoverable from git history.

Matching is newline-equivalent: CRLF normalizes to LF, and content differing
only by at most one trailing final newline matches - a file touched by
insert-final-newline tooling is not a divergence (issue #1).

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
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
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


def worktree_root_error(path: Path) -> "str | None":
    """Non-None reason when `path` is not the root of a git working tree.
    Bare repos and nested subdirectories are refused before any mutation —
    a nested install would govern a subtree and leave the root bare."""
    inside = git(path, "rev-parse", "--is-inside-work-tree", check=False)
    if inside.returncode != 0:
        return "not a git repository"
    if inside.stdout.strip() != "true":
        return "a bare repository (no working tree)"
    top = git(path, "rev-parse", "--show-toplevel", check=False)
    if top.returncode != 0 or not top.stdout.strip():
        return "missing a resolvable working-tree root"
    if Path(top.stdout.strip()).resolve() != path:
        return "not the working-tree root (that is {})".format(top.stdout.strip())
    return None


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


def maybe_reexec(head_before: str, head_after: str, environ=None, execv_fn=None,
                 script_argv=None) -> bool:
    """After a sync fast-forward, run the freshly synced runner exactly once:
    re-exec with --no-sync under a loop-guard marker, so a new manifest is
    never read by an old in-memory runner. Returns False when no re-exec is
    needed; a real re-exec never returns (fakes do, for tests)."""
    environ = os.environ if environ is None else environ
    if head_after == head_before or environ.get("AGB_REFRESH_REEXEC"):
        return False
    environ["AGB_REFRESH_REEXEC"] = "1"
    argv = [sys.executable, str(Path(__file__).resolve())]
    argv += list(sys.argv[1:] if script_argv is None else script_argv)
    if "--no-sync" not in argv:
        argv.append("--no-sync")
    (os.execv if execv_fn is None else execv_fn)(sys.executable, argv)
    return True


def load_shipped_set(toolkit: Path) -> dict:
    return json.loads((toolkit / "tools" / "shipped-set.json").read_text(encoding="utf-8"))


_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_KNOWN_CLASSES = ("replace-whole", "replace")


def validate_manifest(shipped: dict, toolkit: Path) -> "list[str]":
    """Structural safety checks before any read or write: the manifest is
    trusted input only after these hold. Relative paths only, no upward
    traversal, unique targets, known classes, well-formed hashes,
    existing sources."""
    errors = []
    seen = set()
    if shipped.get("schema") != 1:
        errors.append("unsupported or missing manifest schema (expected 1, got {!r})".format(shipped.get("schema")))

    def check_rel(kind, rel):
        p = Path(rel)
        if not rel or p.is_absolute() or rel.startswith(("/", "\\")):
            errors.append("{} path is absolute or empty: {!r}".format(kind, rel))
        elif ".." in p.parts:
            errors.append("{} path traverses upward: {}".format(kind, rel))

    for art in shipped.get("artifacts", []):
        tgt = art.get("target", "")
        check_rel("source", art.get("source", ""))
        check_rel("target", tgt)
        if tgt in seen:
            errors.append("duplicate target: {}".format(tgt))
        seen.add(tgt)
        if art.get("class") not in _KNOWN_CLASSES:
            errors.append("unknown class {!r} for {}".format(art.get("class"), tgt))
        elif not (toolkit / art.get("source", "")).is_file():
            errors.append("missing source file: {}".format(art.get("source")))
        for h in art.get("formerly", []):
            if not _HEX64.match(h):
                errors.append("malformed hash for {}: {!r}".format(tgt, h))
    for ret in shipped.get("retired", []):
        check_rel("retired target", ret.get("target", ""))
        for h in ret.get("formerly", []):
            if not _HEX64.match(h):
                errors.append("malformed hash for retired {}: {!r}".format(ret.get("target"), h))
    return errors


def assert_safe_dest(target_repo: Path, rel: str) -> None:
    """Refuse a destination whose existing components include a symlink or
    whose resolved parent escapes the repository root. The never-overwrite
    promise depends on writes landing exactly where the manifest names."""
    probe = target_repo
    for part in Path(rel).parts:
        probe = probe / part
        if probe.is_symlink():
            raise RuntimeError(
                "{}: {} is a symlink; refusing to write through it".format(rel, probe))
        if not probe.exists():
            break
    root = target_repo.resolve()
    resolved_parent = (target_repo / rel).parent.resolve()
    if resolved_parent != root and root not in resolved_parent.parents:
        raise RuntimeError("{}: resolves outside the repository root".format(rel))


def write_atomic(dest: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(dest.parent), prefix=".refresh-tmp-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, str(dest))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class Plan:
    def __init__(self) -> None:
        self.install = []   # (target, source_path)
        self.update = []    # (target, source_path)
        self.restore = []   # (target, source_path) - diverged, converged back
        self.remove = []    # target
        self.current = []   # target
        self.flags = []     # (target, reason)
        self.drift = {}     # target -> introducing-commit provenance line
        self.gitignore_repairs = []  # (line_no, old_line, new_lines)


def _drift_provenance(target_repo: Path, rel: str) -> str:
    """The last few commits that touched a diverged path - the audit trail
    that lets the owner see who introduced the drift without digging."""
    proc = git(target_repo, "log", "-3", "--format=%h %s", "--", rel, check=False)
    lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()] \
        if proc.returncode == 0 else []
    return " | ".join(lines) if lines else "no commit history for this path"


def _ever_shipped(target_repo: Path, rel: str, known: "set[str]") -> bool:
    """True when any committed historical version of `rel` matches a known
    shipped hash - evidence the repo was governed, so a present-day mismatch
    is drift to restore, not a foreign file to protect. Runs only when a
    replace-whole target diverges; blobs are read once each."""
    proc = git(target_repo, "log", "--format=%H", "--", rel, check=False)
    if proc.returncode != 0:
        return False
    seen = set()
    for commit in proc.stdout.split():
        blob = git(target_repo, "rev-parse", "{}:{}".format(commit, rel), check=False)
        oid = blob.stdout.strip()
        if blob.returncode != 0 or not oid or oid in seen:
            continue
        seen.add(oid)
        data = subprocess.run(["git", "-C", str(target_repo), "cat-file", "blob", oid],
                              capture_output=True)
        if data.returncode == 0 and candidate_hashes(data.stdout) & known:
            return True
    return False


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
        elif (candidate_hashes(tgt_bytes) & set(art.get("formerly", []))
              and not candidate_hashes(tgt_bytes) & candidate_hashes(src_bytes)):
            # A historical hash never widens the current equivalence
            # boundary: when the current source's own hash sits in
            # formerly[], a file within one newline of current-but-not-
            # stem-equal is drift to restore, never a silent update (M1).
            plan.update.append((art["target"], src))
        elif art["class"] == "replace-whole" and not _ever_shipped(
                target_repo, art["target"],
                set(art.get("formerly", [])) | candidate_hashes(src_bytes)):
            plan.flags.append((
                art["target"],
                "matches no known template version and no committed version ever "
                "did - a foreign governance file; refusing to replace. If this repo "
                "has never been bootstrapped by the toolkit, run the bootstrap "
                "procedure instead.",
            ))
        else:
            plan.restore.append((art["target"], src))
            plan.drift[art["target"]] = _drift_provenance(target_repo, art["target"])
    for ret in shipped.get("retired", []):
        tgt = target_repo / ret["target"]
        if not tgt.exists():
            continue
        if not candidate_hashes(tgt.read_bytes()) & set(ret.get("formerly", [])):
            plan.drift[ret["target"]] = _drift_provenance(target_repo, ret["target"])
        plan.remove.append(ret["target"])
    return plan


def check_committability(target_repo: Path, plan: Plan, shipped: dict) -> None:
    """check-ignore each path we would add; repair known blanket adapter-dir
    ignores in the repo's root .gitignore; flag-and-skip anything else."""
    paths = [t for t, _ in plan.install + plan.update + plan.restore]
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
            for lst in (plan.install, plan.update, plan.restore):
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
    ".agents/machines.md",
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
        for line in text.splitlines():
            if "lint: allow" in line:
                # The visible per-line escape for legitimate illustrative or
                # historical references (same convention as the plan lint).
                continue
            for m in PATH_TOKEN.finditer(line):
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


def manifest_digest(toolkit: Path) -> str:
    return hashlib.sha256(
        (toolkit / "tools" / "shipped-set.json").read_bytes()).hexdigest()


def build_record(toolkit: Path, target: Path, plan: Plan) -> dict:
    """The immutable operation record: what a human approves is what
    --apply later verifies, field for field, before any write."""
    def entry(t, s):
        return {"target": t,
                "source": Path(s).relative_to(toolkit).as_posix(),
                "sha256": hashlib.sha256(Path(s).read_bytes()).hexdigest()}
    head = git(target, "rev-parse", "HEAD", check=False)
    rec = {
        "schema": 1,
        "toolkit_sha": git(toolkit, "rev-parse", "HEAD").stdout.strip(),
        "toolkit_dirty": bool(
            git(toolkit, "status", "--porcelain", check=False).stdout.strip()),
        "manifest_digest": manifest_digest(toolkit),
        "target_head": head.stdout.strip() if head.returncode == 0 else "",
        "installs": [entry(t, s) for t, s in plan.install],
        "updates": [entry(t, s) for t, s in plan.update],
        "restores": [entry(t, s) for t, s in plan.restore],
        "drift": dict(sorted(plan.drift.items())),
        "removes": list(plan.remove),
        "gitignore_repairs": [[ln, old, list(repl)]
                              for ln, old, repl in plan.gitignore_repairs],
        "flags": [[t, r] for t, r in plan.flags],
        "staged_paths": touched_paths(plan),
    }
    canonical = json.dumps(rec, sort_keys=True, separators=(",", ":"))
    rec["digest"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return rec


def verify_record(record: dict, toolkit: Path, target: Path, plan: Plan) -> "list[str]":
    """Reasons an approved plan record no longer matches reality. Any
    non-empty result refuses the apply before the first write."""
    if record.get("schema") != 1:
        return ["unsupported plan schema: {!r}".format(record.get("schema"))]
    current = build_record(toolkit, target, plan)
    problems = []
    if current["toolkit_dirty"] or record.get("toolkit_dirty"):
        problems.append("toolkit worktree is dirty (apply requires a clean tree)")
    for field in ("toolkit_sha", "manifest_digest", "target_head", "installs",
                  "updates", "restores", "drift", "removes",
                  "gitignore_repairs", "flags", "staged_paths"):
        if current[field] != record.get(field):
            problems.append("drift in {}: the current state no longer matches the approved plan".format(field))
    if not problems and current["digest"] != record.get("digest"):
        problems.append("plan digest mismatch")
    return problems


def touched_paths(plan: Plan) -> list:
    paths = [t for t, _ in plan.install + plan.update + plan.restore] + list(plan.remove)
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
    # Validate every destination before the first write: a refusal must
    # leave the tree untouched, never partially mutated.
    for target, _src in plan.install + plan.update + plan.restore:
        assert_safe_dest(target_repo, target)
    for target in plan.remove:
        assert_safe_dest(target_repo, target)
    if plan.gitignore_repairs:
        assert_safe_dest(target_repo, ".gitignore")
    for target, src in plan.install + plan.update + plan.restore:
        dest = target_repo / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        write_atomic(dest, src.read_bytes())
    for target in plan.remove:
        (target_repo / target).unlink()
    if plan.gitignore_repairs:
        gitignore = target_repo / ".gitignore"
        lines = gitignore.read_text(encoding="utf-8").splitlines()
        # apply bottom-up so line numbers stay valid
        for lineno, _old, repl in sorted(plan.gitignore_repairs, reverse=True):
            lines[lineno - 1:lineno] = list(repl)
        write_atomic(gitignore, ("\n".join(lines) + "\n").encode("utf-8"))


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


def render_cmd(argv, windows=None) -> str:
    """Platform-correct copy/paste rendering: POSIX quoting is wrong for
    Windows shells, so render with list2cmdline there."""
    win = (os.name == "nt") if windows is None else windows
    return subprocess.list2cmdline(argv) if win else shlex.join(argv)


def non_tty_commands(candidates, prompt: str, target: Path, toolkit: Path) -> str:
    """The non-interactive fallback under the banner: never prompt, never
    hang - print the exact ready-to-paste launch command per detected
    harness (or the procedure path when nothing is installed)."""
    if not candidates:
        return ("  no known harness CLI found on PATH; the procedure is\n"
                "  {}".format(toolkit / "procedures" / "bootstrap.md"))
    lines = ["  to run bootstrap, launch one of these in {}:".format(target)]
    for _name, shape in candidates:
        lines.append("    " + render_cmd(launch_argv(shape, prompt)))
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
    ):
        for t in items:
            lines.append("  {}: {}".format(label, t))
    for t, _src in plan.restore:
        lines.append("  restored: {} (DRIFT: matched no shipped version; recent: {})".format(
            t, plan.drift.get(t, "")))
    for t in plan.remove:
        if t in plan.drift:
            lines.append("  removed: {} (DRIFT: matched no shipped version; recent: {})".format(
                t, plan.drift[t]))
        else:
            lines.append("  removed: {}".format(t))
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
    ap.add_argument("--plan-json", default=None, metavar="PATH",
                    help="read-only: write the operation record as JSON (or - for stdout) and change nothing")
    ap.add_argument("--apply", default=None, metavar="PLAN",
                    help="apply a --plan-json record, refusing if anything drifted since it was made")
    args = ap.parse_args(argv)

    if args.plan_json and args.apply:
        print("refresh: --plan-json and --apply are mutually exclusive", file=sys.stderr)
        return 2
    plan_record = None
    if args.apply:
        try:
            plan_record = json.loads(Path(args.apply).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print("refresh: cannot read plan {}: {}".format(args.apply, exc), file=sys.stderr)
            return 2
        args.no_sync = True  # apply never resyncs: the record is the operation

    toolkit = Path(args.toolkit).resolve() if args.toolkit else Path(__file__).resolve().parent.parent
    target = Path(args.target).resolve()

    err = worktree_root_error(target)
    if err:
        print("refresh: {} is {}".format(target, err), file=sys.stderr)
        return 2
    if not (toolkit / "tools" / "shipped-set.json").exists():
        print("refresh: {} does not look like the toolkit (no tools/shipped-set.json)".format(toolkit), file=sys.stderr)
        return 2

    # Preflight: every fatal read happens before the first write, so a
    # nonzero exit always means "nothing changed" — never half-committed.
    policy_path = target / ".agents" / "push-policy.md"
    policy_line = None
    if policy_path.exists():
        policy_lines = policy_path.read_text(encoding="utf-8").strip().splitlines()
        if not policy_lines:
            print("refresh: {} is empty or malformed; fix the push policy before refreshing".format(policy_path), file=sys.stderr)
            return 4
        policy_line = policy_lines[-1]

    sync_note = ""
    if not args.no_sync:
        head_before = git(toolkit, "rev-parse", "HEAD").stdout.strip()
        sync_note = sync_toolkit(toolkit)
        head_after = git(toolkit, "rev-parse", "HEAD").stdout.strip()
        maybe_reexec(head_before, head_after)
    toolkit_sha = git(toolkit, "rev-parse", "--short", "HEAD").stdout.strip()

    shipped = load_shipped_set(toolkit)
    manifest_errors = validate_manifest(shipped, toolkit)
    if manifest_errors:
        print("refresh: tools/shipped-set.json failed validation:", file=sys.stderr)
        for e in manifest_errors:
            print("  " + e, file=sys.stderr)
        return 4
    plan = classify(target, toolkit, shipped)
    check_committability(target, plan, shipped)
    core = core_flags(plan, shipped)

    conflicts = dirty_conflicts(target, plan)
    if conflicts:
        print("refresh: refusing to run over uncommitted changes on paths it would touch:", file=sys.stderr)
        for line in conflicts:
            print("  " + line, file=sys.stderr)
        return 3

    if args.plan_json:
        record = build_record(toolkit, target, plan)
        payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
        if args.plan_json == "-":
            sys.stdout.write(payload)
        else:
            Path(args.plan_json).write_text(payload, encoding="utf-8")
        print("governance refresh plan against toolkit {} (read-only - nothing changed)".format(toolkit_sha))
        print(summarize(plan, sync_note))
        for rel, note_msg, kind in lint_governance(target):
            print("  {} {}: {}".format("NOTE" if kind == "note" else "LINT", rel, note_msg))
        return 0

    if plan_record is not None:
        problems = verify_record(plan_record, toolkit, target, plan)
        if problems:
            print("refresh: refusing --apply; the approved plan no longer matches:", file=sys.stderr)
            for p in problems:
                print("  " + p, file=sys.stderr)
            return 4

    changed = bool(plan.install or plan.update or plan.restore or plan.remove
                   or plan.gitignore_repairs)
    if changed:
        try:
            apply_plan(target, plan)
        except RuntimeError as exc:
            print("refresh: refusing unsafe write - {}".format(exc), file=sys.stderr)
            return 4
        stage(target, plan)
        if not args.stage_only:
            # Pathspec-scoped commit: unrelated pre-staged work stays staged
            # and out of the governance commit, then the created commit is
            # verified to touch exactly the planned paths.
            paths = touched_paths(plan)
            msg = "governance refresh: toolkit {}\n\n{}".format(toolkit_sha, summarize(plan, ""))
            if plan_record is not None:
                msg += "\n\ntoolkit-sha: {}\nplan-digest: {}".format(
                    plan_record.get("toolkit_sha", ""), plan_record.get("digest", ""))
            git(target, "commit", "-m", msg, "--", *paths)
            committed = set(
                git(target, "show", "--name-only", "--format=", "HEAD").stdout.splitlines())
            committed.discard("")
            if committed != set(paths):
                print("refresh: the created commit does not match the plan "
                      "(expected {}; got {}). The commit exists - inspect it "
                      "before retrying.".format(sorted(set(paths)), sorted(committed)),
                      file=sys.stderr)
                return 4

    print("governance refresh against toolkit {}".format(toolkit_sha))
    print(summarize(plan, sync_note))
    if git(toolkit, "status", "--porcelain", check=False).stdout.strip():
        print("  NOTE: toolkit tree is dirty; installed bytes may not match {}".format(toolkit_sha))
    for rel, msg, kind in lint_governance(target):
        print("  {} {}: {}".format("NOTE" if kind == "note" else "LINT", rel, msg))
    if changed and args.stage_only:
        print("  (staged only - the bootstrap procedure makes the single scoped commit)")
    if policy_line is not None:
        print("push policy: {}".format(policy_line))

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
