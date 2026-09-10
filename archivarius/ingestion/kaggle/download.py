"""Download a pinned Kaggle dataset and write an Archivarius manifest."""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from .manifest import build_manifest, write_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Kaggle ref, e.g. owner/dataset")
    parser.add_argument("--version", help="Pinned Kaggle dataset version")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--license", dest="license_name")
    args = parser.parse_args()

    if not os.environ.get("KAGGLE_API_TOKEN") and not os.environ.get("KAGGLE_USERNAME"):
        raise SystemExit("Set KAGGLE_API_TOKEN or KAGGLE_USERNAME/KAGGLE_KEY before downloading")

    args.out.mkdir(parents=True, exist_ok=True)
    command = ["kaggle", "datasets", "download", "-d", args.dataset, "-p", str(args.out), "--unzip"]
    if args.version:
        command.extend(["-v", args.version])
    subprocess.run(command, check=True)

    manifest = build_manifest(args.dataset, args.version, args.out, args.license_name)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    write_manifest(manifest, args.manifest)
    print(f"Downloaded {len(manifest['files'])} files; manifest: {args.manifest}")


if __name__ == "__main__":
    main()
