from decimal import Decimal


def format_money(value):
    """Punto de miles, coma decimal y dos decimales: 2.447.563,88 EUR."""

    if value is None:
        return "—"
    quantized = Decimal(value).quantize(Decimal("0.01"))
    sign = "-" if quantized < 0 else ""
    whole, cents = f"{abs(quantized):.2f}".split(".")
    groups = []
    while whole:
        groups.append(whole[-3:])
        whole = whole[:-3]
    return sign + ".".join(reversed(groups)) + "," + cents + " EUR"


def format_percent(value):
    if value is None:
        return "No aplicable"
    return f"{Decimal(value).quantize(Decimal('0.01')):.2f}".replace(".", ",") + " %"
