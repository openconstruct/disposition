from billing.invoice import format_money, invoice_total


def test_total_no_discount():
    sub, tax, total = invoice_total([("hotdesk", 1)])
    assert round(sub, 2) == 180.0
    assert round(tax, 2) == 37.8
    assert round(total, 2) == 217.8


def test_format_money():
    assert format_money(217.8) == "€217.80"
