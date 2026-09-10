"""Validate downloaded Kaggle files against an Archivarius manifest."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from manifest import sha256_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    failures = []
    for item in manifest.get("files", []):
        path = args.root / item["path"]
        if not path.is_file():
            failures.append(f"missing: {path}")
            continue
        actual_size = path.stat().st_size
        actual_hash = sha256_file(path)
        if actual_size != item["size_bytes"]:
            failures.append(f"size mismatch: {path}")
        if actual_hash != item["sha256"]:
            failures.append(f"sha256 mismatch: {path}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print(f"OK: validated {len(manifest.get('files', []))} files")


if __name__ == "__main__":
    main()
