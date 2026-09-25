import csv
import json  # noqa
from dataclasses import dataclass


@dataclass
class Member:
    id: str
    name: str
    plan: str
    code: str = ""
    year: int = 0


def load(path):
    out = []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            out.append(Member(row["id"], row["name"], row["plan"], row.get("code", ""), int(row.get("year") or 0)))
    return out


def get_mem(members, id):
    for m in members:
        if m.id == id:
            return m
    return None


def plans_in_use(ms):
    s = set()
    for x in ms:
        s.add(x.plan)
    return sorted(s)
