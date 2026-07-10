"""Behavioral tests for tools/refresh.py against a hermetic fixture toolkit.

Each test builds a throwaway toolkit repo (mini shipped set) and a throwaway
target repo, then runs refresh.py end-to-end via subprocess (or in-process
for the sync unit test). No test touches the real toolkit's shipped set or
any real remote.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
REFRESH = TOOLS / "refresh.py"

CUR_AGENTS = "# Agent Guidance\ncurrent template body\n"
OLD_AGENTS = "# Agent Guidance\nold template body\n"
CUR_TOOL = "current tool wrapper\n"
OLD_TOOL = "old tool wrapper\n"
CUR_SETTINGS = '{"hooks": "current"}\n'
OLD_SETTINGS = '{"hooks": "old"}\n'
OLD_HOOK = "retired hook script\n"
CUR_SHIM = "@AGENTS.md"  # no final newline - the canonical shape that produced issue #1


def nhash(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode()).hexdigest()


def run_git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise AssertionError("git {} failed: {}".format(args, proc.stderr))
    return proc.stdout


def init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    run_git(path, "config", "user.email", "test@example.invalid")
    run_git(path, "config", "user.name", "Test")
    run_git(path, "config", "core.autocrlf", "false")


def commit_all(repo: Path, msg: str = "base") -> None:
    run_git(repo, "add", "-A")
    run_git(repo, "commit", "-q", "-m", msg)


def make_toolkit(root: Path) -> Path:
    tk = root / "toolkit"
    init_repo(tk)
    (tk / "templates" / "commands" / "claude").mkdir(parents=True)
    (tk / "templates" / "hooks" / "claude").mkdir(parents=True)
    (tk / "templates" / "shims").mkdir(parents=True)
    (tk / "tools").mkdir()
    (tk / "templates" / "AGENTS.template.md").write_text(CUR_AGENTS, newline="\n")
    (tk / "templates" / "commands" / "claude" / "tool.md").write_text(CUR_TOOL, newline="\n")
    (tk / "templates" / "hooks" / "claude" / "settings.json").write_text(CUR_SETTINGS, newline="\n")
    (tk / "templates" / "shims" / "CLAUDE.template.md").write_text(CUR_SHIM, newline="\n")
    shipped = {
        "artifacts": [
            {"source": "templates/AGENTS.template.md", "target": "AGENTS.md",
             "class": "replace-whole", "formerly": [nhash(OLD_AGENTS)]},
            {"source": "templates/commands/claude/tool.md", "target": ".claude/commands/tool.md",
             "class": "replace-if-unmodified", "formerly": [nhash(OLD_TOOL)]},
            {"source": "templates/hooks/claude/settings.json", "target": ".claude/settings.json",
             "class": "replace-if-unmodified", "formerly": [nhash(OLD_SETTINGS)]},
            {"source": "templates/shims/CLAUDE.template.md", "target": "CLAUDE.md",
             "class": "replace-if-unmodified", "formerly": []},
        ],
        "retired": [
            {"target": ".claude/old-hook.py", "formerly": [nhash(OLD_HOOK)]},
        ],
        "machine_local_exclusions": {".claude": [".claude/settings.local.json"]},
    }
    (tk / "tools" / "shipped-set.json").write_text(json.dumps(shipped), newline="\n")
    commit_all(tk)
    return tk


def make_target(root: Path) -> Path:
    tgt = root / "target"
    init_repo(tgt)
    (tgt / "README.md").write_text("hello\n", newline="\n")
    commit_all(tgt)
    return tgt


def refresh(toolkit: Path, target: Path, *extra: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        [sys.executable, str(REFRESH), str(target),
         "--toolkit", str(toolkit), "--no-sync", *extra],
        capture_output=True, text=True, encoding="utf-8",
        stdin=subprocess.DEVNULL)


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.toolkit = make_toolkit(self.root)
        self.target = make_target(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def commits(self):
        return run_git(self.target, "log", "--oneline").splitlines()

    # -- install / idempotence ------------------------------------------

    def test_installs_full_set_into_bare_repo_and_commits(self):
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self.target / "AGENTS.md").read_text(), CUR_AGENTS)
        self.assertEqual((self.target / ".claude" / "commands" / "tool.md").read_text(), CUR_TOOL)
        self.assertEqual((self.target / ".claude" / "settings.json").read_text(), CUR_SETTINGS)
        head = run_git(self.target, "log", "-1", "--format=%B")
        self.assertIn("governance refresh: toolkit ", head)

    def test_second_run_is_a_noop(self):
        refresh(self.toolkit, self.target)
        n = len(self.commits())
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("nothing to do", proc.stdout)
        self.assertEqual(len(self.commits()), n)

    # -- replace-if-unmodified ------------------------------------------

    def test_unmodified_stale_artifact_updates(self):
        (self.target / ".claude" / "commands").mkdir(parents=True)
        (self.target / ".claude" / "commands" / "tool.md").write_text(OLD_TOOL, newline="\n")
        commit_all(self.target, "stale wrapper")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self.target / ".claude" / "commands" / "tool.md").read_text(), CUR_TOOL)
        self.assertIn("updated: .claude/commands/tool.md", proc.stdout)

    def test_owner_modified_artifact_is_flagged_not_overwritten(self):
        (self.target / ".claude" / "commands").mkdir(parents=True)
        (self.target / ".claude" / "commands" / "tool.md").write_text("my custom wrapper\n", newline="\n")
        commit_all(self.target, "custom wrapper")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual((self.target / ".claude" / "commands" / "tool.md").read_text(), "my custom wrapper\n")
        self.assertIn("FLAG .claude/commands/tool.md", proc.stdout)

    # -- replace-whole (AGENTS.md) --------------------------------------

    def test_formerly_shipped_agents_md_is_replaced(self):
        (self.target / "AGENTS.md").write_text(OLD_AGENTS, newline="\n")
        commit_all(self.target, "old agents")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual((self.target / "AGENTS.md").read_text(), CUR_AGENTS)

    def test_foreign_agents_md_is_flagged_never_replaced(self):
        (self.target / "AGENTS.md").write_text("# My own house rules\n", newline="\n")
        commit_all(self.target, "foreign agents")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual((self.target / "AGENTS.md").read_text(), "# My own house rules\n")
        self.assertIn("FLAG AGENTS.md", proc.stdout)
        self.assertIn("bootstrap procedure", proc.stdout)

    # -- preflight before mutation ---------------------------------------
    # A nonzero exit must always mean "nothing changed": target validation
    # and push-policy parsing happen before the first write.

    def test_bare_repo_is_refused(self):
        bare = self.root / "bare.git"
        subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
        proc = refresh(self.toolkit, bare)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("bare repository", proc.stderr)

    def test_nested_directory_is_refused(self):
        sub = self.target / "sub"
        sub.mkdir()
        proc = refresh(self.toolkit, sub)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("working-tree root", proc.stderr)
        self.assertFalse((sub / "AGENTS.md").exists())

    def test_empty_push_policy_fails_before_any_write(self):
        (self.target / ".agents").mkdir()
        (self.target / ".agents" / "push-policy.md").write_text("", newline="\n")
        commit_all(self.target, "empty policy")
        n = len(self.commits())
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("push policy", proc.stderr)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertEqual(len(self.commits()), n)

    # -- filesystem containment ------------------------------------------
    # Writes must land exactly where the manifest names them: symlinked
    # components and unsafe manifest paths are refused with the tree
    # untouched.

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_broken_symlink_dest_refused_nothing_written(self):
        outside = self.root / "outside.md"
        (self.target / "AGENTS.md").symlink_to(outside)
        commit_all(self.target, "symlinked agents")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("symlink", proc.stderr)
        self.assertFalse(outside.exists())
        self.assertFalse((self.target / ".claude").exists())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_symlinked_parent_dir_refused(self):
        outside_dir = self.root / "outside-dir"
        outside_dir.mkdir()
        (self.target / ".claude").symlink_to(outside_dir)
        commit_all(self.target, "symlinked adapter dir")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("symlink", proc.stderr)
        self.assertEqual(list(outside_dir.iterdir()), [])

    def _mutate_manifest(self, fn):
        ss = self.toolkit / "tools" / "shipped-set.json"
        data = json.loads(ss.read_text(encoding="utf-8"))
        fn(data)
        with open(str(ss), "w", newline="\n") as f:
            json.dump(data, f)

    def test_manifest_traversal_target_refused(self):
        self._mutate_manifest(
            lambda d: d["artifacts"][0].update(target="../escape.md"))
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("traverses", proc.stderr)
        self.assertFalse((self.root / "escape.md").exists())
        self.assertFalse((self.target / ".claude").exists())

    def test_manifest_absolute_target_refused(self):
        evil = str(self.root / "evil.md")
        self._mutate_manifest(lambda d: d["artifacts"][0].update(target=evil))
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("absolute", proc.stderr)
        self.assertFalse((self.root / "evil.md").exists())

    def test_manifest_duplicate_target_refused(self):
        self._mutate_manifest(
            lambda d: d["artifacts"].append(dict(d["artifacts"][0])))
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("duplicate", proc.stderr)

    # -- exact commit scope ----------------------------------------------

    def test_pre_staged_unrelated_file_stays_out_of_the_commit(self):
        (self.target / "unrelated.txt").write_text("wip\n", newline="\n")
        run_git(self.target, "add", "unrelated.txt")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        committed = run_git(self.target, "show", "--name-only",
                            "--format=", "HEAD").split()
        self.assertIn("AGENTS.md", committed)
        self.assertNotIn("unrelated.txt", committed)
        staged = run_git(self.target, "diff", "--cached", "--name-only").split()
        self.assertIn("unrelated.txt", staged)

    # -- legacy carve-out route mechanics (bootstrap Step 7) -------------
    # Pins the behavior the two-commit carve-out route documents: refresh
    # refuses an uncommitted deletion of the foreign AGENTS.md (the
    # dirty-path guard), and installs with its own commit once the
    # deletion is committed - the route's commit 2.

    def test_uncommitted_foreign_agents_deletion_is_refused(self):
        (self.target / "AGENTS.md").write_text("# Legacy house rules\n", newline="\n")
        commit_all(self.target, "legacy governance")
        (self.target / "AGENTS.md").unlink()
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 3, proc.stderr)
        self.assertIn("uncommitted changes", proc.stderr)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / ".claude").exists())

    def test_committed_foreign_agents_deletion_installs_and_commits(self):
        (self.target / "AGENTS.md").write_text("# Legacy house rules\n", newline="\n")
        commit_all(self.target, "legacy governance")
        (self.target / "AGENTS.md").unlink()
        commit_all(self.target, "carve-out: delete legacy AGENTS.md")
        n = len(self.commits())
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self.target / "AGENTS.md").read_text(), CUR_AGENTS)
        self.assertEqual(len(self.commits()), n + 1)

    # -- newline normalization ------------------------------------------

    def test_crlf_checkout_of_current_content_is_treated_current(self):
        (self.target / "AGENTS.md").write_bytes(CUR_AGENTS.replace("\n", "\r\n").encode())
        commit_all(self.target, "crlf agents")
        n = len(self.commits())
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("FLAG AGENTS.md", proc.stdout)
        # AGENTS.md untouched (already current), only missing artifacts installed
        self.assertIn(b"\r\n", (self.target / "AGENTS.md").read_bytes())

    def test_crlf_checkout_of_formerly_shipped_updates_not_flags(self):
        (self.target / ".claude" / "commands").mkdir(parents=True)
        (self.target / ".claude" / "commands" / "tool.md").write_bytes(OLD_TOOL.replace("\n", "\r\n").encode())
        commit_all(self.target, "crlf stale wrapper")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual((self.target / ".claude" / "commands" / "tool.md").read_text(), CUR_TOOL)

    # -- trailing-newline equivalence (issue #1) --------------------------

    def test_shim_gaining_final_newline_stays_current_not_flagged(self):
        # The issue #1 repro: an installed no-final-newline shim is touched
        # by insert-final-newline tooling; refresh must read it as current,
        # not flag it owner-modified forever.
        refresh(self.toolkit, self.target)
        (self.target / "CLAUDE.md").write_bytes(CUR_SHIM.encode() + b"\n")
        commit_all(self.target, "editor adds final newline")
        n = len(self.commits())
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("FLAG CLAUDE.md", proc.stdout)
        self.assertIn("nothing to do", proc.stdout)
        self.assertEqual((self.target / "CLAUDE.md").read_bytes(), CUR_SHIM.encode() + b"\n")
        self.assertEqual(len(self.commits()), n)

    def test_current_content_minus_final_newline_is_current(self):
        (self.target / ".claude" / "commands").mkdir(parents=True)
        (self.target / ".claude" / "commands" / "tool.md").write_bytes(CUR_TOOL.rstrip("\n").encode())
        commit_all(self.target, "wrapper missing final newline")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("FLAG .claude/commands/tool.md", proc.stdout)
        self.assertEqual((self.target / ".claude" / "commands" / "tool.md").read_bytes(),
                         CUR_TOOL.rstrip("\n").encode())

    def test_formerly_shipped_minus_final_newline_updates_not_flags(self):
        (self.target / ".claude" / "commands").mkdir(parents=True)
        (self.target / ".claude" / "commands" / "tool.md").write_bytes(OLD_TOOL.rstrip("\n").encode())
        commit_all(self.target, "stale wrapper missing final newline")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual((self.target / ".claude" / "commands" / "tool.md").read_text(), CUR_TOOL)
        self.assertIn("updated: .claude/commands/tool.md", proc.stdout)

    def test_retired_artifact_minus_final_newline_is_removed(self):
        (self.target / ".claude").mkdir()
        (self.target / ".claude" / "old-hook.py").write_bytes(OLD_HOOK.rstrip("\n").encode())
        commit_all(self.target, "old hook missing final newline")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertFalse((self.target / ".claude" / "old-hook.py").exists())

    def test_second_trailing_newline_still_flags(self):
        # Equivalence stops at ONE trailing newline: a second one is a real
        # modification and must keep flagging.
        (self.target / ".claude" / "commands").mkdir(parents=True)
        (self.target / ".claude" / "commands" / "tool.md").write_bytes(CUR_TOOL.encode() + b"\n")
        commit_all(self.target, "double final newline")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("FLAG .claude/commands/tool.md", proc.stdout)
        self.assertEqual((self.target / ".claude" / "commands" / "tool.md").read_bytes(),
                         CUR_TOOL.encode() + b"\n")

    # -- retired ---------------------------------------------------------

    def test_retired_artifact_matching_formerly_shipped_is_removed(self):
        (self.target / ".claude").mkdir()
        (self.target / ".claude" / "old-hook.py").write_text(OLD_HOOK, newline="\n")
        commit_all(self.target, "old hook")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertFalse((self.target / ".claude" / "old-hook.py").exists())
        self.assertIn("removed: .claude/old-hook.py", proc.stdout)

    def test_modified_retired_artifact_is_flagged_kept(self):
        (self.target / ".claude").mkdir()
        (self.target / ".claude" / "old-hook.py").write_text("customized hook\n", newline="\n")
        commit_all(self.target, "custom old hook")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue((self.target / ".claude" / "old-hook.py").exists())
        self.assertIn("FLAG .claude/old-hook.py", proc.stdout)

    # -- committability / .gitignore -------------------------------------

    def test_blanket_adapter_ignore_is_repaired_and_committed(self):
        (self.target / ".gitignore").write_text(".claude/\n", newline="\n")
        commit_all(self.target, "blanket ignore")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        gi = (self.target / ".gitignore").read_text()
        self.assertNotIn(".claude/\n", gi.replace(".claude/settings.local.json", ""))
        self.assertIn(".claude/settings.local.json", gi)
        tracked = run_git(self.target, "ls-files")
        self.assertIn(".claude/commands/tool.md", tracked)
        self.assertEqual(run_git(self.target, "status", "--porcelain").strip(), "")

    def test_unrecognized_ignore_rule_flags_and_skips(self):
        (self.target / ".gitignore").write_text("*.json\n", newline="\n")
        commit_all(self.target, "json ignore")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertFalse((self.target / ".claude" / "settings.json").exists())
        self.assertIn("FLAG .claude/settings.json", proc.stdout)
        self.assertIn("never force-added", proc.stdout)
        gi = (self.target / ".gitignore").read_text()
        self.assertEqual(gi, "*.json\n")

    # -- dirty-tree refusal ----------------------------------------------

    def test_refuses_when_a_touched_path_is_dirty(self):
        (self.target / ".gitignore").write_text(".claude/\n", newline="\n")
        commit_all(self.target, "blanket ignore")
        with open(self.target / ".gitignore", "a", newline="\n") as f:
            f.write("# uncommitted local edit\n")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 3)
        self.assertIn("refusing", proc.stderr)
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_dirty_unrelated_path_does_not_block(self):
        (self.target / "notes.txt").write_text("scratch\n", newline="\n")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.target / "AGENTS.md").exists())

    # -- stage-only -------------------------------------------------------

    def test_stage_only_stages_without_committing(self):
        drafts = self.target / ".agents"
        drafts.mkdir()
        (drafts / "state.md").write_text("draft state\n", newline="\n")
        run_git(self.target, "add", "--", ".agents/state.md")
        n = len(self.commits())
        proc = refresh(self.toolkit, self.target, "--stage-only")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(self.commits()), n)
        staged = run_git(self.target, "diff", "--cached", "--name-only").splitlines()
        self.assertIn("AGENTS.md", staged)
        self.assertIn(".agents/state.md", staged)  # pre-staged foreign path untouched
        self.assertIn("staged only", proc.stdout)

    # -- governance lint (always on, read-only) ----------------------------

    def test_lint_flags_dead_path_reference(self):
        ag = self.target / ".agents"
        ag.mkdir()
        (ag / "state.md").write_text(
            "See `.agents/repo-map.json` and `docs/plan.md` for details.\n", newline="\n")
        commit_all(self.target, "state with dead pointers")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("LINT .agents/state.md: references missing path `.agents/repo-map.json`", proc.stdout)
        self.assertIn("references missing path `docs/plan.md`", proc.stdout)

    def test_lint_notes_git_vouched_deletion_instead_of_warning(self):
        # Owner direction 2026-07-09: verbatim historical records name
        # retired substrate forever; when git holds the deletion commit the
        # line is a NOTE carrying that provenance, not a warning. Paths git
        # never tracked keep the loud LINT line - a typo never left a
        # deletion commit, so the check stays typo-safe with no allowlist.
        (self.target / "tools").mkdir()
        (self.target / "tools" / "old-tool.py").write_text("x\n", newline="\n")
        commit_all(self.target, "add old tool")
        run_git(self.target, "rm", "-q", "tools/old-tool.py")
        run_git(self.target, "commit", "-q", "-m", "retire old tool")
        short = run_git(self.target, "log", "--diff-filter=D", "--format=%h",
                        "-1", "--", "tools/old-tool.py").strip()
        ag = self.target / ".agents"
        ag.mkdir()
        (ag / "decisions.md").write_text(
            "# D\n\nWe retired `tools/old-tool.py`; `docs/never-was.md` never existed.\n",
            newline="\n")
        commit_all(self.target, "decision naming retired tool")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertIn(
            "NOTE .agents/decisions.md: historical: `tools/old-tool.py` - deleted in {}".format(short),
            proc.stdout)
        self.assertNotIn("missing path `tools/old-tool.py`", proc.stdout)
        self.assertIn(
            "LINT .agents/decisions.md: references missing path `docs/never-was.md`",
            proc.stdout)

    def test_lint_notes_deleted_directory_mentioned_with_trailing_slash(self):
        d = self.target / "drafts"
        d.mkdir()
        (d / "a.md").write_text("x\n", newline="\n")
        commit_all(self.target, "add drafts")
        run_git(self.target, "rm", "-q", "-r", "drafts")
        run_git(self.target, "commit", "-q", "-m", "retire drafts")
        ag = self.target / ".agents"
        ag.mkdir()
        (ag / "state.md").write_text(
            "Scratch lived in `drafts/` back then.\n", newline="\n")
        commit_all(self.target, "state naming retired dir")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("NOTE .agents/state.md: historical: `drafts/` - deleted in ", proc.stdout)
        self.assertNotIn("LINT .agents/state.md", proc.stdout)

    def test_lint_skips_existing_commands_urls_and_placeholders(self):
        ag = self.target / ".agents"
        ag.mkdir()
        (ag / "repo-guidance.md").write_text(
            "Run `git ls-remote --exit-code` then `npm run e2e`.\n"
            "See `http://q:3000/x/y.md`, `docs/plan.md:15`, `.claude/commands/<name>.md`,\n"
            "`procedures/*.md`, and `README.md` (exists at root, no slash - skipped).\n"
            "Real file: `.agents/repo-guidance.md`.\n", newline="\n")
        commit_all(self.target, "guidance with skip-worthy tokens")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("LINT .agents/repo-guidance.md", proc.stdout)

    def test_lint_flags_closed_decision_awaiting_archive(self):
        ag = self.target / ".agents"
        ag.mkdir()
        (ag / "decisions.md").write_text(
            "# Decisions\n\n### Old rule\n\nStatus: Adopted 2026-07-01\n\nbody\n\n"
            "### Live rule\n\nStatus: Active\n\nbody\n", newline="\n")
        commit_all(self.target, "decisions")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("closed decision awaiting archive: Old rule", proc.stdout)
        self.assertNotIn("Live rule", proc.stdout)

    def test_lint_skips_agents_md_and_create_on_first_use_archives(self):
        # Field finding 2026-07-08 (Move-SteamGame refresh): the template and
        # the decisions header name docs/history archive paths "create on
        # first use", so every fresh repo flagged them — trust-eroding noise.
        # AGENTS.md is the byte-verified template: never linted. The
        # designated archive paths are exempt everywhere.
        (self.target / "AGENTS.md").write_text(
            CUR_AGENTS + "\nSee `docs/nonexistent-thing.md` and `docs/history/state-archive.md`.\n",
            newline="\n")
        ag = self.target / ".agents"
        ag.mkdir()
        (ag / "state.md").write_text(
            "Rotate to `docs/history/state-archive.md` (create on first use).\n",
            newline="\n")
        (ag / "decisions.md").write_text(
            "# D\n\nArchive: `docs/history/decisions-archive.md` under `docs/history/`.\n",
            newline="\n")
        commit_all(self.target, "fresh governance, no archives yet")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("LINT", proc.stdout)

    def test_lint_never_blocks_commit_or_exit(self):
        ag = self.target / ".agents"
        ag.mkdir()
        (ag / "state.md").write_text("Dead: `.agents/gone.md`\n", newline="\n")
        commit_all(self.target, "dead pointer present")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        head = run_git(self.target, "log", "-1", "--format=%B")
        self.assertIn("governance refresh: toolkit ", head)  # commit still made

    # -- refusals ----------------------------------------------------------

    def test_non_git_target_is_refused(self):
        plain = self.root / "plain"
        plain.mkdir()
        proc = refresh(self.toolkit, plain)
        self.assertEqual(proc.returncode, 2)

    def test_bad_toolkit_is_refused(self):
        proc = subprocess.run(
            [sys.executable, str(REFRESH), str(self.target),
             "--toolkit", str(self.root), "--no-sync"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 2)

    # -- sync never blocks -------------------------------------------------

    def test_offline_sync_proceeds_with_flag(self):
        sys.path.insert(0, str(TOOLS))
        try:
            import refresh as refresh_mod
            old = refresh_mod.CANONICAL_URLS
            refresh_mod.CANONICAL_URLS = ["http://127.0.0.1:1/nonexistent.git"]
            try:
                note = refresh_mod.sync_toolkit(self.toolkit)
            finally:
                refresh_mod.CANONICAL_URLS = old
        finally:
            sys.path.remove(str(TOOLS))
        self.assertIn("no canonical remote reachable", note)

    # -- bootstrap banner and offer ----------------------------------------

    def test_foreign_core_file_prints_banner_and_commands(self):
        (self.target / "AGENTS.md").write_text("# Mine\nforeign\n", newline="\n")
        commit_all(self.target, "foreign agents")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("ATTENTION: AGENTS.md was NOT replaced.", proc.stdout)
        self.assertIn("bootstrap", proc.stdout)
        # non-TTY: never asks, never hangs
        self.assertNotIn("Run bootstrap now?", proc.stdout)

    def test_clean_run_prints_no_banner(self):
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("ATTENTION", proc.stdout)

    def test_non_core_flag_prints_no_banner(self):
        refresh(self.toolkit, self.target)
        (self.target / ".claude" / "commands" / "tool.md").write_text(
            "my edited wrapper\n", newline="\n")
        commit_all(self.target, "edit tool")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("ATTENTION", proc.stdout)

    def _refresh_mod(self):
        sys.path.insert(0, str(TOOLS))
        self.addCleanup(sys.path.remove, str(TOOLS))
        import refresh as refresh_mod
        return refresh_mod

    def test_offer_launches_chosen_harness_with_prompt(self):
        mod = self._refresh_mod()
        seen = {}
        cands = [("fakecli", ["fakecli", "--prompt", "{prompt}"])]
        rc = mod.offer_bootstrap(cands, "do the bootstrap", self.target,
                                 input_fn=lambda _q: "1",
                                 launch_fn=lambda argv: seen.setdefault("argv", argv) and 0)
        self.assertEqual(seen["argv"], ["fakecli", "--prompt", "do the bootstrap"])

    def test_offer_declines_on_q_empty_junk_and_eof(self):
        mod = self._refresh_mod()
        cands = [("fakecli", ["fakecli", "{prompt}"])]
        boom = lambda argv: self.fail("must not launch")
        for answer in ("q", "", "no", "2", "0"):
            self.assertIsNone(mod.offer_bootstrap(
                cands, "p", self.target,
                input_fn=lambda _q, a=answer: a, launch_fn=boom))
        def raise_eof(_q):
            raise EOFError
        self.assertIsNone(mod.offer_bootstrap(
            cands, "p", self.target, input_fn=raise_eof, launch_fn=boom))

    def test_non_tty_commands_without_harness_points_at_procedure(self):
        mod = self._refresh_mod()
        text = mod.non_tty_commands([], "p", self.target, self.toolkit)
        self.assertIn(str(self.toolkit / "procedures" / "bootstrap.md"), text)


if __name__ == "__main__":
    unittest.main()
