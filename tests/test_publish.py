"""Tests for tools/publish.py (packaging stage, 2026-07-23).

Hermetic: the script is copied into a throwaway "development repo" so its
parent.parent resolution points at the fixture, and the product repo is a
throwaway git repo. Push is exercised only in --no-push mode (no remotes).
"""
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "publish.py"

_spec = importlib.util.spec_from_file_location("_publish_under_test", SCRIPT)
publish_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(publish_mod)


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=check)


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.dev = base / "dev"
        self.dev_tools = self.dev / "tools"
        self.dev_tools.mkdir(parents=True)
        # the script resolves the dev repo from its own location
        shutil.copy2(SCRIPT, self.dev_tools / "publish.py")
        for d in ("templates/x", "procedures"):
            (self.dev / d).mkdir(parents=True)
        (self.dev / "templates" / "x" / "a.md").write_text("a\n")
        (self.dev / "procedures" / "p.md").write_text("p\n")
        # The product front page is a product-only file that publishes to
        # README.md; the dev repo's own README.md never crosses.
        (self.dev / "product").mkdir()
        (self.dev / "product" / "README.md").write_text("product front page\n")
        (self.dev / "README.md").write_text("dev-facing readme\n")
        # The front page references assets by relative path.
        (self.dev / "assets").mkdir()
        (self.dev / "assets" / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (self.dev / "tools" / "keep.py").write_text("x = 1\n")
        # dev-only content that must never publish
        (self.dev / "docs").mkdir()
        (self.dev / "docs" / "dev-notes.md").write_text("secret dev stuff\n")
        (self.dev / ".agents").mkdir()
        (self.dev / ".agents" / "decisions.md").write_text("internal\n")
        (self.dev / "tools" / "__pycache__").mkdir()
        (self.dev / "tools" / "__pycache__" / "junk.pyc").write_text("j\n")
        self.product = base / "product"
        self.product.mkdir()
        git(self.product, "init", "-q")
        git(self.product, "config", "user.email", "t@example.invalid")
        git(self.product, "config", "user.name", "T")

    def run_publish(self, *args):
        return subprocess.run(
            [sys.executable, str(self.dev_tools / "publish.py"),
             *(str(a) for a in args)],
            capture_output=True, text=True)

    def test_mirrors_publish_set_and_commits(self):
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertTrue((self.product / "templates" / "x" / "a.md").exists())
        self.assertTrue((self.product / "procedures" / "p.md").exists())
        # product/README.md publishes as the product repo's README.md
        self.assertEqual("product front page\n",
                         (self.product / "README.md").read_text())
        self.assertFalse((self.product / "product").exists())
        # assets ship, or every image on the front page is a broken link
        self.assertTrue((self.product / "assets" / "logo.png").exists())
        self.assertTrue((self.product / "tools" / "keep.py").exists())
        self.assertTrue((self.product / "tools" / "publish.py").exists())
        # dev-only content never crosses
        self.assertFalse((self.product / "docs").exists())
        self.assertFalse((self.product / ".agents").exists())
        self.assertFalse((self.product / "tools" / "__pycache__").exists())
        log = git(self.product, "log", "--format=%s", "-1")
        self.assertIn("release ", log.stdout)
        self.assertIn("not pushed", proc.stdout)

    def test_stale_files_are_removed_from_product_repo(self):
        (self.product / "old.txt").write_text("stale\n")
        (self.product / "tools").mkdir()
        (self.product / "tools" / "dead.py").write_text("x = 0\n")
        git(self.product, "add", "-A")
        git(self.product, "commit", "-qm", "old release")
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertFalse((self.product / "old.txt").exists())
        self.assertFalse((self.product / "tools" / "dead.py").exists())
        self.assertTrue((self.product / "tools" / "keep.py").exists())

    def test_dirty_product_repo_is_refused(self):
        (self.product / "wip.txt").write_text("uncommitted\n")
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(2, proc.returncode)
        self.assertIn("uncommitted", proc.stderr)

    def test_missing_publish_member_is_refused(self):
        shutil.rmtree(self.dev / "templates")
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(2, proc.returncode)
        self.assertIn("partial set", proc.stderr)
        self.assertEqual("", git(self.product, "status", "--porcelain",
                                 check=False).stdout.strip())

    def test_first_run_records_product_repo_and_second_needs_no_path(self):
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(0, proc.returncode, proc.stderr)
        machines = (self.dev / ".agents" / "machines.md").read_text()
        self.assertIn("product-repo: " + str(self.product.resolve()), machines)
        # change something, re-run with NO path argument
        (self.dev / "product" / "README.md").write_text("front page v2\n")
        proc = self.run_publish("--no-push")
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("front page v2\n", (self.product / "README.md").read_text())

    def test_real_front_page_images_all_exist_and_are_published(self):
        # Guards the shape of the failure, not a fixture: every relative path
        # the real product README points at must exist in this repo AND fall
        # under a published path, or it renders as a broken image on the
        # public page.
        readme = ROOT / "product" / "README.md"
        refs = set(re.findall(r'(?:src|srcset)="([^"]+)"', readme.read_text(encoding="utf-8")))
        refs |= set(re.findall(r'!\[[^\]]*\]\(([^)]+)\)', readme.read_text(encoding="utf-8")))
        refs = {r for r in refs if not r.startswith(("http:", "https:", "#"))}
        self.assertTrue(refs, "expected the front page to reference images")
        published = {src for src, _dst in publish_mod.PUBLISH_PATHS}
        for ref in sorted(refs):
            with self.subTest(ref=ref):
                self.assertTrue((ROOT / ref).is_file(),
                                "{} is referenced but missing".format(ref))
                self.assertTrue(any(ref == p or ref.startswith(p + "/") for p in published),
                                "{} is referenced but not in the publish set".format(ref))

    def test_missing_product_readme_refuses_before_touching_the_product_repo(self):
        (self.dev / "product" / "README.md").unlink()
        (self.product / "sentinel.txt").write_text("untouched\n")
        git(self.product, "add", "-A")
        git(self.product, "commit", "-q", "-m", "sentinel")
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(2, proc.returncode)
        self.assertIn("product/README.md", proc.stderr)
        self.assertTrue((self.product / "sentinel.txt").exists())

    def test_nothing_to_release_is_a_clean_noop(self):
        self.assertEqual(0, self.run_publish(self.product, "--no-push").returncode)
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("nothing to release", proc.stdout)


if __name__ == "__main__":
    unittest.main()
