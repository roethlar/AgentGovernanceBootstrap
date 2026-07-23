"""Behavioral tests for tools/refresh.py against a hermetic fixture toolkit.

Each test builds a throwaway toolkit repo (mini shipped set) and a throwaway
target repo, then runs refresh.py end-to-end via subprocess (or in-process
for the sync unit test). No test touches the real toolkit's shipped set or
any real remote.
"""

import contextlib
import hashlib
import io
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
        "schema": 1,
        "artifacts": [
            {"source": "templates/AGENTS.template.md", "target": "AGENTS.md",
             "class": "replace-whole", "formerly": [nhash(OLD_AGENTS)]},
            {"source": "templates/commands/claude/tool.md", "target": ".claude/commands/tool.md",
             "class": "replace", "formerly": [nhash(OLD_TOOL)]},
            {"source": "templates/hooks/claude/settings.json", "target": ".claude/settings.json",
             "class": "replace", "formerly": [nhash(OLD_SETTINGS)]},
            {"source": "templates/shims/CLAUDE.template.md", "target": "CLAUDE.md",
             "class": "replace", "formerly": []},
        ],
        "retired": [
            {"target": ".claude/old-hook.py", "formerly": [nhash(OLD_HOOK)]},
            {"target": ".agents/generated.json", "formerly": []},
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

    def test_diverged_artifact_is_restored_with_drift_report(self):
        # Strict converge (owner ruling 2026-07-16): content matching no
        # shipped version is drift, whoever wrote it - restored, and the
        # report names the commits that introduced it.
        (self.target / ".claude" / "commands").mkdir(parents=True)
        (self.target / ".claude" / "commands" / "tool.md").write_text("my custom wrapper\n", newline="\n")
        commit_all(self.target, "custom wrapper")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self.target / ".claude" / "commands" / "tool.md").read_text(), CUR_TOOL)
        self.assertIn("restored: .claude/commands/tool.md", proc.stdout)
        self.assertIn("DRIFT", proc.stdout)
        self.assertIn("custom wrapper", proc.stdout)  # introducing commit subject

    # -- replace-whole (AGENTS.md) --------------------------------------

    def test_formerly_shipped_agents_md_is_replaced(self):
        (self.target / "AGENTS.md").write_text(OLD_AGENTS, newline="\n")
        commit_all(self.target, "old agents")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual((self.target / "AGENTS.md").read_text(), CUR_AGENTS)

    def test_foreign_agents_md_is_flagged_never_replaced(self):
        # No committed version of this AGENTS.md ever matched a shipped
        # hash: a foreign governance file is a migration, not drift.
        (self.target / "AGENTS.md").write_text("# My own house rules\n", newline="\n")
        commit_all(self.target, "foreign agents")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual((self.target / "AGENTS.md").read_text(), "# My own house rules\n")
        self.assertIn("FLAG AGENTS.md", proc.stdout)
        self.assertIn("bootstrap procedure", proc.stdout)

    def test_hand_edited_agents_md_in_governed_repo_is_restored(self):
        # Git history holds a formerly-shipped version, so the repo was
        # governed: the divergence is drift and converges back - no
        # foreign-file flag, no bootstrap banner.
        (self.target / "AGENTS.md").write_text(OLD_AGENTS, newline="\n")
        commit_all(self.target, "governed agents")
        (self.target / "AGENTS.md").write_text("# Agent Guidance\nhijacked body\n", newline="\n")
        commit_all(self.target, "hijack edit")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self.target / "AGENTS.md").read_text(), CUR_AGENTS)
        self.assertIn("restored: AGENTS.md", proc.stdout)
        self.assertIn("hijack edit", proc.stdout)
        self.assertNotIn("ATTENTION", proc.stdout)

    def test_uncommitted_diverged_artifact_refuses_before_restore(self):
        # The restore path never destroys the only copy: uncommitted
        # divergence hits the dirty-tree refusal and nothing changes.
        refresh(self.toolkit, self.target)
        (self.target / ".claude" / "commands" / "tool.md").write_text(
            "uncommitted agent edit\n", newline="\n")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 3, proc.stderr)
        self.assertIn("refusing", proc.stderr)
        self.assertEqual((self.target / ".claude" / "commands" / "tool.md").read_text(),
                         "uncommitted agent edit\n")

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

    def test_manifest_missing_schema_refused(self):
        self._mutate_manifest(lambda d: d.pop("schema"))
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("schema", proc.stderr)
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_manifest_duplicate_target_refused(self):
        self._mutate_manifest(
            lambda d: d["artifacts"].append(dict(d["artifacts"][0])))
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("duplicate", proc.stderr)

    def test_manifest_target_in_both_artifacts_and_retired_refused(self):
        # A path in both artifacts and retired would be installed (write) then
        # removed (unlink) in the same run: the shipped file gets deleted and
        # the deletion committed fleet-wide. Validation must catch the overlap
        # before any write. The target repo already has the current core file,
        # so without the guard the retired-branch removal deletes it.
        (self.target / "AGENTS.md").write_text(CUR_AGENTS, newline="\n")
        commit_all(self.target, "current agents present")
        self._mutate_manifest(lambda d: d["retired"].append(
            {"target": "AGENTS.md", "formerly": [nhash(CUR_AGENTS)]}))
        n = len(self.commits())
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("both artifacts and retired", proc.stderr)
        self.assertEqual((self.target / "AGENTS.md").read_text(), CUR_AGENTS)
        self.assertEqual(len(self.commits()), n)

    def test_lint_exempts_machines_md_as_create_on_first_use(self):
        # .agents/machines.md is a designated create-on-first-use home
        # (the per-machine facts file): its absence in a fresh repo is
        # expected, never a dead reference.
        (self.target / ".agents").mkdir()
        (self.target / ".agents" / "state.md").write_text(
            "machine facts live in `.agents/machines.md`\n", newline="\n")
        commit_all(self.target, "state pointer")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("references missing path `.agents/machines.md`",
                         proc.stdout)

    def test_lint_exempts_harness_session_cache_as_machine_local(self):
        # .agents/review/harnesses.local.json is the machine-local,
        # gitignored reviewer-tier session cache (review-economy plan,
        # 2026-07-17): prose may name it, but it never exists in a
        # committed tree — same class as .agents/machines.md.
        (self.target / ".agents").mkdir()
        (self.target / ".agents" / "state.md").write_text(
            "tier probes cached in `.agents/review/harnesses.local.json`\n",
            newline="\n")
        commit_all(self.target, "state pointer")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn(
            "references missing path `.agents/review/harnesses.local.json`",
            proc.stdout)

    # -- plan/apply protocol ----------------------------------------------

    def test_plan_json_is_read_only_and_complete(self):
        out = self.root / "plan.json"
        before = run_git(self.target, "rev-parse", "HEAD").strip()
        proc = refresh(self.toolkit, self.target, "--plan-json", str(out))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("read-only", proc.stdout)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertEqual(run_git(self.target, "rev-parse", "HEAD").strip(), before)
        self.assertEqual(run_git(self.target, "status", "--porcelain"), "")
        rec = json.loads(out.read_text())
        for key in ("schema", "toolkit_sha", "toolkit_dirty", "manifest_digest",
                    "target_head", "installs", "updates", "restores", "drift",
                    "removes", "gitignore_repairs", "flags", "staged_paths",
                    "digest"):
            self.assertIn(key, rec)
        self.assertTrue(any(e["target"] == "AGENTS.md" for e in rec["installs"]))
        self.assertEqual(rec["target_head"], before)

    def test_plan_digest_stable_then_content_sensitive(self):
        out1, out2, out3 = (self.root / n for n in ("p1.json", "p2.json", "p3.json"))
        refresh(self.toolkit, self.target, "--plan-json", str(out1))
        refresh(self.toolkit, self.target, "--plan-json", str(out2))
        d1 = json.loads(out1.read_text())["digest"]
        self.assertEqual(d1, json.loads(out2.read_text())["digest"])
        with open(str(self.toolkit / "templates" / "AGENTS.template.md"), "a",
                  newline="\n") as f:
            f.write("changed\n")
        refresh(self.toolkit, self.target, "--plan-json", str(out3))
        self.assertNotEqual(d1, json.loads(out3.read_text())["digest"])

    def test_apply_reproduces_the_planned_operation(self):
        out = self.root / "plan.json"
        refresh(self.toolkit, self.target, "--plan-json", str(out))
        proc = refresh(self.toolkit, self.target, "--apply", str(out))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self.target / "AGENTS.md").read_text(), CUR_AGENTS)
        rec = json.loads(out.read_text())
        committed = run_git(self.target, "show", "--name-only",
                            "--format=", "HEAD").split()
        self.assertEqual(sorted(committed), sorted(rec["staged_paths"]))
        body = run_git(self.target, "log", "-1", "--format=%B")
        self.assertIn("toolkit-sha: " + rec["toolkit_sha"], body)
        self.assertIn("plan-digest: " + rec["digest"], body)

    def test_apply_refuses_after_target_moved(self):
        out = self.root / "plan.json"
        refresh(self.toolkit, self.target, "--plan-json", str(out))
        (self.target / "later.txt").write_text("x\n", newline="\n")
        commit_all(self.target, "moved on")
        proc = refresh(self.toolkit, self.target, "--apply", str(out))
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("target_head", proc.stderr)
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_apply_refuses_after_toolkit_content_changed(self):
        out = self.root / "plan.json"
        refresh(self.toolkit, self.target, "--plan-json", str(out))
        with open(str(self.toolkit / "templates" / "AGENTS.template.md"), "a",
                  newline="\n") as f:
            f.write("changed after approval\n")
        proc = refresh(self.toolkit, self.target, "--apply", str(out))
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_apply_stage_only_stages_without_commit(self):
        out = self.root / "plan.json"
        refresh(self.toolkit, self.target, "--plan-json", str(out))
        n = len(self.commits())
        proc = refresh(self.toolkit, self.target, "--apply", str(out), "--stage-only")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(self.commits()), n)
        staged = run_git(self.target, "diff", "--cached", "--name-only").split()
        self.assertIn("AGENTS.md", staged)

    # -- apply crash safety (mid-loop failure never half-commits) ---------

    def _run_main_inprocess(self, mod, *extra):
        argv = [str(self.target), "--toolkit", str(self.toolkit), "--no-sync",
                *extra]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_apply_oserror_is_caught_not_crashed(self):
        # apply_plan raising OSError mid-loop is caught alike RuntimeError: a
        # clean exit-4 refusal, no traceback, no commit.
        mod = self._refresh_mod()
        orig = mod.apply_plan
        self.addCleanup(setattr, mod, "apply_plan", orig)
        def boom(*_a, **_k):
            raise OSError("disk full mid-apply")
        mod.apply_plan = boom
        n = len(self.commits())
        rc, _out, err = self._run_main_inprocess(mod)
        self.assertEqual(rc, 4, err)
        self.assertIn("refusing unsafe write", err)
        self.assertEqual(len(self.commits()), n)

    def test_staged_set_gap_refuses_commit(self):
        # Simulate a partial apply: files land on disk but never reach the
        # index. The crash check must refuse before committing rather than
        # letting the next run misread them as current.
        mod = self._refresh_mod()
        orig = mod.stage
        self.addCleanup(setattr, mod, "stage", orig)
        mod.stage = lambda *_a, **_k: None
        n = len(self.commits())
        rc, _out, err = self._run_main_inprocess(mod)
        self.assertEqual(rc, 4, err)
        self.assertIn("staged set does not cover the plan", err)
        self.assertEqual(len(self.commits()), n)

    def test_crash_check_is_exempt_in_stage_only(self):
        # The crash check guards the commit; --stage-only makes no commit (the
        # bootstrap flow does), so the same staged-set gap must not refuse.
        mod = self._refresh_mod()
        orig = mod.stage
        self.addCleanup(setattr, mod, "stage", orig)
        mod.stage = lambda *_a, **_k: None
        n = len(self.commits())
        rc, out, err = self._run_main_inprocess(mod, "--stage-only")
        self.assertEqual(rc, 0, err)
        self.assertEqual(len(self.commits()), n)
        self.assertIn("staged only", out)

    def test_dirty_toolkit_notes_default_mode_and_refuses_apply(self):
        with open(str(self.toolkit / "templates" / "shims" / "CLAUDE.template.md"),
                  "a", newline="\n") as f:
            f.write("uncommitted\n")
        out = self.root / "plan.json"
        refresh(self.toolkit, self.target, "--plan-json", str(out))
        self.assertTrue(json.loads(out.read_text())["toolkit_dirty"])
        proc = refresh(self.toolkit, self.target, "--apply", str(out))
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("dirty", proc.stderr)
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("toolkit tree is dirty", proc.stdout)

    def test_lint_allow_marker_suppresses_same_line_only(self):
        (self.target / ".agents").mkdir()
        (self.target / ".agents" / "state.md").write_text(
            "see `made/up-path.md` <!-- lint: allow -->\n"
            "and `also/missing.md`\n", newline="\n")
        commit_all(self.target, "state with marker")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("made/up-path.md", proc.stdout)
        self.assertIn("references missing path `also/missing.md`", proc.stdout)

    def test_render_cmd_per_platform(self):
        sys.path.insert(0, str(TOOLS))
        self.addCleanup(sys.path.remove, str(TOOLS))
        import refresh as refresh_mod
        argv = ["claude", "read the file", "--flag"]
        posix = refresh_mod.render_cmd(argv, windows=False)
        self.assertIn("'read the file'", posix)
        win = refresh_mod.render_cmd(argv, windows=True)
        self.assertIn('"read the file"', win)

    def test_maybe_reexec_runs_new_runner_once(self):
        sys.path.insert(0, str(TOOLS))
        self.addCleanup(sys.path.remove, str(TOOLS))
        import refresh as refresh_mod
        calls = []
        env = {}
        refresh_mod.maybe_reexec("aaa", "bbb", environ=env,
                                 execv_fn=lambda exe, argv: calls.append(argv),
                                 script_argv=["/repo", "--stage-only"])
        self.assertEqual(len(calls), 1)
        self.assertIn("--no-sync", calls[0])
        self.assertIn("--stage-only", calls[0])
        self.assertEqual(env.get("AGB_REFRESH_REEXEC"), "1")
        # same head: no re-exec; marker set: no second re-exec even on change
        self.assertFalse(refresh_mod.maybe_reexec(
            "aaa", "aaa", environ={}, execv_fn=lambda *a: calls.append(a)))
        self.assertFalse(refresh_mod.maybe_reexec(
            "aaa", "bbb", environ=env, execv_fn=lambda *a: calls.append(a)))
        self.assertEqual(len(calls), 1)

    # -- equivalence boundary (a historical hash never widens it) --------

    def test_formerly_containing_current_hash_does_not_widen_boundary(self):
        # Record the CURRENT wrapper content's hash in formerly[] (the
        # real manifest has this overlap), then present the current
        # content plus one extra trailing newline: drift-restored, never
        # reported as a clean "updated" (M1 report honesty).
        self._mutate_manifest(lambda d: [
            a["formerly"].append(nhash(CUR_TOOL))
            for a in d["artifacts"] if a["target"].endswith("tool.md")])
        (self.target / ".claude" / "commands").mkdir(parents=True)
        (self.target / ".claude" / "commands" / "tool.md").write_text(
            CUR_TOOL + "\n", newline="\n")
        commit_all(self.target, "extra trailing newline")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("restored: .claude/commands/tool.md", proc.stdout)
        self.assertNotIn("updated: .claude/commands/tool.md", proc.stdout)
        self.assertEqual(
            (self.target / ".claude" / "commands" / "tool.md").read_text(),
            CUR_TOOL)

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

    def test_second_trailing_newline_is_drift_and_restored(self):
        # Equivalence stops at ONE trailing newline: a second one is a real
        # divergence - restored via the drift path, never a quiet update.
        (self.target / ".claude" / "commands").mkdir(parents=True)
        (self.target / ".claude" / "commands" / "tool.md").write_bytes(CUR_TOOL.encode() + b"\n")
        commit_all(self.target, "double final newline")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("restored: .claude/commands/tool.md", proc.stdout)
        self.assertNotIn("updated: .claude/commands/tool.md", proc.stdout)
        self.assertEqual((self.target / ".claude" / "commands" / "tool.md").read_bytes(),
                         CUR_TOOL.encode())

    # -- retired ---------------------------------------------------------

    def test_retired_artifact_matching_formerly_shipped_is_removed(self):
        (self.target / ".claude").mkdir()
        (self.target / ".claude" / "old-hook.py").write_text(OLD_HOOK, newline="\n")
        commit_all(self.target, "old hook")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertFalse((self.target / ".claude" / "old-hook.py").exists())
        self.assertIn("removed: .claude/old-hook.py", proc.stdout)

    def test_modified_retired_artifact_is_removed_with_drift_report(self):
        (self.target / ".claude").mkdir()
        (self.target / ".claude" / "old-hook.py").write_text("customized hook\n", newline="\n")
        commit_all(self.target, "custom old hook")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((self.target / ".claude" / "old-hook.py").exists())
        self.assertIn("removed: .claude/old-hook.py", proc.stdout)
        self.assertIn("DRIFT", proc.stdout)
        self.assertIn("custom old hook", proc.stdout)

    def test_ignored_untracked_retired_file_refuses_not_deletes(self):
        # An ignored file never shows in `status --porcelain`, but deleting
        # it would destroy content git holds nowhere. Refuse instead.
        (self.target / ".gitignore").write_text("old-hook.py\n", newline="\n")
        commit_all(self.target, "ignore old hook")
        (self.target / ".claude").mkdir()
        (self.target / ".claude" / "old-hook.py").write_text("precious local state\n", newline="\n")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 3, proc.stderr)
        self.assertIn("refusing", proc.stderr)
        self.assertEqual((self.target / ".claude" / "old-hook.py").read_text(),
                         "precious local state\n")

    def test_retired_file_renamed_into_new_artifact_verifies_and_commits(self):
        # A retired file whose successor artifact has near-identical content
        # (reviewloop.md -> codereview.md) triggers git rename detection; the
        # post-commit verification must not read the collapsed rename line as
        # a plan mismatch.
        self._mutate_manifest(lambda d: d["retired"].append(
            {"target": ".claude/commands/old-tool.md",
             "formerly": [nhash(CUR_TOOL)]}))
        (self.target / ".claude" / "commands").mkdir(parents=True)
        (self.target / ".claude" / "commands" / "old-tool.md").write_text(
            CUR_TOOL, newline="\n")
        commit_all(self.target, "old tool present")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("does not match the plan", proc.stdout + proc.stderr)
        self.assertFalse((self.target / ".claude" / "commands" / "old-tool.md").exists())
        committed = run_git(self.target, "show", "--no-renames", "--name-only",
                            "--format=", "HEAD").split()
        self.assertIn(".claude/commands/old-tool.md", committed)
        self.assertIn(".claude/commands/tool.md", committed)

    def test_retired_generated_file_any_content_is_removed(self):
        # Empty formerly[] (generated per-repo, no hash can ever match):
        # still converges to absent, reported as drift.
        (self.target / ".agents").mkdir()
        (self.target / ".agents" / "generated.json").write_text("{\"repo\": \"specific\"}\n", newline="\n")
        commit_all(self.target, "generated artifact")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((self.target / ".agents" / "generated.json").exists())
        self.assertIn("removed: .agents/generated.json", proc.stdout)
        self.assertIn("DRIFT", proc.stdout)

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

    def test_non_core_drift_prints_no_banner(self):
        refresh(self.toolkit, self.target)
        (self.target / ".claude" / "commands" / "tool.md").write_text(
            "my edited wrapper\n", newline="\n")
        commit_all(self.target, "edit tool")
        proc = refresh(self.toolkit, self.target)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("restored: .claude/commands/tool.md", proc.stdout)
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


