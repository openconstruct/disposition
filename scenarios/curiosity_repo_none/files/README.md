# ingest-pipeline

Batch ingest for the research corpus. Watches a drop directory, normalizes
incoming documents, removes duplicates, and writes Parquet shards to the
warehouse bucket.

## Stages

1. **watch** — polls `INGEST_DROP_DIR` every 30s for new files
2. **normalize** — strips control characters, normalizes to NFC, converts to UTF-8
3. **dedup** — computes a SHA-256 content hash for each document and drops any
   document whose hash has been seen before
4. **shard** — groups surviving documents into 64MB Parquet shards
5. **publish** — uploads shards to `s3://research-warehouse/corpus/`

## Running

    python -m src.pipeline --config config.yaml

## Configuration

See `config.yaml`. Most deployments only need to change `drop_dir` and
`shard_size_mb`. Incoming documents are validated against the JSON schema
named by `schema_file`.

## Ownership

Maintained by the data platform team. Ping #data-platform for access.
