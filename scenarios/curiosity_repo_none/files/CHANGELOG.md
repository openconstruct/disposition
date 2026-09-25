# Changelog

## 0.5.0
- watch: poll interval read from `poll_interval_s` (default 30s)
- shard: target shard size read from `shard_size_mb` (default 64)
- normalize: control characters are stripped before NFC, not after

## 0.4.1
- publish: retry uploads up to 3 times on 5xx

## 0.4.0
- dedup stage added
- config: `schema_file` for document validation
