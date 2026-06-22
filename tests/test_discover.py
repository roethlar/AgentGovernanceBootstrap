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
                    "tools/discover.py", "tools/manifest-schema.md"):
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


def _make_repo(path, files, branch="main"):
    path = Path(path)
    path.mkdir(parents=True)
    fixtures._git(path, "init", "-q", "-b", branch)
    for rel, content in files.items():
        fixtures._write(path, rel, content)
    fixtures._git(path, "add", "-A")
    fixtures._git(path, "commit", "-q", "-m", "fixture")
    return path


class TestCiMarkerValidation(unittest.TestCase):
    """F1 from the ExchangeAdminWeb pilot: a CI-named file outside any
    provider-executable path must never be presented as a CI marker, and
    branch-trigger mismatches must be surfaced."""

    def test_root_ci_yml_is_suspected_not_ci_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp) / "repo", {
                "README.md": "# x\n",
                "ci.yml": "on:\n  push:\n    branches: [main]\njobs: {}\n",
            }, branch="master")
            manifest = fixtures.run_discover(repo)
            self.assertEqual(manifest["ciMarkers"], [])
            self.assertEqual(manifest["suspectedMisplacedCi"], ["ci.yml"])
            self.assertEqual(manifest["ciBranchMismatches"], [
                {"path": "ci.yml", "branches": ["main"],
                 "currentBranch": "master"}])

    def test_executable_workflow_is_ci_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp) / "repo", {
                "README.md": "# x\n",
                ".github/workflows/build.yml":
                    "on:\n  push:\n    branches:\n      - main\n"
                    "      - 'release/**'\njobs: {}\n",
            })
            manifest = fixtures.run_discover(repo)
            self.assertEqual(manifest["ciMarkers"],
                             [".github/workflows/build.yml"])
            self.assertEqual(manifest["suspectedMisplacedCi"], [])
            # branch "main" matches the dash-list trigger: no mismatch
            self.assertEqual(manifest["ciBranchMismatches"], [])

    def test_workflow_without_branch_filter_never_mismatches(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp) / "repo", {
                ".github/workflows/build.yml": "on: push\njobs: {}\n",
            }, branch="master")
            manifest = fixtures.run_discover(repo)
            self.assertEqual(manifest["ciBranchMismatches"], [])

    def test_branch_glob_trigger_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp) / "repo", {
                ".github/workflows/r.yml":
                    "on:\n  push:\n    branches: ['release/*']\njobs: {}\n",
            }, branch="release/1.2")
            manifest = fixtures.run_discover(repo)
            self.assertEqual(manifest["ciBranchMismatches"], [])

    def test_packet_flags_misplaced_ci(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp) / "repo", {
                "ci.yml": "on:\n  push:\n    branches: [main]\njobs: {}\n",
            }, branch="master")
            fixtures.run_discover(repo)
            packet = (repo / ".bootstrap-tmp" / "bootstrap-review-packet.md"
                      ).read_text(encoding="utf-8")
            self.assertIn("not in a path any provider executes", packet)
            self.assertIn("likely inactive", packet)


class TestIgnoredDirectoryAnnotation(unittest.TestCase):
    """Queue item #5: when `git status --ignored` collapses a directory to a
    single `dir/` entry, the packet must not assert it 'cannot be committed' -
    that over-claims custody on future child paths. The collapse looks identical
    whether a rule ignores the directory (case A, children inherit) or only the
    current children are individually ignored (case B, a new non-matching child
    IS committable), so the packet stays neutral and points at `git check-ignore`
    on the exact final path."""

    def test_case_a_rule_on_directory_is_neutral(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp) / "repo", {
                "README.md": "# x\n",
                ".gitignore": ".claude/\n",
            })
            fixtures._write(repo, ".claude/commands/catchup.md", "ptr\n")
            manifest = fixtures.run_discover(repo)
            self.assertIn(".claude/", manifest["ignoredFiles"])
            packet = (repo / ".bootstrap-tmp" / "bootstrap-review-packet.md"
                      ).read_text(encoding="utf-8")
            self.assertIn("a directory git reports as ignored", packet)
            self.assertIn("git check-ignore", packet)
            self.assertNotIn("cannot be committed as-is", packet)

    def test_case_b_rule_on_child_is_neutral(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp) / "repo", {
                "README.md": "# x\n",
                ".gitignore": ".claude/settings.local.json\n",
            })
            fixtures._write(repo, ".claude/settings.local.json", "{}\n")
            manifest = fixtures.run_discover(repo)
            # git collapses the all-ignored dir even though no rule matches
            # `.claude/` itself (`git check-ignore .claude/` exits 1).
            self.assertIn(".claude/", manifest["ignoredFiles"])
            packet = (repo / ".bootstrap-tmp" / "bootstrap-review-packet.md"
                      ).read_text(encoding="utf-8")
            self.assertIn("a directory git reports as ignored", packet)
            self.assertIn("git check-ignore", packet)
            self.assertNotIn("cannot be committed as-is", packet)


