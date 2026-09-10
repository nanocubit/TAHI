"""Provenance and manifest helpers for Kaggle ingestion."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(dataset: str, version: str | None, root: Path, license_name: str | None = None) -> dict[str, Any]:
    files = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        files.append({
            "path": str(path.relative_to(root)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return {
        "source_id": f"kaggle:{dataset}",
        "provider": "kaggle",
        "dataset_ref": dataset,
        "dataset_version": version,
        "license": license_name,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "status": "downloaded",
    }


def write_manifest(manifest: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
