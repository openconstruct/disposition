import argparse

from .invoice import format_money, invoice_total
from .members import load


def main():
    parser = argparse.ArgumentParser(description="Print this month's invoices.")
    parser.add_argument("--month", help="billing month, YYYY-MM")
    parser.add_argument("--members", default="members.csv", help="path to members.csv")
    parser.add_argument("--verbose", "-v", action="store_true", help="also print subtotal and VAT")
    args = parser.parse_args()
    for member in load(args.members):
        subtotal, tax, total = invoice_total([(member.plan, 1)], member.code)
        print(member.member_id, member.name, format_money(total))
        if args.verbose:
            print("   ", format_money(subtotal), format_money(tax))


if __name__ == "__main__":
    main()
