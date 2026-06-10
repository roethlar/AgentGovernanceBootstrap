"""Regenerate golden manifests. Run after intentionally changing discover.py
output or the fixtures:    python3 tests/regen_golden.py
Then review the diff before committing - the golden files are the contract."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixtures  # noqa: E402

GOLDEN = Path(__file__).resolve().parent / "golden"


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        pairs = [
            ("greenfield-manifest.json",
             fixtures.run_discover(fixtures.make_greenfield_repo(base / "green"))),
            ("governance-manifest.json",
             fixtures.run_discover(fixtures.make_governance_repo(base / "gov"))),
        ]
        for name, manifest in pairs:
            normalized = fixtures.normalize_manifest(manifest)
            (GOLDEN / name).write_text(
                json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
            print(f"wrote tests/golden/{name}")


if __name__ == "__main__":
    main()
