"""Fetch-contract lint for the fleet-global model map (.agents/model-map.json).

Executable form of the map schema and fetch contract in
docs/superpowers/plans/2026-07-19-model-map-reviewer-dispatch.md (F1, F9).
The validator below IS the contract at owner-adjudicated sizing: the owner
declined a standalone runtime resolver program (ruling 2026-07-19, recorded
in the plan's round-2 ledger), so the contract lives as playbook text for
the dispatching agent plus these hostile-fixture checks against the
committed file. `.agents/model-map.json` is the single sanctioned committed
home for concrete model slugs.

Loud-stop discipline: every rejection names the failed constraint and
nothing else — fetched content never appears in a stop message.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP_PATH = ROOT / ".agents" / "model-map.json"

SIZE_CAP = 16 * 1024
KNOWN_HARNESSES = frozenset({"codex", "claude", "gemini"})
TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

# A sentinel planted in every hostile fixture; no stop message may echo it.
EVIL = "zz-evil-payload-zz"


class MapRejected(Exception):
    """Loud stop: carries the failed constraint name, never fetched content."""

    def __init__(self, constraint):
        self.constraint = constraint
        super().__init__("model map rejected: %s" % constraint)


def _reject_duplicates(pairs):
    seen = set()
    for key, _ in pairs:
        if key in seen:
            raise MapRejected("duplicate-key")
        seen.add(key)
    return dict(pairs)


def validate_model_map(raw):
    """Apply the fetch contract, in contract order, to raw fetched bytes.

    Returns the parsed document; raises MapRejected(constraint) on the
    first failed rule. Constraint names: size-cap, parse, duplicate-key,
    shape, version, charset, harness-set.
    """
    # 1. Size cap — before any parsing touches the bytes.
    if len(raw) > SIZE_CAP:
        raise MapRejected("size-cap")
    # 2. Strict parse — UTF-8, duplicate keys anywhere are fatal (F9).
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicates)
    except MapRejected:
        raise
    except (UnicodeDecodeError, ValueError):
        raise MapRejected("parse") from None
    # 3. Shape — object; version 1; nicknames an object of objects.
    if not isinstance(doc, dict):
        raise MapRejected("shape")
    if doc.get("version") != 1:
        raise MapRejected("version")
    nicknames = doc.get("nicknames")
    if not isinstance(nicknames, dict):
        raise MapRejected("shape")
    for nickname, entry in nicknames.items():
        if not isinstance(entry, dict):
            raise MapRejected("shape")
        # 4. Charset — exact lowercase, no case folding (F9).
        if not TOKEN_RE.fullmatch(nickname):
            raise MapRejected("charset")
        for harness, slug in entry.items():
            if not isinstance(slug, str):
                raise MapRejected("shape")
            if not TOKEN_RE.fullmatch(harness):
                raise MapRejected("charset")
            # 5. Closed harness set — unknown keys are a hard failure (F9).
            if harness not in KNOWN_HARNESSES:
                raise MapRejected("harness-set")
            if not TOKEN_RE.fullmatch(slug):
                raise MapRejected("charset")
    return doc


def _valid_doc():
    return {"version": 1, "nicknames": {"sol": {"codex": "gpt-5.6-sol"}}}


def _reject(test, raw, constraint):
    with test.assertRaises(MapRejected) as ctx:
        validate_model_map(raw)
    test.assertEqual(ctx.exception.constraint, constraint)
    test.assertNotIn(EVIL, str(ctx.exception))
    return ctx.exception


class CommittedMapTests(unittest.TestCase):
    """The committed map must pass the same validator dispatch applies."""

    def test_committed_map_passes_fetch_contract(self):
        doc = validate_model_map(MAP_PATH.read_bytes())
        self.assertTrue(doc["nicknames"], "committed map has no nicknames")

    def test_committed_map_within_size_cap(self):
        self.assertLessEqual(MAP_PATH.stat().st_size, SIZE_CAP)


class SizeCapTests(unittest.TestCase):
    def test_oversize_rejected(self):
        raw = json.dumps(_valid_doc()).encode() + b" " * SIZE_CAP
        _reject(self, raw, "size-cap")

    def test_size_cap_applies_before_parse(self):
        # Oversize garbage must die as size-cap, never reach the parser.
        raw = (EVIL.encode() + b"{[not json") * 2048
        self.assertGreater(len(raw), SIZE_CAP)
        _reject(self, raw, "size-cap")

    def test_exactly_at_cap_accepted(self):
        raw = json.dumps(_valid_doc()).encode()
        raw += b" " * (SIZE_CAP - len(raw))
        self.assertEqual(len(raw), SIZE_CAP)
        validate_model_map(raw)


class StrictParseTests(unittest.TestCase):
    def test_invalid_json_rejected(self):
        _reject(self, ("{%s" % EVIL).encode(), "parse")

    def test_non_utf8_rejected(self):
        _reject(self, b"\xff\xfe" + EVIL.encode(), "parse")

    def test_duplicate_top_level_key_rejected(self):
        raw = '{"version": 1, "version": 1, "nicknames": {"%s": {}}}' % EVIL
        _reject(self, raw.encode(), "duplicate-key")

    def test_duplicate_nickname_rejected(self):
        raw = ('{"version": 1, "nicknames": '
               '{"sol": {"codex": "%s"}, "sol": {"codex": "b"}}}' % EVIL)
        _reject(self, raw.encode(), "duplicate-key")

    def test_duplicate_harness_key_rejected(self):
        raw = ('{"version": 1, "nicknames": '
               '{"sol": {"codex": "%s", "codex": "b"}}}' % EVIL)
        _reject(self, raw.encode(), "duplicate-key")


class ShapeTests(unittest.TestCase):
    def test_non_object_top_level_rejected(self):
        _reject(self, json.dumps([EVIL]).encode(), "shape")

    def test_wrong_version_rejected(self):
        _reject(self, json.dumps({"version": 2, "nicknames": {}}).encode(),
                "version")

    def test_string_version_rejected(self):
        _reject(self, json.dumps({"version": "1", "nicknames": {}}).encode(),
                "version")

    def test_missing_nicknames_rejected(self):
        _reject(self, json.dumps({"version": 1}).encode(), "shape")

    def test_nicknames_not_object_rejected(self):
        _reject(self, json.dumps({"version": 1, "nicknames": [EVIL]}).encode(),
                "shape")

    def test_nickname_entry_not_object_rejected(self):
        raw = json.dumps({"version": 1, "nicknames": {"sol": EVIL}})
        _reject(self, raw.encode(), "shape")

    def test_non_string_slug_rejected(self):
        raw = json.dumps({"version": 1, "nicknames": {"sol": {"codex": 7}}})
        _reject(self, raw.encode(), "shape")


class CharsetTests(unittest.TestCase):
    def test_uppercase_nickname_rejected(self):
        raw = json.dumps(
            {"version": 1, "nicknames": {"SOL": {"codex": EVIL}}})
        _reject(self, raw.encode(), "charset")

    def test_uppercase_slug_rejected(self):
        raw = json.dumps(
            {"version": 1, "nicknames": {"sol": {"codex": "GPT-5.6"}}})
        _reject(self, raw.encode(), "charset")

    def test_overlong_slug_rejected(self):
        raw = json.dumps(
            {"version": 1, "nicknames": {"sol": {"codex": "a" * 65}}})
        _reject(self, raw.encode(), "charset")

    def test_64_char_slug_accepted(self):
        raw = json.dumps(
            {"version": 1, "nicknames": {"sol": {"codex": "a" * 64}}})
        validate_model_map(raw.encode())

    def test_leading_punctuation_rejected(self):
        raw = json.dumps(
            {"version": 1, "nicknames": {"-sol": {"codex": "x"}}})
        _reject(self, raw.encode(), "charset")

    def test_empty_nickname_rejected(self):
        raw = json.dumps({"version": 1, "nicknames": {"": {"codex": "x"}}})
        _reject(self, raw.encode(), "charset")


class HarnessSetTests(unittest.TestCase):
    def test_unknown_harness_rejected(self):
        raw = json.dumps(
            {"version": 1, "nicknames": {"sol": {"openai": EVIL}}})
        exc = _reject(self, raw.encode(), "harness-set")
        # Strictness serves loud-stop: the alien key itself is not echoed.
        self.assertNotIn("openai", str(exc))

    def test_charset_precedes_harness_set(self):
        raw = json.dumps(
            {"version": 1, "nicknames": {"sol": {"OpenAI": EVIL}}})
        _reject(self, raw.encode(), "charset")


if __name__ == "__main__":
    unittest.main()
