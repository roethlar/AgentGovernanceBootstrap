"""Tests for tools/new-project.py (Stage 1, owner-surface redesign).

Hermetic: temp target dirs, real toolkit templates via the real repo, stub
harness CLIs on a temp PATH. The agent-phase offer is driven through
function seams (input_fn / launch_fn), never a real TTY.
"""
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "new-project.py"
LAUNCHER = ROOT / "tools" / "new-project"

sys.path.insert(0, str(ROOT / "tools"))
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("new_project", SCRIPT)
new_project = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(new_project)


def run_script(target, *extra, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target), *extra],
        capture_output=True, text=True, env=env)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


class NewProjectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.target = self.base / "proj"

    def test_creates_dir_git_init_and_stages_shipped_set(self):
        proc = run_script(self.target)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertTrue((self.target / ".git").is_dir())
        # shipped set present in the worktree
        self.assertTrue((self.target / "AGENTS.md").exists())
        self.assertTrue((self.target / ".agents" / "playbooks" / "codereview.md").exists())
        # staged (in the index) but not committed
        staged = git(self.target, "ls-files", "--", "AGENTS.md")
        self.assertIn("AGENTS.md", staged.stdout)
        log = git(self.target, "log", "--oneline")
        self.assertEqual("", log.stdout.strip())

    def test_hint_lands_in_printed_launch_lines(self):
        bindir = self.base / "bin"
        bindir.mkdir()
        stub = bindir / "claude"
        stub.write_text("#!/bin/sh\nexit 0\n")
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        env = dict(os.environ)
        env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
        proc = run_script(self.target, "a", "markdown", "todo", "CLI", env=env)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("claude", proc.stdout)
        self.assertIn("a markdown todo CLI", proc.stdout)
        self.assertIn("setup.md", proc.stdout)

    def test_refuses_existing_governance(self):
        self.target.mkdir()
        (self.target / "AGENTS.md").write_text("foreign\n")
        proc = run_script(self.target)
        self.assertEqual(2, proc.returncode)
        self.assertIn("already has governance", proc.stderr)
        self.assertIn("refresh.py", proc.stderr)
        self.assertFalse((self.target / ".git").is_dir())

    def test_refuses_existing_agents_dir(self):
        self.target.mkdir()
        (self.target / ".agents").mkdir()
        proc = run_script(self.target)
        self.assertEqual(2, proc.returncode)
        self.assertIn("already has governance", proc.stderr)

    def test_no_harness_prints_procedure_path(self):
        empty = self.base / "empty-bin"
        empty.mkdir()
        env = dict(os.environ)
        env["PATH"] = str(empty) + os.pathsep + "/usr/bin" + os.pathsep + "/bin"
        proc = run_script(self.target, env=env)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("setup.md", proc.stdout)
        self.assertIn("no known harness CLI", proc.stdout)


class OfferLaunchTests(unittest.TestCase):
    """The TTY offer through its seams: never a real terminal."""

    def setUp(self):
        self.candidates = [("claude", ("claude", "{prompt}")),
                           ("codex", ("codex", "{prompt}"))]
        self.prompt = "KICKOFF"
        self.target = Path("/nonexistent")

    def launch(self, answers):
        launched = []
        it = iter(answers)
        code = new_project.offer_launch(
            self.candidates, self.prompt, self.target,
            input_fn=lambda _msg: next(it),
            launch_fn=lambda argv: launched.append(argv) or 0)
        return code, launched

    def test_valid_choice_launches_with_prompt(self):
        code, launched = self.launch(["2"])
        self.assertEqual(0, code)
        self.assertEqual([["codex", "KICKOFF"]], launched)

    def test_declines_on_q_empty_junk_out_of_range(self):
        for junk in ("q", "", "x", "0", "9"):
            code, launched = self.launch([junk])
            self.assertIsNone(code)
            self.assertEqual([], launched)

    def test_eof_declines(self):
        def eof(_msg):
            raise EOFError
        code = new_project.offer_launch(
            self.candidates, self.prompt, self.target, input_fn=eof)
        self.assertIsNone(code)


class LauncherTests(unittest.TestCase):
    def test_print_python_finds_a_310_or_better(self):
        proc = subprocess.run(["sh", str(LAUNCHER), "--print-python"],
                              capture_output=True, text=True)
        self.assertEqual(0, proc.returncode, proc.stderr)
        binary = proc.stdout.strip()
        ver = subprocess.run([binary, "-c",
                              "import sys; print(sys.version_info >= (3, 10))"],
                             capture_output=True, text=True)
        self.assertIn("True", ver.stdout)


if __name__ == "__main__":
    unittest.main()
