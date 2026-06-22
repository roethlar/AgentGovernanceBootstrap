"""Deterministic git fixture repos and helpers for discover.py tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

BOOTSTRAP_ROOT = Path(__file__).resolve().parent.parent
DISCOVER = BOOTSTRAP_ROOT / "tools" / "discover.py"

FIXED_ENV = {
    "GIT_AUTHOR_NAME": "Fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.com",
    "GIT_COMMITTER_NAME": "Fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.com",
    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00 +0000",
    "GIT_COMMITTER_DATE": "2026-01-01T00:00:00 +0000",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}


def _git(repo, *args):
    env = dict(os.environ)
    env.update(FIXED_ENV)
    subprocess.run(["git", *args], cwd=repo, env=env, check=True,
                   capture_output=True)


def _write(repo, rel, content):
    p = Path(repo) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def make_greenfield_repo(path):
    """No governance files. Has package.json scripts and a Makefile."""
    path = Path(path)
    path.mkdir(parents=True)
    _git(path, "init", "-q", "-b", "main")
    _write(path, "README.md", "# Greenfield Fixture\n")
    _write(path, "src/main.py", "print('hello')\n")
    _write(path, "package.json",
           '{"name": "fixture", "scripts": '
           '{"test": "node test.js", "lint": "eslint .", "deploy": "scp ."}}\n')
    _write(path, "Makefile", "test:\n\tnode test.js\n\nclean:\n\trm -rf dist\n")
    _git(path, "add", "-A")
    _git(path, "commit", "-q", "-m", "fixture: greenfield")
    return path


def make_governance_repo(path):
    """Miniature of the Blit pattern: AGENTS.md, CLAUDE.md, STATE/DEVLOG/DECISIONS,
    .claude/commands, a Cargo workspace, and a sensitive-named file."""
    path = Path(path)
    path.mkdir(parents=True)
    _git(path, "init", "-q", "-b", "main")
    _write(path, "README.md", "# Governance Fixture\n")
    _write(path, "AGENTS.md", "# Agent contract\n\nRead docs/STATE.md first.\n")
    _write(path, "CLAUDE.md", "@AGENTS.md\n")
    _write(path, "docs/STATE.md", "# STATE\n\n## Now\n- fixture work\n")
    _write(path, "DEVLOG.md", "# DEVLOG\n\n2026-01-01 entry.\n")
    _write(path, "docs/DECISIONS.md", "# Decisions\n")
    _write(path, ".claude/commands/catchup.md", "Re-ground from STATE.md.\n")
    _write(path, "Cargo.toml", '[workspace]\nmembers = ["crates/app"]\n')
    _write(path, "crates/app/Cargo.toml",
           '[package]\nname = "app"\nversion = "0.1.0"\n')
    _write(path, "crates/app/src/lib.rs", "pub fn x() {}\n")
    _write(path, "deploy/secrets.yaml", "placeholder: none\n")
    _git(path, "add", "-A")
    _git(path, "commit", "-q", "-m", "fixture: governance")
    return path


def run_discover(repo, *extra_args):
    """Run discover.py as a subprocess (tests the real CLI). Returns manifest dict."""
    proc = subprocess.run(
        [sys.executable, str(DISCOVER), str(repo), *extra_args],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssertionError(
            f"discover.py failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    manifest_path = Path(repo) / ".bootstrap-tmp" / "repo-discovery-manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def normalize_manifest(manifest):
    """Blank fields that legitimately vary between runs/machines."""
    m = json.loads(json.dumps(manifest))
    m["generatedAt"] = "<NORMALIZED>"
    m["validated_against"]["date"] = "<NORMALIZED>"
    m["validated_against"]["commit"] = "<NORMALIZED>"
    m["git"]["commit"] = "<NORMALIZED>"
    m["repo"]["root"] = "<REPO_ROOT>"
    m["bootstrapRepoPath"] = "<BOOTSTRAP_REPO>"
    m["harvestRepoPath"] = "<NORMALIZED>"
    # currentVersion tracks the toolkit's template stamp and changes on every
    # bump; blank it so goldens stay stable. The version mechanism itself is
    # guarded by TestAgentsTemplateStatus, not the golden contract.
    m["agentsTemplate"]["currentVersion"] = "<NORMALIZED>"
    return m
