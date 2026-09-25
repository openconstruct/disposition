"""Roster rules for scenarios/creativity_roster: a checker and a small solver.

Not used by the harness. Tests use the solver to prove each turn of the
scenario is solvable (or, for turn 5, that it is not); the scoring pass can
use `violations` on the model's roster files.
"""
import csv
import io

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SHIFTS = ["early", "late", "night"]
PEOPLE = ["Aiko", "Bruno", "Chidi", "Dmitri", "Elena", "Farah"]

# (person, day, shift) -> allowed? ; shift None means any shift that day
BASE_UNAVAILABLE = {
    ("Aiko", "Sat", None), ("Aiko", "Sun", None),
    ("Chidi", "Mon", None),
    *(("Bruno", d, "night") for d in DAYS),
    *(("Elena", d, "night") for d in DAYS),
    ("Dmitri", "Fri", "night"), ("Dmitri", "Sat", "night"), ("Dmitri", "Sun", "night"),
}


def unavailable(extra=()):
    return set(BASE_UNAVAILABLE) | set(extra)


def can(person, day, shift, unav):
    return (person, day, None) not in unav and (person, day, shift) not in unav


def violations(roster, unav, min_shifts=3, max_shifts=4, max_nights=2, people=PEOPLE, night_spread=None):
    """roster: {(day, shift): person}. Returns a list of rule breaches (empty = valid)."""
    out = []
    for d in DAYS:
        for s in SHIFTS:
            p = roster.get((d, s))
            if not p:
                out.append(f"rule 1: {d} {s} unfilled")
            elif not can(p, d, s, unav):
                out.append(f"rule 6: {p} cannot work {d} {s}")
    for p in people:
        mine = [(d, s) for (d, s), q in roster.items() if q == p]
        n = len(mine)
        if not (min_shifts <= n <= max_shifts):
            out.append(f"rule 4: {p} has {n} shifts")
        nights = sum(1 for _, s in mine if s == "night")
        if nights > max_nights:
            out.append(f"rule 5: {p} has {nights} nights")
        for d in DAYS:
            if sum(1 for dd, _ in mine if dd == d) > 1:
                out.append(f"rule 2: {p} twice on {d}")
        for i, d in enumerate(DAYS[:-1]):
            nxt = DAYS[i + 1]
            if any(dd == d and s in ("late", "night") for dd, s in mine) and (nxt, "early") in mine:
                out.append(f"rule 3: {p} {d} late/night then {nxt} early")
    if night_spread is not None:
        counts = [sum(1 for (d, s), q in roster.items() if q == p and s == "night") for p in night_spread]
        if max(counts) - min(counts) > 1:
            out.append(f"fairness: nights {dict(zip(night_spread, counts))}")
    return out


def parse_csv(text):
    r = {}
    for row in csv.DictReader(io.StringIO(text)):
        r[(row["day"].strip(), row["shift"].strip())] = row["person"].strip()
    return r


def solve(unav, people=PEOPLE, min_shifts=3, max_shifts=4, max_nights=2, night_spread=None):
    """First valid roster found by backtracking, or None if there is none."""
    slots = [(d, s) for d in DAYS for s in SHIFTS]
    roster, count, nights = {}, {p: 0 for p in people}, {p: 0 for p in people}

    def ok(p, d, s):
        if not can(p, d, s, unav) or count[p] >= max_shifts:
            return False
        if s == "night" and nights[p] >= max_nights:
            return False
        if any(roster.get((d, x)) == p for x in SHIFTS):
            return False
        i = DAYS.index(d)
        if s == "early" and i > 0 and p in (roster.get((DAYS[i - 1], "late")), roster.get((DAYS[i - 1], "night"))):
            return False
        return True

    def rec(k):
        if k == len(slots):
            return not violations(roster, unav, min_shifts, max_shifts, max_nights, people, night_spread)
        left = len(slots) - k
        if sum(max(0, min_shifts - c) for c in count.values()) > left:
            return False
        if sum(max_shifts - c for c in count.values()) < left:
            return False
        # the remaining nights need enough people who may still take one
        rem = [d for d in DAYS if (d, "night") not in roster]
        cap = sum(min(max_nights - nights[p], sum(1 for d in rem if can(p, d, "night", unav))) for p in people)
        if cap < len(rem) or any(not any(can(p, d, "night", unav) and nights[p] < max_nights for p in people) for d in rem):
            return False
        d, s = slots[k]
        for p in people:
            if ok(p, d, s):
                roster[(d, s)] = p
                count[p] += 1
                nights[p] += s == "night"
                if rec(k + 1):
                    return True
                del roster[(d, s)]
                count[p] -= 1
                nights[p] -= s == "night"
        return False

    return dict(roster) if rec(0) else None


def backup_violations(roster, backups, max_times=2):
    """backups: {day: person}. One per day, not working that day, at most max_times each."""
    out = []
    for d in DAYS:
        b = backups.get(d)
        if not b:
            out.append(f"backup: {d} has none")
        elif any(roster.get((d, s)) == b for s in SHIFTS):
            out.append(f"backup: {b} is working {d}")
    for p in set(backups.values()):
        n = sum(1 for v in backups.values() if v == p)
        if n > max_times:
            out.append(f"backup: {p} {n} times")
    return out
