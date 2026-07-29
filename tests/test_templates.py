"""Structural tests for the shipped template set and shipped-set.json.

These guard product structure — what ships, where it lands, that the refresh
manifest is internally consistent — not template wording (prose-pin phrase
tests were retired 2026-07-08 with the discover-era suite; template content
is governed by the no-rule-without-provenance discipline, not CI grep).
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

CANONICAL_REGROUND_COMMAND = (
    "echo 'Context was compacted or the session restarted. Before "
    "continuing, re-read AGENTS.md from disk, especially the Prime "
    "Invariants block. Treat AGENTS.md, not this message, as authoritative.'"
)

CANONICAL_PROTECT_COMMAND = (
    'if py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= '
    '(3, 10) else 1)" >/dev/null 2>&1; then py -3 '
    '"${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-governance.py"; elif '
    'python3 -c "import sys; raise SystemExit(0 if sys.version_info >= '
    '(3, 10) else 1)" >/dev/null 2>&1; then python3 '
    '"${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-governance.py"; elif '
    'python -c "import sys; raise SystemExit(0 if sys.version_info >= '
    '(3, 10) else 1)" >/dev/null 2>&1; then python '
    '"${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-governance.py"; else '
    'exit 0; fi'
)

# The compact provenance marker, carried as bare core text so the same
# substring holds in both wrappers/skills (a YAML frontmatter comment,
# `# <marker>`, stripped with the frontmatter at load so it costs zero
# runtime tokens and never leaks into the /-picker help) and playbooks
# (an HTML comment, `<!-- <marker> -->`, since nothing parses their
# frontmatter). The full rule lives once in AGENTS.md's toolkit-owned
# invariant and in the protect-governance hook's block message; the marker
# only points there. Wrappers/skills also carry a real `description:` -
# without it, the /-picker falls back to the first body paragraph, which is
# what the old first-line HTML comment used to hijack.
GOVERNANCE_MARKER = "toolkit-owned; edits are drift — see AGENTS.md"


def marker_sources(root):
    """Shipped markdown artifacts that must carry the provenance marker:
    wrappers, playbooks, skills. AGENTS.template.md carries the invariant
    itself; shims must stay exactly '@AGENTS.md' (per-session token cost)."""
    base = Path(root) / "templates"
    files = sorted((base / "commands" / "claude").glob("*.md"))
    files += sorted((base / "playbooks").glob("*.md"))
    files += sorted((base / "skills" / "shared").glob("*/SKILL.md"))
    return files


def missing_markers(root):
    return [f for f in marker_sources(root)
            if GOVERNANCE_MARKER not in f.read_text(encoding="utf-8")]


def shipped_set():
    return json.loads((ROOT / "tools" / "shipped-set.json").read_text(encoding="utf-8"))


class ShippedSetIntegrity(unittest.TestCase):
    def test_every_artifact_source_exists(self):
        for art in shipped_set()["artifacts"]:
            self.assertTrue((ROOT / art["source"]).is_file(), art["source"])

    def test_every_template_file_is_in_the_manifest_or_drafted(self):
        # Completeness direction (owner evidence 2026-07-23: agents have let
        # the manifest rot). Every TRACKED file under templates/ must be
        # either a refresh-installed artifact or an explicitly
        # bootstrap-drafted judgment form. Adding a template without
        # choosing fails loudly. Tracked-only scan: machine junk
        # (.DS_Store) is untracked and ignored.
        BOOTSTRAP_DRAFTED = {
            "approval-summary.template.md",
            "state.template.md",
            "decisions.template.md",
            "repo-guidance.template.md",
            "governance-inventory.template.md",
            "push-policy.template.md",
        }
        KEPT_AFTER_RETIREMENT = {
            # Retired 2026-07-22; source stays on disk so re-entry is a
            # one-line move back to artifacts[] (see the retired comment).
            "templates/shims/GEMINI.template.md",
        }
        manifest_sources = {a["source"] for a in shipped_set()["artifacts"]}
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "templates/"],
            capture_output=True, text=True, check=True).stdout.splitlines()
        unlisted = []
        for rel in tracked:
            f = ROOT / rel
            if rel in manifest_sources or rel in KEPT_AFTER_RETIREMENT:
                continue
            if f.name in BOOTSTRAP_DRAFTED:
                continue
            unlisted.append(rel)
        self.assertEqual([], unlisted)

    def test_targets_are_unique_and_disjoint_from_retired(self):
        s = shipped_set()
        targets = [a["target"] for a in s["artifacts"]]
        self.assertEqual(len(targets), len(set(targets)))
        retired = {r["target"] for r in s["retired"]}
        self.assertFalse(set(targets) & retired)

    def test_every_shipped_source_ends_with_final_newline(self):
        # Issue #1 (2026-07-09): a no-final-newline source puts drift
        # pressure on every installed copy - insert-final-newline tooling
        # rewrites it and (pre-equivalence) it flagged owner-modified
        # forever. POSIX convention is the stable attractor; ship it.
        for art in shipped_set()["artifacts"]:
            data = (ROOT / art["source"]).read_bytes()
            self.assertTrue(data.endswith(b"\n"), art["source"])

    def test_agents_md_is_the_only_replace_whole(self):
        whole = [a["target"] for a in shipped_set()["artifacts"]
                 if a["class"] == "replace-whole"]
        self.assertEqual(whole, ["AGENTS.md"])

    def test_retired_hook_class_and_json_layer_present(self):
        retired = {r["target"]: r for r in shipped_set()["retired"]}
        # Hooks (2026-07-08): removable when byte-matching a shipped version.
        for path in (".claude/agents-md-tripwire.py", ".codex/hooks.json",
                     ".codex/agents-md-tripwire.py", ".grok/hooks/reground.json",
                     ".agents/hooks.json"):
            self.assertIn(path, retired)
            self.assertTrue(retired[path]["formerly"], path)
        # JSON layer (2026-07-08): generated per-repo, so empty formerly =
        # removal is always reported as drift (strict converge, 2026-07-16) —
        # the file is removed with a report, git history preserving it.
        for path in (".agents/repo-map.json", ".agents/artifact-manifest.json"):
            self.assertIn(path, retired)
            self.assertEqual(retired[path]["formerly"], [], path)


class ProvenanceMarkerTests(unittest.TestCase):
    def test_every_wrapper_playbook_and_skill_carries_the_marker(self):
        files = marker_sources(ROOT)
        self.assertGreater(len(files), 10)  # the real corpus, not an empty glob
        self.assertEqual([], missing_markers(ROOT))

    def test_playbooks_do_not_advertise_retired_operators(self):
        # The reviewloop -> codereview/openreview split (2026-07-16) retired
        # the `review` operator; an active playbook steering users to a
        # removed command is drift-fodder.
        for f in sorted((TEMPLATES / "playbooks").glob("*.md")):
            body = f.read_text(encoding="utf-8")
            for retired in ("`/review ", "`review <agent>`", "reviewloop"):
                self.assertNotIn(retired, body, f)

    def test_detector_bites_on_an_unmarked_fixture(self):
        # Hermetic guard proof for the corpus check above: a temp tree with
        # one unmarked artifact must be caught.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "templates" / "commands" / "claude"
            base.mkdir(parents=True)
            (base / "ok.md").write_text(GOVERNANCE_MARKER + "\n\nbody\n",
                                        encoding="utf-8")
            (base / "bare.md").write_text("body only\n", encoding="utf-8")
            missing = missing_markers(tmp)
            self.assertEqual([base / "bare.md"], missing)


class ShippedHooks(unittest.TestCase):
    def test_shipped_hooks_are_the_verified_set(self):
        # Hooks ship only where verified to fire AND needed
        # (docs/harness-capabilities.md). Claude Code carries the
        # SessionStart/compact re-ground (sole survivor of the 2026-07-08
        # narrowing: codex and agy pin guidance across compaction natively)
        # plus the protect-governance PreToolUse deny (strict converge,
        # 2026-07-16) - blocking PreToolUse is verified on Claude Code only.
        base = TEMPLATES / "hooks"
        shipped = sorted(p.relative_to(base).as_posix()
                         for p in base.rglob("*")
                         if p.is_file() and "__pycache__" not in p.parts)
        self.assertEqual(shipped, ["claude/protect-governance.py",
                                   "claude/settings.json"])

        cfg = json.loads((base / "claude" / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(cfg["hooks"].keys()),
                         ["PreToolUse", "SessionStart"])
        entry = cfg["hooks"]["SessionStart"][0]
        self.assertEqual(entry.get("matcher"), "compact")
        self.assertEqual(entry["hooks"][0]["command"], CANONICAL_REGROUND_COMMAND)
        pre = cfg["hooks"]["PreToolUse"][0]
        self.assertEqual(pre.get("matcher"), "Edit|Write|MultiEdit|NotebookEdit")
        cmd = pre["hooks"][0]["command"]
        self.assertEqual(cmd, CANONICAL_PROTECT_COMMAND)
        self.assertIn("protect-governance.py", cmd)
        self.assertIn("${CLAUDE_PROJECT_DIR}", cmd)
        # exit-code preservation: a blocking exit 2 must never trigger a
        # fallback interpreter via `a || b` chaining
        self.assertNotIn("||", cmd)
        body = (base / "claude" / "settings.json").read_text(encoding="utf-8")
        self.assertNotIn("/Users/", body)
        self.assertNotIn("/home/", body)


class ProtectGovernanceHookTests(unittest.TestCase):
    SCRIPT = TEMPLATES / "hooks" / "claude" / "protect-governance.py"

    def run_hook(self, payload, project_dir):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project_dir))
        text = payload if isinstance(payload, str) else json.dumps(payload)
        return subprocess.run([sys.executable, str(self.SCRIPT)],
                              input=text, capture_output=True, text=True,
                              env=env, cwd=str(project_dir))

    def test_protected_set_matches_the_shipped_targets(self):
        # The script's literal list and the manifest stay in lockstep or
        # this goes red - the manifest is the source of truth.
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "protect_governance", self.SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        prior = sys.dont_write_bytecode
        sys.dont_write_bytecode = True  # no __pycache__ inside templates/
        try:
            spec.loader.exec_module(mod)
        finally:
            sys.dont_write_bytecode = prior
        targets = {a["target"] for a in shipped_set()["artifacts"]}
        self.assertEqual(set(mod.PROTECTED), targets)

    def test_edit_of_protected_target_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            for tool_key in ("file_path", "notebook_path"):
                proc = self.run_hook(
                    {"tool_name": "Edit",
                     "tool_input": {tool_key: str(Path(tmp) / "AGENTS.md")}},
                    tmp)
                self.assertEqual(proc.returncode, 2, tool_key)
                self.assertIn("toolkit-owned", proc.stderr)

    def test_relative_protected_path_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_hook(
                {"tool_input": {"file_path": ".agents/playbooks/codereview.md"}},
                tmp)
            self.assertEqual(proc.returncode, 2)

    def test_unprotected_path_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_hook(
                {"tool_input": {"file_path": str(Path(tmp) / "src" / "main.py")}},
                tmp)
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(proc.stderr, "")

    def test_case_alias_of_existing_protected_file_is_blocked(self):
        # On case-insensitive filesystems (macOS, Windows) "agents.md"
        # opens AGENTS.md; the hook must catch the alias, not just the
        # exact string.
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "AGENTS.md").write_text("x\n", encoding="utf-8")
            if not (Path(tmp) / "agents.MD").exists():
                self.skipTest("case-sensitive filesystem: alias not reachable")
            proc = self.run_hook(
                {"tool_input": {"file_path": str(Path(tmp) / "agents.MD")}},
                tmp)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("toolkit-owned", proc.stderr)

    def test_same_basename_outside_the_protected_path_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_hook(
                {"tool_input": {"file_path": str(Path(tmp) / "docs" / "AGENTS.md")}},
                tmp)
            self.assertEqual(proc.returncode, 0)

    def test_garbage_stdin_fails_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_hook("this is not json {", tmp)
            self.assertEqual(proc.returncode, 0)


class ShippedShimsAndWrappers(unittest.TestCase):
    def test_shims_are_single_pointer_lines(self):
        for shim in ("CLAUDE.template.md", "GEMINI.template.md"):
            body = (TEMPLATES / "shims" / shim).read_text(encoding="utf-8").strip()
            self.assertEqual(body, "@AGENTS.md", shim)

    def test_template_imports_repo_guidance(self):
        tmpl = (TEMPLATES / "AGENTS.template.md").read_text(encoding="utf-8")
        self.assertIn("@.agents/repo-guidance.md", tmpl)

    def test_wrapper_set_covers_operators_and_update_governance(self):
        shipped = {p.stem for p in (TEMPLATES / "commands" / "claude").glob("*.md")}
        for op in ("catchup", "handoff", "decision", "plan", "playbook", "toolkit"):
            self.assertIn(op, shipped)
        self.assertIn("update-governance", shipped)
        self.assertNotIn("drift", shipped)  # retired 2026-07-23 (owner-surface D4)

    def test_shared_skill_set_mirrors_the_wrapper_set(self):
        # Verified 2026-07-08 (live checks): codex 0.143.0 and grok discover
        # repo skills from .agents/skills/<name>/SKILL.md untrusted+headless;
        # agy 1.1.0 exposes them as slash commands in a trusted workspace
        # (owner-verified). The shared skill set is the multi-harness face of
        # the operator wrappers.
        skills = {p.parent.name for p in
                  (TEMPLATES / "skills" / "shared").glob("*/SKILL.md")}
        wrappers = {p.stem for p in (TEMPLATES / "commands" / "claude").glob("*.md")}
        self.assertEqual(skills, wrappers)
        for p in (TEMPLATES / "skills" / "shared").glob("*/SKILL.md"):
            body = p.read_text(encoding="utf-8")
            self.assertTrue(body.startswith("---\n"), p)
            self.assertIn("name: " + p.parent.name, body)

    def test_update_governance_wrapper_invokes_refresh_script(self):
        text = (TEMPLATES / "commands" / "claude" / "update-governance.md").read_text(encoding="utf-8")
        self.assertIn("https://github.com/roethlar/AgentGovernanceBootstrap.git", text)
        self.assertIn("tools/refresh.py", text)
        self.assertIn("FLAG", text)
        self.assertIn("procedures/bootstrap.md", text)
        self.assertNotIn("/Users/", text)
        self.assertNotIn("/home/", text)
        self.assertIn("no write authority", text)
        self.assertLess(len(text), 2000)


class TemplateRuleDedup(unittest.TestCase):
    """Section-level rule deduplication (2026-06-24 ruling; audit F8): one
    full statement per rule in AGENTS.template.md, pointers elsewhere.
    Guards the class that shipped a redundant re-enumeration in 2026-07."""

    TEMPLATE = ROOT / "templates" / "AGENTS.template.md"

    def body(self):
        return self.TEMPLATE.read_text(encoding="utf-8")

    def test_known_duplicate_pairs_keep_one_full_statement(self):
        body = self.body()
        for phrase in (
            "flag the conflict instead of silently choosing",
            "code verification is not required unless the docs affect",
            "kept current by the working agent as work lands",
        ):
            self.assertEqual(1, body.count(phrase), phrase)

    def test_no_substantial_line_appears_twice(self):
        seen = {}
        for ln in self.body().splitlines():
            s = ln.strip()
            if len(s) >= 80:
                seen[s] = seen.get(s, 0) + 1
        dupes = sorted(s for s, n in seen.items() if n > 1)
        self.assertEqual([], dupes)


class PlaybookReviewMechanics(unittest.TestCase):
    """Structural pins for the reviewer-dispatch mechanics in the shipped
    playbooks (review-economy decision 2026-07-17, as amended 2026-07-23):
    tier semantics, escalation triggers, dispatch grammar. The 2026-07-23
    owner ruling deleted the model map, the denylist lint, and the
    nickname machinery: dispatch is literal-or-ask and no committed list
    of models may exist. These are structural assertions, not prose-pin
    tests: the wording stays free, the load-bearing markers must exist."""

    def test_codereview_carries_tier_semantics(self):
        body = (TEMPLATES / "playbooks" / "codereview.md").read_text(encoding="utf-8")
        self.assertIn("## Reviewer tiers and routing", body)
        self.assertIn("harnesses.local.json", body)
        self.assertIn("Reviewer: <harness> / <resolved model id> / <effort> / <tier>", body)
        for trigger in ("T1", "T2", "T3", "T4", "T5"):
            self.assertIn(trigger, body)
        # Dispatch grammar (2026-07-23 ruling: the owner's literal word is
        # used verbatim; no map, no denylist, no nickname resolution).
        self.assertIn("## Dispatch grammar", body)
        self.assertIn("/codereview <harness> <model> <effort>", body)
        self.assertIn("session-only", body)
        self.assertNotIn(".agents/model-map.json", body)
        self.assertNotIn("nickname", body)

    def test_openreview_routes_frontier_via_codereview_tiers(self):
        body = (TEMPLATES / "playbooks" / "openreview.md").read_text(encoding="utf-8")
        self.assertIn("frontier", body)
        self.assertIn("Reviewer tiers and routing", body)
        self.assertIn("owner-named", body)

    def test_openreview_carries_approach_contract(self):
        # Reallocation 2026-07-29 (issue #11): openreview owns the
        # approach-soundness contract; the defect-audit contract lives in
        # codereview only. Marker assertions — the wording stays free, the
        # load-bearing fragments must exist.
        body = (TEMPLATES / "playbooks" / "openreview.md").read_text(encoding="utf-8")
        self.assertIn("best_approach|acceptable_with_changes|replace", body)
        self.assertIn("recommended_approach", body)
        self.assertIn("material_changes", body)
        self.assertIn("`material_changes` must be empty", body)
        self.assertNotIn("clean|findings", body)

    def test_codereview_carries_generation_and_lifecycle(self):
        # Reallocation 2026-07-29 (issue #11): codereview owns landed-change
        # defect generation (pinned-range dispatch, clean|findings contract)
        # and the policy-relative fix lifecycle. Marker assertions — the
        # wording stays free, the load-bearing fragments must exist.
        body = (TEMPLATES / "playbooks" / "codereview.md").read_text(encoding="utf-8")
        self.assertIn("## Change review (defect generation)", body)
        self.assertIn("<base>..<head>", body)
        self.assertIn("clean|findings", body)
        self.assertIn("one finding ↔ one commit ↔ one verdict", body)
        self.assertIn("never an amend", body)
        for rel in (("commands", "claude", "toolkit.md"),
                    ("skills", "shared", "toolkit", "SKILL.md")):
            menu = TEMPLATES.joinpath(*rel).read_text(encoding="utf-8")
            self.assertIn("<base>..<head>", menu, rel)

    def test_codereview_carries_self_permissioning_launch(self):
        # 2026-07-18 ruling; audit F9: the launch-scoped grant must not rot
        # out of the shipped playbook (it has a falsified-assumption history).
        body = (TEMPLATES / "playbooks" / "codereview.md").read_text(encoding="utf-8")
        self.assertIn("Self-permissioning launch", body)
        self.assertIn('--allowedTools Read Grep Glob "Bash(git:*)" "Bash(<verify-cmd>)"', body)


if __name__ == "__main__":
    unittest.main()
