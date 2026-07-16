"""Structural tests for the shipped template set and shipped-set.json.

These guard product structure — what ships, where it lands, that the refresh
manifest is internally consistent — not template wording (prose-pin phrase
tests were retired 2026-07-08 with the discover-era suite; template content
is governed by the no-rule-without-provenance discipline, not CI grep).
"""

import json
import os
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

GOVERNANCE_MARKER = (
    "<!-- Installed by governance refresh; do not edit. Any change here "
    "is drift and is restored on the next refresh. Route changes "
    "through the toolkit owner. -->"
)


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


if __name__ == "__main__":
    unittest.main()
