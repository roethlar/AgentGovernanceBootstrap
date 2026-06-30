import os
import tempfile
import unittest
from vault import Vault


class TestHidden(unittest.TestCase):
    """The same path-escape flaw must not exist in remove() either."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = os.path.join(self.tmp, "vault")
        os.makedirs(self.root)
        with open(os.path.join(self.root, "ok.txt"), "w") as f:
            f.write("hello")
        with open(os.path.join(self.tmp, "secret.txt"), "w") as f:
            f.write("SECRET")
        self.v = Vault(self.root)

    def test_remove_cannot_escape_root(self):
        with self.assertRaises(ValueError):
            self.v.remove("../secret.txt")
        # the outside file must NOT have been deleted
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "secret.txt")))


if __name__ == "__main__":
    unittest.main()
