"""Checker for scenarios/creativity_merge. Not used by the harness.

`check(csv_text)` compares a merged member list against checkers/merge_truth.json
(48 people, two of them different people both called Sol Rossi).
"""
import csv
import io
import json
import re
from pathlib import Path

TRUTH = json.loads((Path(__file__).parent / "merge_truth.json").read_text())


def _phone(s):
    d = re.sub(r"\D", "", s or "")
    if d.startswith("44"):
        d = "0" + d[2:]
    return d


def check(csv_text):
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    lower = [{(k or "").strip().lower(): (v or "").strip() for k, v in r.items()} for r in rows]
    emails = {r.get("email", "").lower() for r in lower}
    phones = {_phone(r.get("phone", "")) for r in lower}
    found = [p for p in TRUTH if p["email"] in emails or _phone(p["phone"]) in phones]
    sols = [r for r in lower if r.get("first", "").lower() == "sol" and r.get("last", "").lower() == "rossi"]
    return {
        "rows": len(rows),
        "members_found": len(found),
        "extra_rows": len(rows) - len(found),
        "sol_rossi_rows": len(sols),                         # 2 is right; 1 means the two people were merged
        "valid": len(rows) == 48 and len(found) == 48,
    }
