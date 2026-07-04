"""Guards for tests/_pyshim.py's interpreter probe: a python3 that hangs or
is missing must read as not-working (so the shim installs), never escape as
an exception from setUpModule."""
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _pyshim  # noqa: E402


class TestPython3Probe(unittest.TestCase):
    def test_hung_python3_reads_as_not_working(self):
        with mock.patch.object(
                _pyshim.subprocess, "run",
                side_effect=subprocess.TimeoutExpired(cmd="python3", timeout=30)):
            self.assertFalse(_pyshim._python3_works())

    def test_missing_python3_reads_as_not_working(self):
        with mock.patch.object(
                _pyshim.subprocess, "run", side_effect=FileNotFoundError()):
            self.assertFalse(_pyshim._python3_works())
