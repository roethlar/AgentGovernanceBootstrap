#!/usr/bin/env python3
"""Governance checker. The mechanical half of the v2 toolkit.

Judgment lives in prose (the agent discovers, drafts, migrates); this script only
verifies what a machine can verify:

  verify (default)  upstream-owned files match their frozen checksums (drift
                    detection), word budgets hold, markdown pointers in governance
                    files resolve, state.md carries an Updated: stamp.
  --freeze          create or update .agents/governance.json after an authorized
                    install or refresh. Freezing is itself a gated act: only the
                    install/refresh procedures call it.

Installed at .agents/check.py in target repos. Stdlib only; runs anywhere Python 3
does. Exit 0 clean, 1 on any error. Pointers are checked only in markdown-link form
[text](path) — a path in backticks is prose, not a checkable pointer.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = ".agents/governance.json"

DEFAULT_MANIFEST = {
    "version": "2.0.0",
    "source": "https://github.com/roethlar/AgentGovernanceBootstrap",
    "upstream": {
        "AGENTS.md": None,
        ".agents/check.py": None,
        ".agents/playbooks/operators.md": None,
    },
    "budgets": {
        "AGENTS.md": 400,
        ".agents/context.md": 700,
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word_count(text: str) -> int:
    # HTML comments are plumbing (budget notices, template hints), not guidance.
    return len(re.sub(r"<!--.*?-->", " ", text, flags=re.S).split())


def check_pointers(root: Path, md: Path, errors: list) -> None:
    text = md.read_text(encoding="utf-8")
    for match in re.finditer(r"\[[^\]]*\]\(([^)#\s]+)\)", text):
        target = match.group(1)
        if re.match(r"[a-z][a-z0-9+.-]*://", target):
            continue  # URL, not a file pointer
        if not (md.parent / target).exists() and not (root / target).exists():
            errors.append(f"{md.relative_to(root)}: broken pointer -> {target}")


def freeze(root: Path, manifest_path: Path) -> int:
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = json.loads(json.dumps(DEFAULT_MANIFEST))
    missing = []
    for rel in manifest["upstream"]:
        path = root / rel
        if path.exists():
            manifest["upstream"][rel] = sha256(path)
        else:
            missing.append(rel)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if missing:
        print(f"frozen with missing upstream files: {', '.join(missing)}")
        return 1
    print(f"manifest frozen: {manifest_path}")
    return 0


def verify(root: Path, manifest_path: Path) -> int:
    if not manifest_path.exists():
        print(f"error: no manifest at {MANIFEST}; run install first (see procedures/install.md)")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors, warnings = [], []

    for rel, frozen in manifest.get("upstream", {}).items():
        path = root / rel
        if not path.exists():
            errors.append(f"missing upstream-owned file: {rel}")
        elif frozen is None:
            errors.append(f"never frozen: {rel} (run --freeze during install/refresh)")
        elif sha256(path) != frozen:
            errors.append(
                f"drift: {rel} differs from its frozen upstream copy "
                f"(hand-edit or unrecorded refresh); reconcile before continuing"
            )

    for rel, limit in manifest.get("budgets", {}).items():
        path = root / rel
        if path.exists():
            count = word_count(path.read_text(encoding="utf-8"))
            if count > limit:
                errors.append(
                    f"over budget: {rel} is {count} words (limit {limit}); evict before adding"
                )

    agents_dir = root / ".agents"
    for md in sorted(agents_dir.rglob("*.md")) if agents_dir.exists() else []:
        check_pointers(root, md, errors)
    if (root / "AGENTS.md").exists():
        check_pointers(root, root / "AGENTS.md", errors)

    state = root / ".agents" / "state.md"
    if state.exists() and not re.search(
        r"^Updated:\s*\S", state.read_text(encoding="utf-8"), flags=re.M
    ):
        warnings.append(".agents/state.md has no 'Updated:' stamp; handoffs are undatable")

    for warning in warnings:
        print(f"warn: {warning}")
    for error in errors:
        print(f"FAIL: {error}")
    if errors:
        return 1
    print("governance clean")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repo root (default: cwd)")
    parser.add_argument("--freeze", action="store_true", help="write/update the manifest")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest_path = root / MANIFEST
    return freeze(root, manifest_path) if args.freeze else verify(root, manifest_path)


if __name__ == "__main__":
    sys.exit(main())
