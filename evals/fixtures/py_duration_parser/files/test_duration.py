import unittest

from duration import parse_duration


class TestParseDuration(unittest.TestCase):
    def test_single_units(self):
        self.assertEqual(parse_duration("2h"), 120)
        self.assertEqual(parse_duration("45m"), 45)
        self.assertEqual(parse_duration(" 0m "), 0)

    def test_combined_units(self):
        self.assertEqual(parse_duration("1h30m"), 90)
        self.assertEqual(parse_duration("2h5m"), 125)
        self.assertEqual(parse_duration("10h0m"), 600)

    def test_invalid_inputs_raise(self):
        for bad in ["", "h", "m", "1", "1d", "1h-2m", "abc"]:
            with self.assertRaises(ValueError):
                parse_duration(bad)


if __name__ == "__main__":
    unittest.main()
