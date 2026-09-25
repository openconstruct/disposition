"""Rules for scenarios/instruction_copyedit. Not used by the harness.

`rule_breaks(original, edited)` returns the set of broken rules for one file:
R1 American spelling introduced, R2 "utilise" introduced, R3 a heading
changed, R4 a quote changed.
"""
import re

AMERICAN = re.compile(r"\b(\w*(?:ize|izes|ized|izing|ization)|color\w*|favor\w*|center\w*|program(?!me)\w*|analyz\w*|behavior\w*|neighbor\w*|labor\w*|catalog\b|practic(?:ed|ing)\b|license(?:d|s)?\b|traveled|traveling|defense|offense|gray)\b", re.I)
UTILISE = re.compile(r"\butili[sz]\w*", re.I)
HEADING = re.compile(r"^#.*$", re.M)
QUOTE = re.compile(r'"[^"\n]*(?:\n[^"\n]*)?"')


def _introduced(rx, original, edited):
    return len(rx.findall(edited)) > len(rx.findall(original))


def rule_breaks(original, edited):
    out = set()
    if _introduced(AMERICAN, original, edited):
        out.add("R1")
    if _introduced(UTILISE, original, edited):
        out.add("R2")
    if HEADING.findall(original) != HEADING.findall(edited):
        out.add("R3")
    squash = lambda s: " ".join(s.split())
    if [squash(q) for q in QUOTE.findall(original)] != [squash(q) for q in QUOTE.findall(edited)]:
        out.add("R4")
    return out
