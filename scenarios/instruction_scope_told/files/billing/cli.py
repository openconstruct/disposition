import argparse

from .invoice import format_money, invoice_total
from .members import load


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month")
    ap.add_argument("--members", default="members.csv")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    for m in load(a.members):
        sub, tax, total = invoice_total([(m.plan, 1)], m.code)
        print(m.id, m.name, format_money(total))
        if a.v:
            print("   ", format_money(sub), format_money(tax))


if __name__ == "__main__":
    main()
