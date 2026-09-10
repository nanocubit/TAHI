# Optional FastLanes backend

TAHI keeps FastLanes optional. The Python reference backend and normal CI do
not require a native FastLanes installation.

The native probe lives in `native/fastlanes_probe` and can be run through the
manual GitHub Actions workflow `TAHI-X optional FastLanes probe` or locally:

```bash
cmake -S native/fastlanes_probe -B build/fastlanes \
  -DFASTLANES_DIR=/path/to/FastLanes
cmake --build build/fastlanes
./build/fastlanes/tahi_fastlanes_probe
```

This step verifies the native include/build boundary only. It does not yet
implement TAHI segment serialization or Python FFI. Those require a pinned
FastLanes API and a separate parity benchmark.
