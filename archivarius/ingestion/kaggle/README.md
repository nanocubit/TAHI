# Kaggle ingestion gateway

This package downloads a pinned Kaggle dataset version, records provenance, validates files, computes SHA-256, and optionally uploads immutable artifacts to Google Cloud Storage.

## Credentials

Do not commit credentials. Configure:

- `KAGGLE_API_TOKEN` for Kaggle API access.
- `GOOGLE_APPLICATION_CREDENTIALS` or workload identity for GCS.
- `GCS_BUCKET` for the destination bucket.

## Example

```bash
python download.py --dataset owner/dataset --version 12 --out ./data --manifest ./manifest.json
python validate.py --manifest ./manifest.json
python upload_gcs.py --manifest ./manifest.json --prefix raw/kaggle
```

The manifest records dataset reference, version, license metadata when available, local file hashes, retrieval time, and GCS URIs. Raw files are immutable; derived features and TAHI snapshots belong to later pipeline stages.
