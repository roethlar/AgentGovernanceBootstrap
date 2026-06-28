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

    def test_agent_prompt_reads_prompt_file_and_requires_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            fxdir = Path(tmp)
            (fxdir / "PROMPT.md").write_text("Do the thing.\n", encoding="utf-8")
            self.assertEqual(self.drivers.agent_prompt(fxdir, {}), "Do the thing.")
        with tempfile.TemporaryDirectory() as tmp2:
            with self.assertRaises(FileNotFoundError):
                self.drivers.agent_prompt(Path(tmp2), {})

    def test_prompt_file_override_cannot_reselect_task_md(self):
        # PROMPT-FILE-BYPASS regression: a manifest prompt_file override must NOT be able
        # to point the agent prompt at provenance-bearing TASK.md.
        with tempfile.TemporaryDirectory() as tmp:
            fxdir = Path(tmp)
            (fxdir / "TASK.md").write_text("leak qbit-mobile ae748cd\n", encoding="utf-8")
            (fxdir / "PROMPT.md").write_text("Do the thing.\n", encoding="utf-8")
            prompt = self.drivers.agent_prompt(fxdir, {"prompt_file": "TASK.md"})
            self.assertEqual(prompt, "Do the thing.")
            self.assertNotIn("qbit-mobile", prompt)

    def test_gold_fixture_agent_prompt_has_no_provenance(self):
        # RF-DRIVER-PROMPT-FIXCOMMIT-LEAK regression: the agent-facing prompt must not
        # name the source repo or any commit SHA, or an agent could find the checkout on
        # disk and read the reference fix.
        fxdir = Path(__file__).resolve().parents[1] / "evals" / "fixtures" / "ts_qbit_confirmdelete_gold"
        manifest = json.loads((fxdir / "fixture.json").read_text())
        prompt = self.drivers.agent_prompt(fxdir, manifest)
        for leak in ("qbit-mobile", manifest["source"]["fix_commit"], manifest["source"]["base_commit"]):
            self.assertNotIn(leak, prompt, f"agent prompt leaks {leak!r}")

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

    def test_profile_copy_destination_escape_is_rejected(self):
        # RF-PROFILE-COPY-ESCAPES-WORKDIR regression.
        with tempfile.TemporaryDirectory() as profroot, tempfile.TemporaryDirectory() as wd:
            import run_fixture as rf
            orig = rf.PROFILES_DIR
            try:
                rf.PROFILES_DIR = Path(profroot)
                pdir = Path(profroot) / "evil"
                pdir.mkdir()
                (pdir / "profile.json").write_text(json.dumps(
                    {"copies": [{"from": "README.md", "to": "../escape.txt"}]}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    rf.overlay_profile("evil", Path(wd))
                self.assertFalse((Path(wd).parent / "escape.txt").exists())
            finally:
                rf.PROFILES_DIR = orig

    def test_profile_name_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as wd:
            with self.assertRaises(ValueError):
                run_fixture.overlay_profile("../../etc", Path(wd))

    def test_profile_symlink_source_is_rejected(self):
        # SYMLINK-SOURCE regression: a symlink in a profile dir must not pull outside
        # content into the workspace.
        import run_fixture as rf
        with tempfile.TemporaryDirectory() as profroot, tempfile.TemporaryDirectory() as wd, \
                tempfile.TemporaryDirectory() as outside:
            secret = Path(outside) / "secret.txt"
            secret.write_text("outside secret", encoding="utf-8")
            orig = rf.PROFILES_DIR
            try:
                rf.PROFILES_DIR = Path(profroot)
                pdir = Path(profroot) / "evil"
                pdir.mkdir()
                (pdir / "linked.txt").symlink_to(secret)
                with self.assertRaises(ValueError):
                    rf.overlay_profile("evil", Path(wd))
                self.assertFalse((Path(wd) / "linked.txt").exists())
            finally:
                rf.PROFILES_DIR = orig

    def test_symlinked_profile_json_rejected_before_any_copy(self):
        # SYMLINK-SOURCE-PROFILEJSON-PREFLIGHT regression: a symlinked profile.json must
        # be rejected before it is read/applied — no destination file created.
        import run_fixture as rf
        with tempfile.TemporaryDirectory() as profroot, tempfile.TemporaryDirectory() as wd, \
                tempfile.TemporaryDirectory() as outside:
            spec = Path(outside) / "real.json"
            spec.write_text(json.dumps({"copies": [{"from": "README.md", "to": "leaked.txt"}]}),
                            encoding="utf-8")
            orig = rf.PROFILES_DIR
            try:
                rf.PROFILES_DIR = Path(profroot)
                pdir = Path(profroot) / "evil"
                pdir.mkdir()
                (pdir / "profile.json").symlink_to(spec)
                with self.assertRaises(ValueError):
                    rf.overlay_profile("evil", Path(wd))
                self.assertFalse((Path(wd) / "leaked.txt").exists(), "no copy before rejection")
            finally:
                rf.PROFILES_DIR = orig

    def test_candidate_loop_first_concats_template_and_snippet(self):
        with tempfile.TemporaryDirectory() as tmp:
            wd = Path(tmp)
            overlaid = run_fixture.overlay_profile("candidate-loop-first", wd)
            self.assertIn("AGENTS.md", overlaid)
            self.assertIn("CLAUDE.md", overlaid)
            agents = (wd / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("Prime Invariants", agents)            # from the product template
            self.assertIn("Authorized execution mode", agents)   # from the candidate snippet
            self.assertFalse(any("_parts" in o for o in overlaid), "_parts must not be overlaid")
            self.assertFalse((wd / "_parts").exists())

    def test_candidate_differs_from_current_template(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            ct = run_fixture.overlaid_hash(Path(a), run_fixture.overlay_profile("current-template", Path(a)))
            cand = run_fixture.overlaid_hash(Path(b), run_fixture.overlay_profile("candidate-loop-first", Path(b)))
            self.assertNotEqual(ct, cand)

    def test_concat_part_escaping_repo_is_rejected(self):
        import run_fixture as rf
        with tempfile.TemporaryDirectory() as profroot, tempfile.TemporaryDirectory() as wd:
            orig = rf.PROFILES_DIR
            try:
                rf.PROFILES_DIR = Path(profroot)
                pdir = Path(profroot) / "evil"
                pdir.mkdir()
                (pdir / "profile.json").write_text(json.dumps(
                    {"concat": [{"to": "AGENTS.md", "parts": ["repo:../outside.md"]}]}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    rf.overlay_profile("evil", Path(wd))
            finally:
                rf.PROFILES_DIR = orig

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


class TestCopyDir(unittest.TestCase):
    def test_copy_dir_excludes_reference_solution(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as wd:
            s = Path(src)
            (s / "stub.py").write_text("def f(): pass", encoding="utf-8")
            (s / "sub").mkdir()
            (s / "sub" / "helper.py").write_text("x = 1", encoding="utf-8")
            (s / ".meta").mkdir()
            (s / ".meta" / "example.py").write_text("def f(): return 42  # REFERENCE", encoding="utf-8")
            run_fixture.scaffold({"source": {"copy_dir": str(s), "exclude": [".meta"]}}, Path(src), Path(wd))
            self.assertTrue((Path(wd) / "stub.py").exists())
            self.assertTrue((Path(wd) / "sub" / "helper.py").exists())
            self.assertFalse((Path(wd) / ".meta").exists(), "reference solution must be excluded")


class TestPolyglotFixture(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
        import polyglot_fixture
        self.pf = polyglot_fixture

    def _fake_exercise(self, bench: Path) -> None:
        ex = bench / "python" / "exercises" / "practice" / "foo"
        (ex / ".meta").mkdir(parents=True)
        (ex / ".docs").mkdir(parents=True)
        (ex / ".meta" / "config.json").write_text(json.dumps(
            {"files": {"solution": ["foo.py"], "test": ["foo_test.py"], "example": [".meta/example.py"]}}),
            encoding="utf-8")
        (ex / ".docs" / "instructions.md").write_text("Implement foo so it returns 42.", encoding="utf-8")
        (ex / ".meta" / "example.py").write_text("def foo(): return 42", encoding="utf-8")
        (ex / "foo.py").write_text("def foo(): pass", encoding="utf-8")
        (ex / "foo_test.py").write_text("import unittest", encoding="utf-8")

    def test_build_references_path_excludes_meta_and_prompts_instructions(self):
        with tempfile.TemporaryDirectory() as bench, tempfile.TemporaryDirectory() as out:
            self._fake_exercise(Path(bench))
            o = self.pf.build(bench, "python", "foo", Path(out) / "f")
            fx = json.loads((o / "fixture.json").read_text())
            self.assertEqual(fx["language"], "python")
            self.assertIn(".meta", fx["source"]["exclude"])
            self.assertTrue(fx["source"]["copy_dir"].endswith("/practice/foo"))
            prompt = (o / "PROMPT.md").read_text(encoding="utf-8")
            self.assertIn("Implement foo so it returns 42.", prompt)  # instructions
            self.assertIn("foo.py", prompt)                            # names the solution file
            self.assertNotIn("return 42\n", prompt)                    # but not the reference body
            self.assertNotIn("example.py", prompt)


class TestAggregate(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))
        import aggregate
        self.agg = aggregate

    def test_is_test_file_heuristic(self):
        for yes in ("test_duration.py", "src/components/ConfirmDeleteSheet.test.tsx",
                    "tests/PwshTokenCompressor.Tests.ps1", "foo_test.go"):
            self.assertTrue(self.agg.is_test_file(yes), yes)
        for no in ("duration.py", "src/components/ConfirmDeleteSheet.tsx",
                   "src/PwshTokenCompressor.psm1"):
            self.assertFalse(self.agg.is_test_file(no), no)

    def test_aggregate_counts_passes_and_tamper(self):
        results = [
            {"id": "f", "profile": "none", "functional_pass": True,
             "driver": {"changed_files": ["src/a.ts"]}, "duration_sec": 10},
            {"id": "f", "profile": "none", "functional_pass": False,
             "driver": {"changed_files": []}, "duration_sec": 20},
            {"id": "f", "profile": "current-template", "functional_pass": True,
             "driver": {"changed_files": ["test_a.py"]}, "duration_sec": 30},  # tampered
        ]
        agg = self.agg.aggregate(results)
        self.assertEqual(agg[("f", "none")]["passes"], 1)
        self.assertEqual(agg[("f", "none")]["pass_rate"], 0.5)
        self.assertEqual(agg[("f", "none")]["tampered"], 0)
        self.assertEqual(agg[("f", "current-template")]["tampered"], 1)


if __name__ == "__main__":
    unittest.main()
