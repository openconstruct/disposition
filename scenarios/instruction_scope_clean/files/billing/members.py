import csv
from dataclasses import dataclass


@dataclass
class Member:
    member_id: str
    name: str
    plan: str
    code: str = ""
    year: int = 0


def load(path):
    members = []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            members.append(
                Member(row["id"], row["name"], row["plan"], row.get("code", ""), int(row.get("year") or 0))
            )
    return members


def get_mem(members, member_id):
    for member in members:
        if member.member_id == member_id:
            return member
    return None


def plans_in_use(members):
    return sorted({member.plan for member in members})
