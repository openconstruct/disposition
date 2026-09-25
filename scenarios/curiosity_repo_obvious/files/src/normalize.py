"""Text normalization stage."""
import unicodedata

CONTROL = {c for c in range(0x20) if c not in (0x09, 0x0A, 0x0D)}


def clean(text):
    text = "".join(ch for ch in text if ord(ch) not in CONTROL)
    return unicodedata.normalize("NFC", text)


def normalize_batch(docs):
    for doc in docs:
        doc.text = clean(doc.text)
    return docs
