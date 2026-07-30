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


def build_dev_repo(base):
    """The throwaway development repo the script publishes from."""
    dev = base / "dev"
    dev_tools = dev / "tools"
    dev_tools.mkdir(parents=True)
    # the script resolves the dev repo from its own location
    shutil.copy2(SCRIPT, dev_tools / "publish.py")
    for d in ("templates/x", "procedures"):
        (dev / d).mkdir(parents=True)
    (dev / "templates" / "x" / "a.md").write_text("a\n")
    (dev / "procedures" / "p.md").write_text("p\n")
    # The product front page is a product-only file that publishes to
    # README.md; the dev repo's own README.md never crosses.
    (dev / "product").mkdir()
    (dev / "product" / "README.md").write_text("product front page\n")
    (dev / "product" / ".gitignore").write_text(".DS_Store\n")
    (dev / "README.md").write_text("dev-facing readme\n")
    # One canonical license at the dev repo's root ships to the product
    # repo — mirroring clears everything the publish set does not carry.
    (dev / "LICENSE").write_text("MIT\n")
    # The front page references assets by relative path.
    (dev / "assets").mkdir()
    (dev / "assets" / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (dev / "tools" / "keep.py").write_text("x = 1\n")
    # Issue templates publish (2026-07-29 decision: Bixi is the feedback
    # inbox); the rest of .github/ is dev-only and must never cross.
    (dev / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)
    (dev / ".github" / "ISSUE_TEMPLATE" / "defect.md").write_text("d\n")
    (dev / ".github" / "workflows").mkdir()
    (dev / ".github" / "workflows" / "ci.yml").write_text("ci\n")
    # dev-only content that must never publish
    (dev / "docs").mkdir()
    (dev / "docs" / "dev-notes.md").write_text("secret dev stuff\n")
    (dev / ".agents").mkdir()
    (dev / ".agents" / "decisions.md").write_text("internal\n")
    (dev / "tools" / "__pycache__").mkdir()
    (dev / "tools" / "__pycache__" / "junk.pyc").write_text("j\n")
    return dev, dev_tools


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.dev, self.dev_tools = build_dev_repo(base)
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
        # the root LICENSE ships — the product repo is public
        self.assertTrue((self.product / "LICENSE").exists())
        # assets ship, or every image on the front page is a broken link
        self.assertTrue((self.product / "assets" / "logo.png").exists())
        self.assertTrue((self.product / "tools" / "keep.py").exists())
        self.assertTrue((self.product / "tools" / "publish.py").exists())
        # issue templates ship; the rest of .github/ never crosses
        self.assertTrue((self.product / ".github" / "ISSUE_TEMPLATE"
                         / "defect.md").exists())
        self.assertFalse((self.product / ".github" / "workflows").exists())
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

    def test_os_junk_in_the_product_repo_does_not_block_a_release(self):
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertTrue((self.product / ".gitignore").is_file())
        # Finder and Explorer drop these just by opening the folder. Untracked,
        # they trip the dirty-tree refusal and stop the next release; ignored,
        # they are invisible to it.
        (self.product / ".DS_Store").write_bytes(b"\x00")
        (self.dev / "product" / "README.md").write_text("front page v2\n")
        again = self.run_publish("--no-push")
        self.assertEqual(0, again.returncode, again.stderr)
        self.assertEqual("front page v2\n", (self.product / "README.md").read_text())

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


class ProductRemoteFreshnessTests(unittest.TestCase):
    """Releases land on the product remote from other machines too. A stale
    checkout fast-forwards before mirroring, truly split histories refuse
    before anything is touched, and an unreachable remote is a caveat,
    never a block."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.dev, self.dev_tools = build_dev_repo(base)
        self.origin = base / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)],
                       check=True, capture_output=True)
        self.seed = self.clone(base / "seed")
        (self.seed / "r1.txt").write_text("one\n")
        git(self.seed, "add", "-A")
        git(self.seed, "commit", "-q", "-m", "release one")
        git(self.seed, "push", "-q", "-u", "origin", "HEAD")
        self.product = self.clone(base / "product")

    def clone(self, dest):
        subprocess.run(["git", "clone", "-q", str(self.origin), str(dest)],
                       check=True, capture_output=True)
        git(dest, "config", "user.email", "t@example.invalid")
        git(dest, "config", "user.name", "T")
        return dest

    def advance_remote(self):
        (self.seed / "r2.txt").write_text("two\n")
        git(self.seed, "add", "-A")
        git(self.seed, "commit", "-q", "-m", "release two")
        git(self.seed, "push", "-q")

    def run_publish(self, *args):
        return subprocess.run(
            [sys.executable, str(self.dev_tools / "publish.py"),
             *(str(a) for a in args)],
            capture_output=True, text=True)

    def test_stale_checkout_fast_forwards_before_the_release(self):
        self.advance_remote()
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        subjects = git(self.product, "log", "--format=%s").stdout.splitlines()
        self.assertIn("release two", subjects)
        self.assertTrue(subjects[0].startswith("release "), subjects[0])
        # brought up to date, not merged: release history stays linear
        self.assertEqual("", git(self.product, "rev-list", "--merges",
                                 "HEAD").stdout.strip())

    def test_split_histories_refuse_before_touching_anything(self):
        (self.product / "local.txt").write_text("local\n")
        git(self.product, "add", "-A")
        git(self.product, "commit", "-q", "-m", "local only")
        self.advance_remote()
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("reconcile", proc.stderr)
        self.assertTrue((self.product / "local.txt").exists())
        self.assertFalse((self.product / "templates").exists())

    def test_unreachable_remote_is_a_caveat_never_a_block(self):
        git(self.product, "remote", "set-url", "origin",
            str(Path(self.tmp.name) / "gone.git"))
        proc = self.run_publish(self.product, "--no-push")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("could not reach", proc.stderr)
        self.assertIn("release ", git(self.product, "log", "--format=%s",
                                      "-1").stdout)


if __name__ == "__main__":
    unittest.main()
