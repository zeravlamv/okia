from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass
class SaleLine:
    base: Decimal | None
    article: str


@dataclass
class SaleOrder:
    codigo_empresa: str
    ejercicio: int
    serie: str
    numero: str
    codigo_cliente: str
    project: str | None
    header_base: Decimal | None
    tax_included: Decimal | None
    order_date: date | None
    status: str
    lines: list[SaleLine] = field(default_factory=list)
    channel: str = ""
    delegation: str = ""
    department: str = ""
    section: str = ""


@dataclass
class PurchaseLine:
    codigo_empresa: str
    project: str | None
    amount: Decimal | None
    article_name: str
    line_date: date | None
    ejercicio: str = ""
    serie: str = ""
    numero: str = ""


@dataclass
class Movement:
    codigo_empresa: str
    project: str | None
    account_code: str
    account_name: str
    debit: Decimal | None
    credit: Decimal | None


def orders():
    return [
        SaleOrder(
            codigo_empresa="1",
            ejercicio=2026,
            serie="A",
            numero="1001",
            codigo_cliente="C1",
            project="1001",
            header_base=Decimal("1000"),
            tax_included=Decimal("1210"),
            order_date=date(2026, 3, 1),
            status="Pendiente",
            channel="Tienda",
            lines=[
                SaleLine(Decimal("400"), "Servicio"),
                SaleLine(Decimal("400"), "Material"),
            ],
        ),
        SaleOrder(
            codigo_empresa="1",
            ejercicio=2026,
            serie="A",
            numero="1002",
            codigo_cliente="C1",
            project="1002",
            header_base=Decimal("500"),
            tax_included=Decimal("605"),
            order_date=date(2026, 4, 1),
            status="Anulado",
            lines=[],
        ),
        SaleOrder(
            codigo_empresa="1",
            ejercicio=2026,
            serie="A",
            numero="1003",
            codigo_cliente="C2",
            project="1003",
            header_base=Decimal("0"),
            tax_included=Decimal("0"),
            order_date=date(2026, 5, 1),
            status="Servido",
            lines=[],
        ),
        SaleOrder(
            codigo_empresa="1",
            ejercicio=2026,
            serie="A",
            numero="1004",
            codigo_cliente="C3",
            project="1004",
            header_base=None,
            tax_included=None,
            order_date=date(2026, 6, 1),
            status="Facturado",
            lines=[SaleLine(Decimal("10"), "Pieza"), SaleLine(None, "Sin importe")],
        ),
        SaleOrder(
            codigo_empresa="1",
            ejercicio=2026,
            serie="B",
            numero="2001",
            codigo_cliente="C4",
            project="2000",
            header_base=Decimal("100"),
            tax_included=Decimal("121"),
            order_date=date(2026, 2, 1),
            status="Pendiente",
            lines=[],
        ),
        SaleOrder(
            codigo_empresa="1",
            ejercicio=2026,
            serie="B",
            numero="2002",
            codigo_cliente="C4",
            project="2000",
            header_base=Decimal("80"),
            tax_included=Decimal("96.80"),
            order_date=date(2026, 2, 2),
            status="Pendiente",
            lines=[],
        ),
        SaleOrder(
            codigo_empresa="1",
            ejercicio=2026,
            serie="A",
            numero="1005",
            codigo_cliente="C5",
            project="1005",
            header_base=Decimal("300"),
            tax_included=Decimal("363"),
            order_date=date(2025, 12, 1),
            status="Pendiente",
            lines=[],
        ),
        SaleOrder(
            codigo_empresa="2",
            ejercicio=2026,
            serie="A",
            numero="1001",
            codigo_cliente="C9",
            project="1001",
            header_base=Decimal("9999"),
            tax_included=Decimal("12098.79"),
            order_date=date(2026, 3, 1),
            status="Pendiente",
            lines=[],
        ),
    ]


def purchases():
    return [
        PurchaseLine("1", "1001", Decimal("200"), "Tornillo", date(2025, 11, 1)),
        PurchaseLine("1", "1001", Decimal("100"), "Horas montaje", date(2026, 3, 2)),
        PurchaseLine("1", "1002", Decimal("10"), "Tornillo", date(2026, 4, 2)),
        PurchaseLine("1", "1003", Decimal("40"), "Material suelto", date(2026, 5, 2)),
        PurchaseLine("1", "2000", Decimal("999"), "Acero", date(2026, 2, 3)),
        PurchaseLine("1", None, Decimal("15"), "Gasto general", date(2026, 1, 1)),
        PurchaseLine("2", "1001", Decimal("50"), "Tornillo", date(2026, 3, 2)),
    ]


def movements():
    return [
        Movement("1", "1001", "640", "Sueldos y salarios personal", Decimal("50"), Decimal("0")),
        Movement("1", "1001", "700", "Ventas", Decimal("0"), Decimal("800")),
        Movement("1", "1001", "472", "IVA soportado", Decimal("21"), Decimal("0")),
        Movement("2", "1001", "700", "Ventas", Decimal("0"), Decimal("9999")),
    ]


def master_counts():
    return {
        "1": {"clientes": 2, "proveedores": 1, "articulos": 3},
        "2": {"clientes": 1, "proveedores": 1, "articulos": 1},
    }


def for_company(rows, codigo_empresa):
    return [row for row in rows if row.codigo_empresa == codigo_empresa]