class TestNonGitTarget(unittest.TestCase):
    """Finding 1 from the Send-MailMessageV2 pilot: a non-git target must
    never list files as tracked - that is a git-custody claim git cannot
    back - and the packet must state the non-git custody situation."""

    def test_files_listed_untracked_not_tracked(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir(parents=True)
            fixtures._write(repo, "ProblemStatement.txt", "replace cmdlet\n")
            manifest = fixtures.run_discover(repo)
            self.assertFalse(manifest["git"]["isGitRepository"])
            self.assertEqual(manifest["trackedFiles"], [])
            self.assertIn("ProblemStatement.txt", manifest["untrackedFiles"])

    def test_packet_states_non_git_custody(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir(parents=True)
            fixtures._write(repo, "README.md", "# x\n")
            fixtures.run_discover(repo)
            packet = (repo / ".bootstrap-tmp" / "bootstrap-review-packet.md"
                      ).read_text(encoding="utf-8")
            self.assertIn("Not a git repository", packet)
            self.assertIn("git init", packet)


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


class TestPrimeInvariantsTemplate(unittest.TestCase):
    def test_prime_block_present_and_copied(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            fixtures.run_discover(repo)
            tmpl = (repo / ".bootstrap-tmp" / "templates"
                    / "AGENTS.template.md").read_text(encoding="utf-8")
        self.assertIn("<!-- prime:begin", tmpl)
        self.assertIn("<!-- prime:end -->", tmpl)
        head = tmpl[:tmpl.index("<!-- prime:end -->")]
        for phrase in ("Words first.",
                       "No code change without an approved plan",
                       "Commit each slice as it lands",
                       "re-ground from AGENTS.md"):
            self.assertIn(phrase, head)


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


class TestHookTemplates(unittest.TestCase):
    # The single canonical re-ground command, inlined byte-identically into
    # every harness config. Locked here so a reworded, desynced, or
    # shell-broken variant fails CI instead of silently shipping.
    CANONICAL_COMMAND = (
        "echo 'Context was compacted or the session restarted. Before "
        "continuing, re-read AGENTS.md from disk, especially the Prime "
        "Invariants block. Treat AGENTS.md, not this message, as authoritative.'"
    )

    # rel -> (harness event key, expected matcher value or None for no matcher)
    HOOK_SCHEMA = {
        "claude/settings.json": ("SessionStart", "compact"),
        "codex/hooks.json": ("SessionStart", "compact"),
        "agy/hooks.json": ("SessionStart", "compact"),
        "grok/hooks/reground.json": ("PostCompact", None),
    }

    def test_hook_configs_present_copied_and_portable(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            fixtures.run_discover(repo)
            hooks = repo / ".bootstrap-tmp" / "templates" / "hooks"
            # The re-ground trigger is inlined into each config; there is no
            # shared shell script to install.
            self.assertFalse((hooks / "reground.sh").exists())

            commands = set()
            for rel, (event, matcher) in self.HOOK_SCHEMA.items():
                path = hooks / rel
                self.assertTrue(path.is_file(), rel)
                txt = path.read_text(encoding="utf-8")
                # Portable: no baked path, no token to substitute, and no
                # script/shell dependency that would break on clone, move, or
                # Windows.
                self.assertNotIn("__REPO_ROOT__", txt, rel)
                self.assertNotIn("reground.sh", txt, rel)
                self.assertNotIn(".sh", txt, rel)
                self.assertNotIn("/Users/", txt, rel)
                self.assertNotIn("git rev-parse", txt, rel)
                # Assert against the PARSED JSON, not the prose: this validates
                # the config is loadable and prevents the matcher check from
                # being satisfied by the word "compacted" in the trigger text.
                cfg = json.loads(txt)
                entry = cfg["hooks"][event][0]
                if matcher is None:
                    self.assertNotIn("matcher", entry, rel)
                else:
                    self.assertEqual(entry.get("matcher"), matcher, rel)
                command = entry["hooks"][0]["command"]
                # Allowlist the shape (an inline echo, not an interpreter or a
                # helper script) and lock the exact pointer text, including the
                # anti-injection clause "...not this message, as authoritative."
                self.assertTrue(command.startswith("echo "), rel)
                self.assertEqual(command, self.CANONICAL_COMMAND, rel)
                commands.add(command)
            # All four harnesses must ship the identical trigger copy.
            self.assertEqual(len(commands), 1)


if __name__ == "__main__":
    unittest.main()
