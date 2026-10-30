from decimal import Decimal


def format_money(value):
    if value is None:
        return "—"
    quantized = Decimal(value).quantize(Decimal("0.01"))
    return f"{quantized:.2f}".replace(".", ",") + " EUR"


def format_percent(value):
    if value is None:
        return "No aplicable"
    return f"{Decimal(value).quantize(Decimal('0.01')):.2f}".replace(".", ",") + " %"
