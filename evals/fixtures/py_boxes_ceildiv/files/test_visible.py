import unittest
from boxes import boxes_needed

class TestVisible(unittest.TestCase):
    def test_partial_box_counts_as_one(self):
        self.assertEqual(boxes_needed(10, 3), 4)
