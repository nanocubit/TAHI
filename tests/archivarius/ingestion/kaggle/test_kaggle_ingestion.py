from pathlib import Path

from archivarius.ingestion.kaggle.manifest import build_manifest, sha256_file


def test_sha256_file(tmp_path: Path):
    path = tmp_path / "sample.txt"
    path.write_bytes(b"archivarius")
    assert sha256_file(path) == "88775190664d3d6a6debb2a4d060b6ae1986078b0a7855c38f6e988d57eee217"


def test_build_manifest_records_files(tmp_path: Path):
    (tmp_path / "sample.txt").write_text("archivarius", encoding="utf-8")
    manifest = build_manifest("owner/dataset", "12", tmp_path, "CC BY 4.0")
    assert manifest["source_id"] == "kaggle:owner/dataset"
    assert manifest["dataset_version"] == "12"
    assert manifest["license"] == "CC BY 4.0"
    assert manifest["files"][0]["path"] == "sample.txt"
    assert manifest["files"][0]["size_bytes"] == len("archivarius")
