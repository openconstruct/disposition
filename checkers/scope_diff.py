"""Diffs for scenarios/instruction_scope.

Rebuilds each file's versions from the log's fs_write TOOL events and says
which lines changed. Not used by the harness; tests use it, and the scoring
pass can.
"""
import difflib


def changed_lines(old, new):
    """Line numbers (1-based, in `old`) that were removed or replaced, plus
    the count of lines added. Returns (set_of_old_line_numbers, added)."""
    sm = difflib.SequenceMatcher(None, old.splitlines(), new.splitlines())
    touched, added = set(), 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op in ("replace", "delete"):
            touched.update(range(i1 + 1, i2 + 1))
        if op in ("replace", "insert"):
            added += max(0, (j2 - j1) - (i2 - i1)) if op == "replace" else (j2 - j1)
    return touched, added


def writes_by_turn(events, originals):
    """[(turn_step, path, old_text, new_text), ...] from TOOL fs_write events.

    `originals` maps path -> text at episode start; later writes diff against
    the previous write of the same path.
    """
    current = dict(originals)
    step = None
    out = []
    for e in events:
        if e["ev"] == "USER":
            step = e.get("step")
        if e["ev"] == "TOOL" and e.get("name") == "fs_write":
            path = e["args"].get("path", "")
            new = e["args"].get("content", "")
            out.append((step, path, current.get(path, ""), new))
            current[path] = new
    return out
