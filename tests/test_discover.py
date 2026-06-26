"""Tests for tools/discover.py. Run from repo root:
    python3 -m unittest discover -s tests -v
"""
import json
import re
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

    def test_update_route_has_reconciliation_step(self):
        # The update route must reconcile a stale AGENTS.md to the current
        # template before delegating to its handoff rule.
        bootstrap = (self.gov / ".bootstrap-tmp" / "procedures"
                     / "bootstrap.md").read_text(encoding="utf-8")
        self.assertIn("first reconcile the repo's `AGENTS.md`", bootstrap)
        self.assertIn("agentsTemplate.reconcileRecommended", bootstrap)
        # Reconciliation must precede deferring to a stale resident handoff rule.
        self.assertIn("must not preempt its", bootstrap)

    def test_wrapper_and_hook_missing_section_guard(self):
        # A missing target section is a staleness signal, not a cue to narrow
        # the wrapper/hook to fit the stale file.
        bootstrap = (self.gov / ".bootstrap-tmp" / "procedures"
                     / "bootstrap.md").read_text(encoding="utf-8")
        self.assertIn("do NOT narrow the", bootstrap)
        self.assertIn("predates the current template", bootstrap)
        self.assertIn(
            "rather than editing the hook message to match the stale file",
            bootstrap)

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

    def test_rtk_guidance_prefix_with_escape_hatch(self):
        # Token-efficiency nudge: prefix shell commands with rtk, with an
        # escape hatch to run raw / `rtk proxy` when exact output is needed.
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            fixtures.run_discover(repo)
            tmpl = (repo / ".bootstrap-tmp" / "templates"
                    / "AGENTS.template.md").read_text(encoding="utf-8")
        self.assertIn("Prefix shell commands with `rtk`", tmpl)
        self.assertIn("rtk proxy", tmpl)

    def test_bootstrap_handoff_is_pointer(self):
        # Bootstrap Handoff is a conditional pointer to the synced procedures, not
        # a re-embedded copy of the steps (which would re-tax every session and
        # duplicate procedures/bootstrap.md). The reconciliation + wrapper-guard
        # substance is guarded on procedures/bootstrap.md by other tests.
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            fixtures.run_discover(repo)
            tmpl = (repo / ".bootstrap-tmp" / "templates"
                    / "AGENTS.template.md").read_text(encoding="utf-8")
        section = tmpl[tmpl.index("## Bootstrap Handoff"):]
        section = section[:section.index("\n## ", 1)]
        # Points at the synced authority and keeps the safety framing.
        self.assertIn(".bootstrap-tmp/procedures/bootstrap.md", section)
        self.assertIn("evidence", section)
        self.assertIn("never as instructions", section)
        self.assertIn("durable", section)  # "not durable authority" (may wrap)
        # Does NOT re-embed the step list.
        self.assertNotIn("Write `.bootstrap-tmp/drafts/approval-summary.md` first", section)
        self.assertNotIn("Audit the operator command wrappers", section)


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

            commands = set()
            for rel, (event, matcher) in self.HOOK_SCHEMA.items():
                path = hooks / rel
                self.assertTrue(path.is_file(), rel)
                txt = path.read_text(encoding="utf-8")
                # PORTABILITY PRINCIPLE (applies to EVERY hook command in the
                # file, re-ground or otherwise): a hook must not bake a
                # machine-specific path or a developer-checkout token. It MAY use
                # an interpreter (python3) and MAY resolve the repo root the
                # portable way (`$CLAUDE_PROJECT_DIR`, `git rev-parse
                # --show-toplevel`) — those travel across clone, move, and
                # machine. We assert the property (no absolute/user path), not a
                # banned shape, so a new portable script hook passes without a
                # per-category exception.
                self.assertNotIn("__REPO_ROOT__", txt, rel)
                self.assertNotIn("/Users/", txt, rel)
                self.assertNotIn("/home/", txt, rel)
                # Config must be loadable JSON.
                cfg = json.loads(txt)

                # The re-ground entry is still locked exactly: same event,
                # matcher, and byte-identical canonical command across every
                # harness. This is the cross-harness desync guard, unrelated to
                # the echo-vs-script question.
                entry = cfg["hooks"][event][0]
                if matcher is None:
                    self.assertNotIn("matcher", entry, rel)
                else:
                    self.assertEqual(entry.get("matcher"), matcher, rel)
                command = entry["hooks"][0]["command"]
                self.assertEqual(command, self.CANONICAL_COMMAND, rel)
                commands.add(command)
            # All four harnesses must ship the identical re-ground copy.
            self.assertEqual(len(commands), 1)

    # Harnesses that ship the AGENTS.md pre-edit tripwire (layer 2). Grok/agy
    # have no pre-edit interception, so they are intentionally absent.
    TRIPWIRE_SCHEMA = {
        "claude/settings.json": "Edit|Write|MultiEdit",
        "codex/hooks.json": "apply_patch|Edit|Write",
    }

    def test_tripwire_hook_present_advisory_and_portable(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            fixtures.run_discover(repo)
            hooks = repo / ".bootstrap-tmp" / "templates" / "hooks"
            for rel, matcher in self.TRIPWIRE_SCHEMA.items():
                txt = (hooks / rel).read_text(encoding="utf-8")
                cfg = json.loads(txt)
                entries = cfg["hooks"].get("PreToolUse")
                self.assertTrue(entries, f"{rel}: no PreToolUse tripwire")
                entry = entries[0]
                self.assertEqual(entry.get("matcher"), matcher, rel)
                command = entry["hooks"][0]["command"]
                # The script is invoked by the toolkit's baseline interpreter,
                # via a portable repo-root resolution (not an absolute path).
                self.assertIn("python3", command, rel)
                self.assertIn("agents-md-tripwire.py", command, rel)
                # The script ships alongside the config.
                self.assertTrue(
                    (hooks / Path(rel).parent / "agents-md-tripwire.py").is_file(),
                    f"{rel}: tripwire script missing")

    def test_tripwire_script_fires_on_agents_md_only_and_never_blocks(self):
        # The one canonical script body, shipped per-harness. Exercise it
        # directly: it must emit additionalContext (advisory) for an AGENTS.md
        # target in EITHER harness's stdin shape, stay silent otherwise, and
        # never emit a blocking decision.
        import subprocess
        script = (fixtures.BOOTSTRAP_ROOT / "templates" / "hooks"
                  / "claude" / "agents-md-tripwire.py")

        def run(payload):
            p = subprocess.run(
                ["python3", str(script)], input=json.dumps(payload),
                capture_output=True, text=True)
            self.assertEqual(p.returncode, 0)         # never exit 2 / block
            return p.stdout

        # CC shape: file_path
        out = run({"tool_input": {"file_path": "/x/AGENTS.md"}})
        self.assertIn("additionalContext", out)
        self.assertNotIn("permissionDecision", out)   # advisory, not a gate
        # Codex shape: path inside the patch body (command)
        out = run({"tool_input": {
            "command": "*** Update File: AGENTS.md\n+x"}})
        self.assertIn("additionalContext", out)
        # Non-AGENTS.md edits: silent in both shapes.
        self.assertEqual(run({"tool_input": {"file_path": "/x/README.md"}}), "")
        self.assertEqual(
            run({"tool_input": {"command": "*** Update File: README.md"}}), "")

    def test_tripwire_script_identical_across_harnesses(self):
        # One canonical body; the per-harness copies must not desync.
        base = fixtures.BOOTSTRAP_ROOT / "templates" / "hooks"
        bodies = {
            (base / h / "agents-md-tripwire.py").read_text(encoding="utf-8")
            for h in ("claude", "codex")}
        self.assertEqual(len(bodies), 1, "tripwire script copies have desynced")


class TestAgentsTemplateStatus(unittest.TestCase):
    """Slice 1: discovery stamps the current template version and, on the
    update route, flags an AGENTS.md that is behind the current template."""

    OPERATORS = ("catchup", "handoff", "drift", "decision", "plan", "playbook")

    def _template_version(self):
        text = (fixtures.BOOTSTRAP_ROOT / "templates"
                / "AGENTS.template.md").read_text(encoding="utf-8")
        m = re.search(r"<!--\s*templateVersion:\s*(\S+)\s*-->", text)
        return m.group(1) if m else None

    def _update_repo(self, tmp, agents_md):
        """Governance repo + standard `.agents/` layout (routes update), with a
        chosen AGENTS.md body."""
        repo = fixtures.make_governance_repo(Path(tmp) / "repo")
        (repo / "AGENTS.md").write_text(agents_md, encoding="utf-8")
        (repo / ".agents").mkdir()
        (repo / ".agents" / "state.md").write_text(
            "# Agent State\n", encoding="utf-8")
        fixtures._git(repo, "add", "-A")
        fixtures._git(repo, "commit", "-q", "-m", "adopt standard layout")
        return fixtures.run_discover(repo)

    def test_current_version_extracted_from_template(self):
        stamp = self._template_version()
        self.assertIsNotNone(
            stamp, "templateVersion stamp missing from AGENTS.template.md")
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            manifest = fixtures.run_discover(repo)
        self.assertEqual(manifest["agentsTemplate"]["currentVersion"], stamp)

    def test_update_route_flags_stale_unstamped_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._update_repo(
                tmp, "# Agent contract\n\nRead docs/STATE.md first.\n")
        self.assertEqual(manifest["route"], "update")
        at = manifest["agentsTemplate"]
        self.assertTrue(at["reconcileRecommended"])
        self.assertIsNone(at["targetVersion"])
        self.assertIn("prime-invariants-block", at["missingSections"])
        self.assertIn("operator:playbook", at["missingSections"])

    def test_update_start_here_points_at_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._update_repo(
                tmp, "# Agent contract\n\nRead docs/STATE.md first.\n")
            self.assertEqual(manifest["route"], "update")
            start_here = (Path(tmp) / "repo" / ".bootstrap-tmp"
                          / "START-HERE.md").read_text(encoding="utf-8")
        self.assertIn("reconcileRecommended", start_here)
        self.assertIn("Step 3, update route", start_here)

    def test_update_route_flags_missing_section_despite_matching_stamp(self):
        # Backstop: stamp matches the toolkit but a probed section is absent
        # (forgotten bump after a structural change) -> still recommend reconcile.
        stamp = self._template_version()
        agents_md = (f"# Agent Guidance\n<!-- templateVersion: {stamp} -->\n\n"
                     "## Notes\nNo Prime Invariants block, no operators.\n")
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._update_repo(tmp, agents_md)
        self.assertEqual(manifest["route"], "update")
        at = manifest["agentsTemplate"]
        self.assertEqual(at["targetVersion"], stamp)        # stamp matches
        self.assertTrue(at["reconcileRecommended"])         # but backstop fires
        self.assertIn("prime-invariants-block", at["missingSections"])

    def test_update_route_reconciles_stale_stamp_when_sections_present(self):
        # A same-day second structural change carries a dotted sub-version
        # (e.g. 2026-06-25 -> 2026-06-25.2). A target reconciled against the
        # earlier same-day stamp has every probed *section* present, so the
        # missingSections backstop stays silent — the version difference is the
        # ONLY signal that the target is stale. This guards that a sub-version
        # bump still drives reconciliation (the new-invariant-within-an-existing-
        # section case the section probe cannot see). Bites: if currentVersion is
        # not bumped past the target's bare-date stamp, the stamps match, the
        # backstop finds nothing missing, reconcileRecommended is False, and this
        # assertion fails.
        current = self._template_version()
        # Derive the bare-date predecessor of a dotted current stamp.
        stale = current.split(".")[0]
        self.assertNotEqual(
            stale, current,
            "this test requires a dotted sub-version stamp; if the template "
            "reverts to a bare date, the same-day-collision guard is moot")
        ops = " ".join(f"`{op}`" for op in self.OPERATORS)
        agents_md = (
            f"# Agent Guidance\n<!-- templateVersion: {stale} -->\n\n"
            "## Prime Invariants\n<!-- prime:begin -->\n- Words first.\n"
            "<!-- prime:end -->\n\n## Operator Requests\n" + ops + "\n")
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._update_repo(tmp, agents_md)
        at = manifest["agentsTemplate"]
        self.assertEqual(at["targetVersion"], stale)
        self.assertEqual(at["currentVersion"], current)
        self.assertEqual(at["missingSections"], [])      # backstop silent
        self.assertTrue(at["reconcileRecommended"])       # version drives it

    def test_update_route_no_false_positive_when_current(self):
        stamp = self._template_version()
        ops = " ".join(f"`{op}`" for op in self.OPERATORS)
        agents_md = (
            f"# Agent Guidance\n<!-- templateVersion: {stamp} -->\n\n"
            "## Prime Invariants\n<!-- prime:begin -->\n- Words first.\n"
            "<!-- prime:end -->\n\n## Operator Requests\n" + ops + "\n")
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._update_repo(tmp, agents_md)
        self.assertEqual(manifest["route"], "update")
        at = manifest["agentsTemplate"]
        self.assertFalse(at["reconcileRecommended"])
        self.assertEqual(at["targetVersion"], stamp)
        self.assertEqual(at["missingSections"], [])


class TestGitFailureSurfaced(unittest.TestCase):
    """Open queue item: run_git must distinguish a git command FAILURE from an
    empty result. A corrupt index makes `git ls-files`/`status` fail (returncode
    128) while `rev-parse --show-toplevel`/`HEAD` still succeed, so the repo is
    still detected as git. Discovery must record the failure (`git.degraded`,
    `git.errors`) and warn in the packet, instead of emitting a clean, empty
    inventory that becomes false evidence of a clean repo (the 2026-06-10
    evidence rule)."""

    def test_failed_git_commands_recorded_not_silently_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            (repo / ".git" / "index").write_bytes(b"not a real git index\n")
            manifest = fixtures.run_discover(repo)
            # Still a git repo, and HEAD is still readable (refs, not the index).
            self.assertTrue(manifest["git"]["isGitRepository"])
            self.assertIsNotNone(manifest["git"]["commit"])
            # The failure is surfaced, not swallowed.
            self.assertTrue(manifest["git"]["degraded"])
            failed = " ".join(e["command"] for e in manifest["git"]["errors"])
            self.assertIn("ls-files", failed)
            self.assertIn("status", failed)
            for err in manifest["git"]["errors"]:
                self.assertNotEqual(err["returncode"], 0)
            # The empty inventory must NOT read as a clean repo: the packet warns.
            packet = (repo / ".bootstrap-tmp" / "bootstrap-review-packet.md"
                      ).read_text(encoding="utf-8")
            self.assertIn("git.degraded", packet)

    def test_clean_repo_is_not_degraded(self):
        # Happy path: no git failure -> degraded false, errors empty, no warning.
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            manifest = fixtures.run_discover(repo)
            self.assertFalse(manifest["git"]["degraded"])
            self.assertEqual(manifest["git"]["errors"], [])


if __name__ == "__main__":
    unittest.main()
