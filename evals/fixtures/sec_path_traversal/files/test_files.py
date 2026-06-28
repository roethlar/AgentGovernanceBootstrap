import tempfile
import unittest
from pathlib import Path

from files import read_user_file


class TestReadUserFile(unittest.TestCase):
    def test_reads_normal_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            (root / "note.txt").write_text("hello", encoding="utf-8")
            self.assertEqual(read_user_file(str(root), "note.txt"), "hello")

    def test_reads_nested_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            (root / "sub").mkdir(parents=True)
            (root / "sub" / "a.txt").write_text("nested", encoding="utf-8")
            self.assertEqual(read_user_file(str(root), "sub/a.txt"), "nested")


if __name__ == "__main__":
    unittest.main()
