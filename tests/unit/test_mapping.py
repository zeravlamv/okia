import pytest

from apps.erp.mapping import MissingColumn, indicates_hours, is_cancelled, is_income_account, resolve


def test_resolve_prefers_the_tax_base():
    assert resolve(["ImporteLiquido", "BaseImponible"], "base") == "BaseImponible"


def test_resolve_accepts_the_documented_typo_for_exercise():
    assert resolve(["Ejericicio"], "exercise") == "Ejericicio"


def test_missing_column_is_explicit():
    with pytest.raises(MissingColumn):
        resolve(["ImporteLiquido"], "base")


def test_hour_and_income_markers():
    assert indicates_hours("Sueldos y salarios personal")
    assert indicates_hours("Horas montaje")
    assert not indicates_hours("Tornillo")
    assert is_income_account("700", "Ventas")
    assert not is_income_account("640", "Sueldos y salarios personal")
    assert is_cancelled("Anulado")
    assert not is_cancelled("Pendiente")
