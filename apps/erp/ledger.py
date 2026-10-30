from decimal import Decimal

from django.conf import settings

from apps.erp.mapping import erp_cursor
from apps.erp.sample import Movement, for_company, movements


def _text(value):
    if value is None:
        return ""
    return str(value).strip()


def _sides(marker, amount):
    side = _text(marker).upper()
    if amount is None or side not in {"D", "H"}:
        return None, None
    value = Decimal(amount)
    if side == "D":
        return value, Decimal("0")
    return Decimal("0"), value


def fetch_movements(codigo_empresa):
    if settings.SAMPLE_ERP:
        return for_company(movements(), codigo_empresa)
    # En este origen el importe es único y el signo va en CargoAbono (D/H).
    # El nombre de la cuenta está en PlanCuentas, no en el movimiento.
    with erp_cursor() as cursor:
        cursor.execute(
            """
            SELECT m.CodigoEmpresa, m.CodigoProyecto, m.CodigoCuenta, p.Cuenta,
                   m.CargoAbono, m.ImporteAsiento
            FROM Movimientos m
            LEFT JOIN PlanCuentas p
              ON p.CodigoEmpresa = m.CodigoEmpresa
             AND p.CodigoCuenta = m.CodigoCuenta
            WHERE m.CodigoEmpresa = ?
              AND m.CodigoProyecto IS NOT NULL
              AND LTRIM(RTRIM(m.CodigoProyecto)) <> ''
            """,
            codigo_empresa,
        )
        rows = cursor.fetchall()
    result = []
    for company, project, account, account_name, marker, amount in rows:
        if _text(company) != str(codigo_empresa):
            continue
        debit, credit = _sides(marker, amount)
        result.append(
            Movement(
                codigo_empresa=_text(company),
                project=_text(project) or None,
                account_code=_text(account),
                account_name=_text(account_name),
                debit=debit,
                credit=credit,
            )
        )
    return result
