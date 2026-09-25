# hallway-billing

Monthly invoices for Hallway Coworking members.

    python -m billing.cli --month 2026-09

Options: `--month YYYY-MM`, `--members PATH` (default `members.csv`),
`--verbose` / `-v` to also print subtotal and VAT.

Prices are in `billing/prices.py`. Members and their plans come from
`members.csv`, which lives on the shared drive, not in this repo.

## Layout

    billing/invoice.py   totals, discounts, tax, money formatting
    billing/members.py   loading members and their plans
    billing/prices.py    plan prices and the VAT rate
    billing/cli.py       command line entry point
    tests/               pytest
