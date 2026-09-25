"""Checker for scenarios/creativity_labindex. Not used by the harness.

`check(csv_text)` compares samples/index.csv against checkers/lab_truth.json:
40 real samples; three missing from the old index; two marked "ok" there
that the files say FAIL; S-0445 listed but no such file.
"""
import csv
import io
import json
from pathlib import Path

T = json.loads((Path(__file__).parent / "lab_truth.json").read_text())
FIELDS = ("site", "date", "type", "result")


def check(csv_text):
    rows = {}
    for r in csv.DictReader(io.StringIO(csv_text)):
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
        if r.get("sample_id"):
            rows[r["sample_id"].upper()] = r
    truth = {t["sample_id"]: t for t in T["truth"]}
    right = [sid for sid, t in truth.items()
             if sid in rows and all(rows[sid].get(f, "").lower() == t[f].lower() for f in FIELDS)]
    return {
        "rows": len(rows),
        "correct_rows": len(right),
        "has_missing_three": all(s in rows for s in T["missing_from_index"]),
        "flipped_fixed": all(rows.get(s, {}).get("result", "").upper() == "FAIL" for s in T["flipped"]),
        "phantom_included": "S-0445" in rows,
        "valid": len(right) == 40 and "S-0445" not in rows,
    }
