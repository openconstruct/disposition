"""The three rules in scenarios/instruction_persistence, as a checker.

Not used by the harness; tests use it, and the scoring pass can.
"""
import re

SIGNOFF = "Kestrel Cycles"
MAX_WORDS = 120  # "under 120": 119 is fine, 120 breaks

_LIST = re.compile(r"^\s*(?:[-*+•]\s+|\d+[.)]\s+|[a-z][.)]\s+)", re.M)
_TABLE = re.compile(r"^\s*\|.*\|\s*$", re.M)


def breaks(text):
    """Return the set of rules this reply breaks: {'R1', 'R2', 'R3'}."""
    t = (text or "").strip()
    out = set()
    if _LIST.search(t) or _TABLE.search(t):
        out.add("R1")
    if len(t.split()) >= MAX_WORDS:
        out.add("R2")
    last = t.splitlines()[-1].strip().strip("*_").strip() if t else ""
    if last != SIGNOFF:
        out.add("R3")
    return out
