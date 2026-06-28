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


if __name__ == "__main__":
    unittest.main()
