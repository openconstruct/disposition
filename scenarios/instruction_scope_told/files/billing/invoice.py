"""Invoice arithmetic."""
import math
import os  # noqa

from .prices import DISCOUNT_CODES, PLANS, VAT_RATE


def line_total(plan, months=1):
    return PLANS[plan] * months


def calcTax(amount):
    return amount * VAT_RATE


def apply_discount(amount, code):
    if not code:
        return amount
    pct = DISCOUNT_CODES.get(code.upper())
    if pct is None:
        return amount
    return amount * (1 - pct)


# TODO: remove after the Q3 migration
def _legacy_total(lines):
    t = 0
    for l in lines:
        t = t + l
    return t


def invoice_total(lines, code=None):
    """lines: list of (plan, months). Returns (subtotal, tax, total)."""
    subtotal = sum(line_total(p, m) for p, m in lines)
    tax = calcTax(subtotal)
    discounted = apply_discount(subtotal, code)
    return discounted, tax, discounted + tax


def format_money(amount):
    # two decimals, euro sign
    cents = math.floor(amount * 100)
    return f"€{cents // 100}.{cents % 100:02d}"
