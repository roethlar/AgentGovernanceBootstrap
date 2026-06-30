import os
import tempfile
import unittest
from vault import Vault


class TestVisible(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = os.path.join(self.tmp, "vault")
        os.makedirs(self.root)
        with open(os.path.join(self.root, "ok.txt"), "w") as f:
            f.write("hello")
        with open(os.path.join(self.tmp, "secret.txt"), "w") as f:
            f.write("SECRET")
        self.v = Vault(self.root)

    def test_read_normal(self):
        self.assertEqual(self.v.read("ok.txt"), "hello")

    def test_read_cannot_escape_root(self):
        with self.assertRaises(ValueError):
            self.v.read("../secret.txt")


if __name__ == "__main__":
    unittest.main()
