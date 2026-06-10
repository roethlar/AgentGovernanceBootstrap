"""Tests for tools/discover.py. Run from repo root:
    python3 -m unittest discover -s tests -v
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixtures  # noqa: E402


class TestCliExists(unittest.TestCase):
    def test_discover_runs_on_greenfield_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            manifest = fixtures.run_discover(repo)
            self.assertTrue(manifest["git"]["isGitRepository"])


class TestScratchRerun(unittest.TestCase):
    def test_rerun_from_scratch_copy_keeps_bootstrap_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            fixtures.run_discover(repo)
            scratch_script = repo / ".bootstrap-tmp" / "tools" / "discover.py"
            proc = subprocess.run(
                [sys.executable, str(scratch_script), str(repo)],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            manifest = json.loads(
                (repo / ".bootstrap-tmp" / "repo-discovery-manifest.json")
                .read_text(encoding="utf-8"))
            self.assertEqual(manifest["bootstrapRepoPath"],
                             str(fixtures.BOOTSTRAP_ROOT))


class TestManifestCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        base = Path(cls._tmp.name)
        cls.green = fixtures.make_greenfield_repo(base / "green")
        cls.gov = fixtures.make_governance_repo(base / "gov")
        cls.green_manifest = fixtures.run_discover(cls.green)
        cls.gov_manifest = fixtures.run_discover(cls.gov)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_routes(self):
        self.assertEqual(self.green_manifest["route"], "greenfield")
        self.assertEqual(self.gov_manifest["route"], "migration")

    def test_governance_markers_found(self):
        markers = self.gov_manifest["governanceMarkers"]
        for expected in ["AGENTS.md", "CLAUDE.md", "docs/STATE.md", "DEVLOG.md",
                         "docs/DECISIONS.md", ".claude/commands/catchup.md"]:
            self.assertIn(expected, markers)
        self.assertEqual(self.green_manifest["governanceMarkers"], [])

    def test_sensitive_path_flagged_and_not_suggested(self):
        flagged = [e["path"] for e in self.gov_manifest["likelySensitivePaths"]]
        self.assertIn("deploy/secrets.yaml", flagged)
        self.assertNotIn("deploy/secrets.yaml",
                         self.gov_manifest["suggestedReadPaths"])

    def test_tracked_files_complete(self):
        self.assertIn("crates/app/src/lib.rs", self.gov_manifest["trackedFiles"])
        self.assertEqual(self.gov_manifest["coverage"]["status"], "complete")

    def test_scratch_paths_never_in_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_governance_repo(Path(tmp) / "repo")
            fixtures.run_discover(repo)
            second = fixtures.run_discover(repo)  # re-run over existing scratch
            for key in ("trackedFiles", "untrackedFiles", "ignoredFiles"):
                for p in second[key]:
                    self.assertFalse(p.startswith(".bootstrap-tmp"), p)


class TestScratchOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        base = Path(cls._tmp.name)
        cls.green = fixtures.make_greenfield_repo(base / "green")
        cls.gov = fixtures.make_governance_repo(base / "gov")
        fixtures.run_discover(cls.green)
        fixtures.run_discover(cls.gov)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_scratch_is_self_ignored(self):
        gitignore = self.gov / ".bootstrap-tmp" / ".gitignore"
        self.assertEqual(gitignore.read_text(encoding="utf-8"), "*\n")

    def test_procedures_templates_and_script_copied(self):
        scratch = self.gov / ".bootstrap-tmp"
        for rel in ("procedures/bootstrap.md", "procedures/migration.md",
                    "procedures/verification.md", "procedures/harvest.md",
                    "templates/AGENTS.template.md",
                    "templates/governance-inventory.template.md",
                    "templates/harvest-report.template.md",
                    "templates/shims/CLAUDE.template.md",
                    "tools/discover.py"):
            self.assertTrue((scratch / rel).is_file(), rel)

    def test_start_here_routes_migration(self):
        text = (self.gov / ".bootstrap-tmp" / "START-HERE.md").read_text(
            encoding="utf-8")
        self.assertIn("**migration**", text)
        self.assertIn("procedures/migration.md", text)

    def test_start_here_routes_greenfield(self):
        text = (self.green / ".bootstrap-tmp" / "START-HERE.md").read_text(
            encoding="utf-8")
        self.assertIn("**greenfield**", text)
        self.assertIn("Greenfield workflow", text)

    def test_manifest_records_bootstrap_repo_path(self):
        manifest = fixtures.run_discover(self.green)
        self.assertEqual(manifest["bootstrapRepoPath"],
                         str(fixtures.BOOTSTRAP_ROOT))


class TestVerificationCandidates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        base = Path(cls._tmp.name)
        cls.green_manifest = fixtures.run_discover(
            fixtures.make_greenfield_repo(base / "green"))
        cls.gov_manifest = fixtures.run_discover(
            fixtures.make_governance_repo(base / "gov"))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def _commands(self, manifest):
        return [c["command"] for c in manifest["verificationCandidates"]]

    def test_npm_scripts_detected_with_prefix_filter(self):
        commands = self._commands(self.green_manifest)
        self.assertIn("npm run test", commands)
        self.assertIn("npm run lint", commands)
        self.assertNotIn("npm run deploy", commands)  # not a verification verb

    def test_makefile_targets_detected(self):
        commands = self._commands(self.green_manifest)
        self.assertIn("make test", commands)
        self.assertNotIn("make clean", commands)

    def test_cargo_workspace_detected(self):
        self.assertIn("cargo test --workspace", self._commands(self.gov_manifest))

    def test_sources_recorded(self):
        for c in self.green_manifest["verificationCandidates"]:
            self.assertTrue(c["source"])


class TestGoldenManifests(unittest.TestCase):
    def _check(self, builder, golden_name):
        golden_path = (Path(__file__).resolve().parent / "golden" / golden_name)
        golden = json.loads(golden_path.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            manifest = fixtures.run_discover(builder(Path(tmp) / "repo"))
        self.assertEqual(fixtures.normalize_manifest(manifest), golden,
                         f"Manifest drifted from tests/golden/{golden_name}. "
                         "If the change is intentional, run "
                         "python3 tests/regen_golden.py and review the diff.")

    def test_greenfield_matches_golden(self):
        self._check(fixtures.make_greenfield_repo, "greenfield-manifest.json")

    def test_governance_matches_golden(self):
        self._check(fixtures.make_governance_repo, "governance-manifest.json")


class TestUpdateRouteHeuristic(unittest.TestCase):
    def test_agents_dir_without_standard_layout_routes_migration(self):
        # The Blit case: a pre-existing .agents/ (e.g., workspace skills)
        # that is NOT this process's standard layout must not route "update".
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_governance_repo(Path(tmp) / "repo")
            skills = repo / ".agents" / "skills"
            skills.mkdir(parents=True)
            (skills / "catchup.md").write_text("Re-ground.\n", encoding="utf-8")
            fixtures._git(repo, "add", "-A")
            fixtures._git(repo, "commit", "-q", "-m", "add workspace skills")
            manifest = fixtures.run_discover(repo)
            self.assertEqual(manifest["route"], "migration")

    def test_standard_layout_routes_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_governance_repo(Path(tmp) / "repo")
            agents = repo / ".agents"
            agents.mkdir()
            (agents / "state.md").write_text("# Agent State\n", encoding="utf-8")
            fixtures._git(repo, "add", "-A")
            fixtures._git(repo, "commit", "-q", "-m", "adopt standard layout")
            manifest = fixtures.run_discover(repo)
            self.assertEqual(manifest["route"], "update")


if __name__ == "__main__":
    unittest.main()
