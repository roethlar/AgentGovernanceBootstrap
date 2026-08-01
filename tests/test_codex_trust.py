"""The codex hook trust pin (guard-port plan, slice 4): refresh drives
codex's own app-server (`hooks/list` -> `config/batchWrite`), so codex
computes the trust hash and writes its own config - refresh never parses
or edits the TOML. These tests run the real driver against a fake
app-server speaking the probe-verified wire shapes (codex 0.146.0,
capability ledger 2026-08-01)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import refresh  # noqa: E402

# The fake speaks newline-delimited JSON-RPC like `codex app-server`. It
# serves one repo-local untrusted hook, one foreign-path untrusted hook,
# and one repo-local already-trusted hook; a config/batchWrite records its
# params to the sentinel file and flips the repo hook to trusted.
FAKE_APP_SERVER = r'''
import json, os, sys

repo = os.environ["FAKE_REPO"]
sentinel = os.environ["FAKE_SENTINEL"]
repo_key = repo + "/.codex/hooks.json:pre_tool_use:0:0"
hooks = [
    {"key": repo_key, "currentHash": "sha256:aaa111",
     "trustStatus": "untrusted",
     "sourcePath": repo + "/.codex/hooks.json"},
    {"key": "/elsewhere/.codex/hooks.json:pre_tool_use:0:0",
     "currentHash": "sha256:bbb222", "trustStatus": "untrusted",
     "sourcePath": "/elsewhere/.codex/hooks.json"},
    {"key": repo + "/.codex/hooks.json:session_start:0:0",
     "currentHash": "sha256:ccc333", "trustStatus": "trusted",
     "sourcePath": repo + "/.codex/hooks.json"},
]
wrote = False
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    msg = json.loads(line)
    method, rid = msg.get("method"), msg.get("id")
    if rid is None:
        continue  # notifications need no reply
    if method == "initialize":
        out = {"jsonrpc": "2.0", "id": rid, "result": {"codexHome": "x"}}
    elif method == "hooks/list":
        served = [dict(h) for h in hooks]
        if wrote:
            for h in served:
                if h["key"] == repo_key:
                    h["trustStatus"] = "trusted"
        out = {"jsonrpc": "2.0", "id": rid,
               "result": {"data": [{"cwd": repo, "hooks": served,
                                    "errors": [], "warnings": []}]}}
    elif method == "config/batchWrite":
        with open(sentinel, "w") as f:
            json.dump(msg["params"], f)
        wrote = True
        out = {"jsonrpc": "2.0", "id": rid,
               "result": {"status": "ok", "version": "sha256:v2",
                          "filePath": "fake-config.toml"}}
    else:
        out = {"jsonrpc": "2.0", "id": rid,
               "error": {"code": -32601, "message": "unknown"}}
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()
'''


class TrustPinTests(unittest.TestCase):
    def drive(self, tmp, confirm, fake_body=FAKE_APP_SERVER):
        import os
        repo = Path(tmp) / "repo"
        repo.mkdir(exist_ok=True)
        fake = Path(tmp) / "fake_app_server.py"
        fake.write_text(fake_body, encoding="utf-8")
        sentinel = Path(tmp) / "sentinel.json"
        os.environ["FAKE_REPO"] = str(repo).replace("\\", "/")
        os.environ["FAKE_SENTINEL"] = str(sentinel)
        try:
            line = refresh.codex_trust_pin(repo, [sys.executable, str(fake)],
                                           confirm)
        finally:
            os.environ.pop("FAKE_REPO", None)
            os.environ.pop("FAKE_SENTINEL", None)
        return line, sentinel

    def test_pins_only_this_repos_untrusted_hooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            line, sentinel = self.drive(tmp, confirm=lambda prompt: True)
            self.assertEqual(line, "codex trust: pinned 1 hook(s), "
                                   "verified trusted")
            params = json.loads(sentinel.read_text(encoding="utf-8"))
            (edit,) = params["edits"]
            self.assertEqual(edit["keyPath"], "hooks.state")
            self.assertEqual(edit["mergeStrategy"], "upsert")
            (key, value), = edit["value"].items()
            # exactly the repo's untrusted hook: the foreign-path hook and
            # the already-trusted one are never written
            self.assertIn("/repo/.codex/hooks.json:pre_tool_use", key)
            self.assertEqual(value, {"trusted_hash": "sha256:aaa111"})

    def test_decline_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            line, sentinel = self.drive(tmp, confirm=lambda prompt: False)
            self.assertEqual(line, "codex trust: not pinned (declined)")
            self.assertFalse(sentinel.exists())

    def test_dead_server_reports_skipped_and_never_asks(self):
        asked = []
        with tempfile.TemporaryDirectory() as tmp:
            line, sentinel = self.drive(
                tmp, confirm=lambda prompt: asked.append(prompt) or True,
                fake_body="import sys; sys.exit(0)\n")
            self.assertEqual(line,
                             "codex trust: skipped (no app-server handshake)")
            self.assertEqual(asked, [])
            self.assertFalse(sentinel.exists())


class OfferGateTests(unittest.TestCase):
    def test_untouched_codex_config_never_launches(self):
        # The offer must be inert unless this run installed, updated, or
        # restored .codex/hooks.json - regardless of TTY or PATH state.
        plan = refresh.Plan()
        plan.install = [("AGENTS.md", Path("x"))]
        original = refresh.codex_trust_pin
        refresh.codex_trust_pin = lambda *a, **k: self.fail(
            "codex_trust_pin launched for a run that never touched "
            + refresh.CODEX_HOOKS_TARGET)
        try:
            refresh.offer_codex_hook_trust(Path("."), plan)
        finally:
            refresh.codex_trust_pin = original

    def test_touched_gate_matches_the_shipped_target(self):
        # The gate string and the manifest target stay in lockstep.
        targets = {a["target"] for a in json.loads(
            (Path(refresh.__file__).resolve().parent / "shipped-set.json")
            .read_text(encoding="utf-8"))["artifacts"]}
        self.assertIn(refresh.CODEX_HOOKS_TARGET, targets)


if __name__ == "__main__":
    unittest.main()