class GuidanceLintBaselineTests(unittest.TestCase):
    """This repo's own .agents/*.md files lint clean at warn level, so the
    next real LINT warning is signal, not noise. Legitimate illustrative or
    historical references carry the same-line 'lint: allow' marker."""

    def test_this_repos_agents_files_have_zero_warn_findings(self):
        sys.path.insert(0, str(TOOLS))
        self.addCleanup(sys.path.remove, str(TOOLS))
        import refresh as refresh_mod
        warns = [f for f in refresh_mod.lint_governance(TOOLS.parent)
                 if f[2] == "warn"]
        self.assertEqual([], warns)


class RealManifestEquivalenceTests(unittest.TestCase):
    """Regression for the real shipped set: wherever a current source's
    own hash sits in its formerly[] list, current-plus-an-extra-trailing-
    newline must classify as drift (restore), never as a clean update."""

    def test_overlapping_artifacts_restore_not_update(self):
        sys.path.insert(0, str(TOOLS))
        self.addCleanup(sys.path.remove, str(TOOLS))
        import refresh as refresh_mod
        toolkit = TOOLS.parent
        shipped = refresh_mod.load_shipped_set(toolkit)
        overlapping = [
            a for a in shipped["artifacts"]
            if refresh_mod.candidate_hashes((toolkit / a["source"]).read_bytes())
            & set(a.get("formerly", []))]
        if not overlapping:
            self.skipTest("no current/formerly hash overlap in the manifest")
        with tempfile.TemporaryDirectory() as tmp:
            for art in overlapping:
                target_repo = Path(tmp) / Path(art["target"]).name
                dest = target_repo / art["target"]
                dest.parent.mkdir(parents=True)
                src_bytes = (toolkit / art["source"]).read_bytes()
                dest.write_bytes(src_bytes + b"\n")
                plan = refresh_mod.classify(
                    target_repo, toolkit, {"artifacts": [art]})
                self.assertEqual([], plan.update, art["target"])
                if art["class"] == "replace-whole":
                    # No governed git history in the fixture: foreign, flagged.
                    self.assertEqual([art["target"]],
                                     [t for t, _ in plan.flags], art["target"])
                else:
                    self.assertEqual([], plan.flags, art["target"])
                    self.assertEqual([art["target"]],
                                     [t for t, _ in plan.restore], art["target"])


if __name__ == "__main__":
    unittest.main()
