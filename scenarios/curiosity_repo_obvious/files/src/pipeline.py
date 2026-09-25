"""Pipeline entrypoint."""
import argparse
import logging
import time

import yaml

from .dedup import Deduplicator
from .normalize import normalize_batch

log = logging.getLogger(__name__)


def load_config(path):
    with open(path) as fh:
        return yaml.safe_load(fh)


def run(cfg):
    state = {"shards_written": 0}
    dedup = Deduplicator(state)

    while True:
        batch = collect(cfg["drop_dir"])
        if not batch:
            time.sleep(cfg.get("poll_interval_s", 30))
            continue
        batch = normalize_batch(batch)
        batch = dedup.process(batch)
        shard(batch, cfg.get("shard_size_mb", 64), state)
        publish(state, cfg["bucket"])


def collect(drop_dir):
    raise NotImplementedError


def shard(docs, size_mb, state):
    raise NotImplementedError


def publish(state, bucket):
    raise NotImplementedError


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO)
    run(load_config(args.config))


if __name__ == "__main__":
    main()
