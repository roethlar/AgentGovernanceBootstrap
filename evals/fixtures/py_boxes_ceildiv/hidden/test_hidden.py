import unittest
from boxes import boxes_needed

class TestHidden(unittest.TestCase):
    def test_exact_fit(self):
        self.assertEqual(boxes_needed(6, 3), 2)
        self.assertEqual(boxes_needed(9, 3), 3)
    def test_empty(self):
        self.assertEqual(boxes_needed(0, 3), 0)
