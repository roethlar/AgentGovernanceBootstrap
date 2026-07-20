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
        # always flagged for by-hand removal, never machine-deleted.
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
        for op in ("catchup", "handoff", "drift", "decision", "plan", "playbook"):
            self.assertIn(op, shipped)
        self.assertIn("update-governance", shipped)

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


class PlaybookModelFreedom(unittest.TestCase):
    """Shipped template text names no concrete model IDs (review-economy
    decision, 2026-07-17; scope widened to all templates — commands,
    skills, shims — by F11 of the 2026-07-19 model-map plan). The single
    deliberate exemption is `.agents/model-map.json`, the fleet-global
    nickname→slug map: slugs live there and nowhere else in committed
    text. The curated denylist lives beside the model facts in
    docs/harness-capabilities.md so both are updated in the same edit.
    This is a structural lint against a curated list, not a prose-pin
    test: the list is data, the wording stays free."""

    DENYLIST_DOC = ROOT / "docs" / "harness-capabilities.md"

    def load_denylist(self):
        text = self.DENYLIST_DOC.read_text(encoding="utf-8")
        m = re.search(r"```model-id-denylist\n(.*?)```", text, re.S)
        self.assertIsNotNone(
            m, "model-id-denylist fenced block missing from " + str(self.DENYLIST_DOC))
        tokens = [ln.strip() for ln in m.group(1).splitlines()]
        tokens = [t for t in tokens if t and not t.startswith("#")]
        self.assertTrue(tokens, "model-id-denylist block is empty")
        return tokens

    @staticmethod
    def token_pattern(token):
        # Left word boundary always; right boundary too unless the token is
        # a family prefix ending in '-' (e.g. 'grok-' must catch 'grok-4.5').
        pat = r"(?<![a-z0-9])" + re.escape(token.lower())
        if not token.endswith("-"):
            pat += r"(?![a-z0-9])"
        return pat

    def test_denylist_covers_known_families(self):
        tokens = self.load_denylist()
        for required in ("grok-", "gpt-", "gemini-", "claude-"):
            self.assertIn(required, tokens)

    def test_shipped_template_text_names_no_concrete_model_ids(self):
        # F11: every shipped template — playbooks, commands, skills,
        # shims — not just templates/playbooks/*.md.
        tokens = self.load_denylist()
        paths = sorted(TEMPLATES.rglob("*.md"))
        playbooks_only = list((TEMPLATES / "playbooks").glob("*.md"))
        self.assertGreater(
            len(paths), len(playbooks_only),
            "F11 scope regression: scan reaches only playbooks")
        for path in paths:
            body = path.read_text(encoding="utf-8").lower()
            for tok in tokens:
                hit = re.search(self.token_pattern(tok), body)
                self.assertIsNone(
                    hit, "%s names denied model token %r"
                    % (path.relative_to(TEMPLATES), tok))

    def test_codereview_carries_tier_semantics(self):
        body = (TEMPLATES / "playbooks" / "codereview.md").read_text(encoding="utf-8")
        self.assertIn("## Reviewer tiers and routing", body)
        self.assertIn("harnesses.local.json", body)
        self.assertIn("Reviewer: <harness> / <resolved model id> / <effort> / <tier>", body)
        for trigger in ("T1", "T2", "T3", "T4", "T5"):
            self.assertIn(trigger, body)
        # Model-map contract section (2026-07-19 plan, Slice 2).
        self.assertIn("## Model map and dispatch grammar", body)
        self.assertIn(".agents/model-map.json", body)
        self.assertIn("/codereview <harness> <nickname> <effort>", body)
        self.assertIn("session-only", body)

    def test_openreview_routes_frontier_via_codereview_tiers(self):
        body = (TEMPLATES / "playbooks" / "openreview.md").read_text(encoding="utf-8")
        self.assertIn("frontier", body)
        self.assertIn("Reviewer tiers and routing", body)
        self.assertIn("owner-confirmed", body)


if __name__ == "__main__":
    unittest.main()
