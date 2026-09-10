"""Validate and upload Kaggle raw artifacts to immutable GCS objects."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from manifest import sha256_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", default="raw/kaggle")
    parser.add_argument("--output-manifest", type=Path)
    args = parser.parse_args()

    try:
        from google.cloud import storage
    except ImportError as exc:
        raise SystemExit("Install google-cloud-storage to upload to GCS") from exc

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    client = storage.Client()
    bucket = client.bucket(args.bucket)
    dataset = manifest["dataset_ref"].replace("/", "__")
    version = manifest.get("dataset_version") or "unversioned"

    for item in manifest.get("files", []):
        local = args.root / item["path"]
        if not local.is_file():
            raise SystemExit(f"Missing file: {local}")
        if local.stat().st_size != item["size_bytes"] or sha256_file(local) != item["sha256"]:
            raise SystemExit(f"Checksum validation failed: {local}")

        object_name = f"{args.prefix}/{dataset}/v{version}/{item['sha256']}/{item['path']}"
        blob = bucket.blob(object_name)
        blob.upload_from_filename(str(local), if_generation_match=0)
        item["gcs_uri"] = f"gs://{args.bucket}/{object_name}"

    manifest["status"] = "uploaded"
    output = args.output_manifest or args.manifest
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Uploaded {len(manifest.get('files', []))} files to gs://{args.bucket}/{args.prefix}")


if __name__ == "__main__":
    main()
