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


class TestDriver(unittest.TestCase):
    def test_driver_hook_runs_before_verify_and_edits_count(self):
        # A driver that "fixes" the workspace (sets app.txt=FIXED) must make the verify
        # command pass, proving the driver runs after scaffold/setup and before verify.
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_git_oracle_fixture(Path(tmp))

            def fake_driver(workdir, fixture_dir, manifest, env_extra):
                (Path(workdir) / "app.txt").write_text("FIXED\n", encoding="utf-8")
                return {"driver": "fake", "exit": 0}

            r = run_fixture.score_fixture(fx, driver=fake_driver)
            self.assertTrue(r["functional_pass"], "verify should pass after the driver fixes it")
            self.assertEqual(r["driver"]["driver"], "fake")

    def test_no_driver_leaves_fixture_failing(self):
        # Same fixture without a driver stays red (nobody fixed it) — guards that the
        # driver hook, not something else, is what flips the result above.
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_git_oracle_fixture(Path(tmp))
            r = run_fixture.score_fixture(fx)
            self.assertFalse(r["functional_pass"])


class TestDriverModule(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
        import drivers
        self.drivers = drivers

    def test_read_task_prompt_strips_oracle_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            fxdir = Path(tmp)
            (fxdir / "TASK.md").write_text(
                "# T\nDo the thing.\n\n## Oracle\nverify: secret command\n", encoding="utf-8")
            prompt = self.drivers.read_task_prompt(fxdir, {"task": "TASK.md"})
            self.assertIn("Do the thing.", prompt)
            self.assertNotIn("secret command", prompt)
            self.assertNotIn("## Oracle", prompt)

    def test_get_driver_unknown_raises(self):
        with self.assertRaises(ValueError):
            self.drivers.get_driver("nope")

    def test_known_drivers_present(self):
        self.assertTrue(callable(self.drivers.get_driver("codex")))
        self.assertTrue(callable(self.drivers.get_driver("claude")))


class TestProfiles(unittest.TestCase):
    def test_none_overlays_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run_fixture.overlay_profile("none", Path(tmp)), [])

    def test_current_template_generated_from_product_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            wd = Path(tmp)
            overlaid = run_fixture.overlay_profile("current-template", wd)
            self.assertIn("AGENTS.md", overlaid)
            self.assertIn("CLAUDE.md", overlaid)
            self.assertIn("Prime Invariants", (wd / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertIn("@AGENTS.md", (wd / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_profile_hash_differs_between_none_and_current_template(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            none_h = run_fixture.overlaid_hash(Path(a), run_fixture.overlay_profile("none", Path(a)))
            ct_h = run_fixture.overlaid_hash(Path(b), run_fixture.overlay_profile("current-template", Path(b)))
            self.assertNotEqual(none_h, ct_h)


class TestRunMatrix(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))
        import run_trials
        self.rt = run_trials

    def _fixer(self, workdir, fixture_dir, manifest, env_extra):
        (Path(workdir) / "app.txt").write_text("FIXED\n", encoding="utf-8")
        return {"driver": "fake", "exit": 0}

    def test_matrix_with_driver_passes_all_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_git_oracle_fixture(Path(tmp))
            res = self.rt.run_matrix([fx], ["none"], 2, self._fixer, record=False)
            agg = self.rt.summarize(res)
            self.assertEqual(agg[("oracle", "none")]["passes"], 2)
            self.assertEqual(agg[("oracle", "none")]["pass_rate"], 1.0)

    def test_matrix_without_driver_fails_all_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = _make_git_oracle_fixture(Path(tmp))
            res = self.rt.run_matrix([fx], ["none"], 2, None, record=False)
            self.assertEqual(self.rt.summarize(res)[("oracle", "none")]["passes"], 0)


if __name__ == "__main__":
    unittest.main()
