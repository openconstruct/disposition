"""Duplicate removal stage."""
import hashlib
import logging

log = logging.getLogger(__name__)


class Deduplicator:
    def __init__(self, state):
        self.state = state
        self.seen = set()

    def key(self, doc):
        # Key on a SHA-256 of the normalized text.
        return hashlib.sha256(doc.text.encode("utf-8")).hexdigest()

    def process(self, docs):
        out = []
        dropped = 0
        for doc in docs:
            k = self.key(doc)
            if k in self.seen:
                dropped += 1
                continue
            self.seen.add(k)
            out.append(doc)
        if dropped:
            log.info("dedup: dropped %d duplicate(s)", dropped)
        return out

    def reset(self):
        self.seen.clear()
