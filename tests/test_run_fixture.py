"""Tests for tools/run_fixture.py. Run from repo root:
    python3 -m unittest discover -s tests -v

These exercise the language-agnostic scoring core hermetically (source=None fixtures
with inline files and trivial verify commands), so no real source repo or toolchain is
needed to prove the scorer classifies pass/fail and short-circuits on setup failure.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import run_fixture  # noqa: E402


def _make_fixture(tmp: Path, manifest: dict, files: dict[str, str] | None = None) -> Path:
    fx = tmp / "fx"
    fx.mkdir()
    if files:
        (fx / "files").mkdir()
        for name, content in files.items():
            (fx / "files" / name).write_text(content, encoding="utf-8")
        manifest.setdefault("files", "files")
    (fx / "fixture.json").write_text(json.dumps(manifest), encoding="utf-8")
    return fx


class TestScoring(unittest.TestCase):
    def test_verify_exit_zero_is_functional_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_fixture(Path(tmp), {
                "id": "pass", "language": "python", "source": None,
                "verify": "python3 -c \"import sys; sys.exit(0)\"",
            })
            r = run_fixture.score_fixture(fx)
            self.assertEqual(r["verify_exit"], 0)
            self.assertTrue(r["functional_pass"])

    def test_verify_nonzero_is_functional_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_fixture(Path(tmp), {
                "id": "fail", "language": "python", "source": None,
                "verify": "python3 -c \"import sys; sys.exit(1)\"",
            })
            r = run_fixture.score_fixture(fx)
            self.assertEqual(r["verify_exit"], 1)
            self.assertFalse(r["functional_pass"])

    def test_inline_files_are_scaffolded(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_fixture(Path(tmp), {
                "id": "files", "language": "shell", "source": None,
                "verify": "test -f marker.txt",
            }, files={"marker.txt": "hi"})
            r = run_fixture.score_fixture(fx)
            self.assertTrue(r["functional_pass"], "inline file should be present in workdir")

    def test_setup_failure_short_circuits_before_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_fixture(Path(tmp), {
                "id": "setupfail", "language": "shell", "source": None,
                "setup": ["false"],
                "verify": "python3 -c \"import sys; sys.exit(0)\"",
            })
            r = run_fixture.score_fixture(fx)
            self.assertFalse(r["setup_ok"])
            self.assertFalse(r["functional_pass"])
            self.assertIsNone(r["verify_exit"], "verify must not run after setup failure")

    def test_missing_verify_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_fixture(Path(tmp), {"id": "noverify", "source": None, "verify": ""})
            with self.assertRaises(ValueError):
                run_fixture.score_fixture(fx)


def _git(args: list[str], cwd: Path) -> str:
    import subprocess
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}
    import os
    e = dict(os.environ); e.update(env)
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True,
                          text=True, env=e).stdout.strip()


def _make_git_oracle_fixture(tmp: Path, verify: str = "sh check.sh",
                             setup: list[str] | None = None) -> Path:
    """Build a tiny git source repo with a real bug→fix pair, plus a fixture that
    references it. base: app.txt='broken'. fix-commit: adds check.sh (greps app.txt
    for FIXED) and sets app.txt='FIXED'. test_patch=check.sh, solution_patch=app.txt."""
    repo = tmp / "src"
    repo.mkdir()
    _git(["init", "-q"], repo)
    (repo / "app.txt").write_text("broken\n", encoding="utf-8")
    _git(["add", "-A"], repo)
    _git(["commit", "-q", "-m", "base"], repo)
    base = _git(["rev-parse", "HEAD"], repo)
    (repo / "check.sh").write_text("grep -q FIXED app.txt\n", encoding="utf-8")
    (repo / "app.txt").write_text("FIXED\n", encoding="utf-8")
    _git(["add", "-A"], repo)
    _git(["commit", "-q", "-m", "fix"], repo)
    fix_commit = _git(["rev-parse", "HEAD"], repo)
    _git(["checkout", "-q", base], repo)

    fx = tmp / "fx"
    fx.mkdir()
    # Metadata only: SHAs + paths, no diff text vendored into the fixture.
    (fx / "fixture.json").write_text(json.dumps({
        "id": "oracle", "language": "shell", "kind": "gold",
        "source": {"repo_path": str(repo), "base_commit": base, "fix_commit": fix_commit},
        "test_paths": ["check.sh"], "solution_paths": ["app.txt"],
        "setup": setup or [],
        "verify": verify,
    }), encoding="utf-8")
    return fx


class TestOracle(unittest.TestCase):
    def test_valid_oracle_broken_fails_fixed_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_git_oracle_fixture(Path(tmp))
            o = run_fixture.check_oracle(fx)
            self.assertTrue(o["broken_fails"], "test must fail on the parent state")
            self.assertTrue(o["fixed_passes"], "test must pass once the solution is applied")
            self.assertTrue(o["oracle_valid"])

    def test_oracle_invalid_when_test_passes_without_fix(self):
        # verify='true' always passes, so the "broken" state does not fail -> no oracle.
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_git_oracle_fixture(Path(tmp), verify="true")
            o = run_fixture.check_oracle(fx)
            self.assertFalse(o["broken_fails"])
            self.assertFalse(o["oracle_valid"])

    def test_oracle_invalid_when_broken_fails_only_in_setup(self):
        # RF-001 regression: if the broken state fails in SETUP (verify never runs),
        # that is not a valid oracle failure. verify='true' always passes; setup
        # 'grep -q FIXED app.txt' fails on the parent (app.txt='broken') and passes
        # once the solution sets app.txt='FIXED'. The verify command never
        # discriminates, so the oracle must be rejected.
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_git_oracle_fixture(Path(tmp), verify="true",
                                          setup=["grep -q FIXED app.txt"])
            o = run_fixture.check_oracle(fx)
            self.assertFalse(o["broken_setup_ok"])
            self.assertFalse(o["broken_fails"])
            self.assertFalse(o["oracle_valid"])

    def test_test_patch_makes_verify_fail_on_parent(self):
        # A plain score (no solution) of a gold fixture should fail: the injected test
        # is red against the unfixed parent source.
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_git_oracle_fixture(Path(tmp))
            r = run_fixture.score_fixture(fx)
            self.assertFalse(r["functional_pass"])


if __name__ == "__main__":
    unittest.main()
