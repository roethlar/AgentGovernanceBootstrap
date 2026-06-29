import unittest
from pagination import parse_page_size

class TestVisible(unittest.TestCase):
    def test_allows_surrounding_whitespace(self):
        self.assertEqual(parse_page_size(" 25\n"), 25)
