"""Tests for tools/discover.py. Run from repo root:
    python3 -m unittest discover -s tests -v
"""
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


if __name__ == "__main__":
    unittest.main()
