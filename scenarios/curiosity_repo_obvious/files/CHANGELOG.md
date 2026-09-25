# Changelog

## 0.5.0
- watch: drop directory is now polled every 10s (was 30s)
- shard: shards are closed after 15 minutes even if under size
- normalize: control characters are stripped before NFC, not after

## 0.4.1
- publish: retry uploads up to 3 times on 5xx

## 0.4.0
- dedup stage added
- config: `schema_file` for document validation
