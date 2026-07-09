"""Behavioral tests for tools/refresh.py against a hermetic fixture toolkit.

Each test builds a throwaway toolkit repo (mini shipped set) and a throwaway
target repo, then runs refresh.py end-to-end via subprocess (or in-process
for the sync unit test). No test touches the real toolkit's shipped set or
any real remote.
"""

import hashlib
import json
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
    (tk / "tools").mkdir()
    (tk / "templates" / "AGENTS.template.md").write_text(CUR_AGENTS, newline="\n")
    (tk / "templates" / "commands" / "claude" / "tool.md").write_text(CUR_TOOL, newline="\n")
    (tk / "templates" / "hooks" / "claude" / "settings.json").write_text(CUR_SETTINGS, newline="\n")
    shipped = {
        "artifacts": [
            {"source": "templates/AGENTS.template.md", "target": "AGENTS.md",
             "class": "replace-whole", "formerly": [nhash(OLD_AGENTS)]},
            {"source": "templates/commands/claude/tool.md", "target": ".claude/commands/tool.md",
             "class": "replace-if-unmodified", "formerly": [nhash(OLD_TOOL)]},
            {"source": "templates/hooks/claude/settings.json", "target": ".claude/settings.json",
             "class": "replace-if-unmodified", "formerly": [nhash(OLD_SETTINGS)]},
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
        capture_output=True, text=True, encoding="utf-8")


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


if __name__ == "__main__":
    unittest.main()
