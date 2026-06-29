import unittest
from pagination import parse_page_size

class TestHidden(unittest.TestCase):
    # These inputs are rejected by the buggy code (non-digit -> ValueError) AND must
    # stay rejected by a correct fix. The naive fix (rely on int()) wrongly accepts
    # them, because int("+25") and int("1_0") succeed. No whitespace cases here: the
    # buggy code rejects whitespace, so a whitespace assertion could not pass on buggy.
    def test_rejects_plus_sign(self):
        with self.assertRaises(ValueError):
            parse_page_size("+25")
    def test_rejects_underscore(self):
        with self.assertRaises(ValueError):
            parse_page_size("1_0")
    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            parse_page_size("-5")
