from decimal import Decimal

from apps.margins.format import format_money


def test_money_uses_a_dot_for_thousands_and_a_comma_for_decimals():
    assert format_money(Decimal("2447563.88")) == "2.447.563,88 EUR"
    assert format_money(Decimal("1190")) == "1.190,00 EUR"
    assert format_money(Decimal("-40.5")) == "-40,50 EUR"
    assert format_money(None) == "—"
