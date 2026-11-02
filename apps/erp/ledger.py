from datetime import datetime
from decimal import Decimal

from django.conf import settings

from apps.erp.mapping import erp_cursor, month_window
from apps.erp.sample import AnalyticSlice, Movement, for_company, movements


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


def _date(value):
    if isinstance(value, datetime):
        return value.date()
    return value


def _position(value):
    return _text(value).strip("{}").casefold()


def _year(value):
    text = _text(value)
    if not text:
        return None
    return int(text)


def _movement(
    company,
    project,
    account,
    account_name,
    marker,
    amount,
    ejercicio,
    moment,
    position,
    comment,
    channel="",
    delegation="",
    department="",
    section="",
    asiento="",
):
    debit, credit = _sides(marker, amount)
    return Movement(
        codigo_empresa=_text(company),
        project=_text(project) or None,
        account_code=_text(account),
        account_name=_text(account_name),
        debit=debit,
        credit=credit,
        ejercicio=_year(ejercicio),
        movement_date=_date(moment),
        position=_position(position),
        comment=_text(comment),
        channel=_text(channel),
        delegation=_text(delegation),
        department=_text(department),
        section=_text(section),
        asiento=_text(asiento),
    )


def _attach_slices(codigo_empresa, rows, year=None, month=None):
    """CabPosicion es el MovPosicion del movimiento. Una fila borrada no entra.

    El importe y los niveles son los de AnaMovimientos. No se vuelven a repartir.
    """

    indexed = {row.position: row for row in rows if row.position}
    if not indexed:
        return rows
    period = ""
    parameters = [codigo_empresa]
    if year is not None and month is not None:
        start, end = month_window(year, month)
        period = "AND m.FechaAsiento >= ? AND m.FechaAsiento < ?"
        parameters.extend([start, end])
    elif year is not None:
        period = """
              AND (
                (m.FechaAsiento IS NOT NULL AND YEAR(m.FechaAsiento) = ?)
                OR (m.FechaAsiento IS NULL AND m.Ejercicio = ?)
              )
        """
        parameters.extend([year, year])
    with erp_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT a.CabPosicion, a.CodigoCanal, a.IdDelegacion, a.CodigoDepartamento,
                   a.CodigoProyecto, a.CodigoSeccion, a.ImporteAsiento
            FROM AnaMovimientos a
            INNER JOIN Movimientos m ON m.MovPosicion = a.CabPosicion
            WHERE a.CodigoEmpresa = ?
              AND a.StatusBorrado = 0
              {period}
            """,
            parameters,
        )
        slices = cursor.fetchall()
    for position, channel, delegation, department, project, section, amount in slices:
        movement = indexed.get(_position(position))
        if movement is None:
            continue
        movement.slices.append(
            AnalyticSlice(
                channel=_text(channel),
                delegation=_text(delegation),
                department=_text(department),
                project=_text(project),
                section=_text(section),
                amount=None if amount is None else Decimal(amount),
            )
        )
    return rows


def fetch_movements(codigo_empresa):
    if settings.SAMPLE_ERP:
        return for_company(movements(), codigo_empresa)
    # En este origen el importe es único y el signo va en CargoAbono (D/H).
    # El nombre de la cuenta está en PlanCuentas, no en el movimiento.
    with erp_cursor() as cursor:
        cursor.execute(
            """
            SELECT m.CodigoEmpresa, m.CodigoProyecto, m.CodigoCuenta, p.Cuenta,
                   m.CargoAbono, m.ImporteAsiento, m.Ejercicio, m.FechaAsiento,
                   m.MovPosicion, m.Comentario, m.CodigoCanal, m.IdDelegacion,
                   m.CodigoDepartamento, m.CodigoSeccion
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
    for (
        company,
        project,
        account,
        account_name,
        marker,
        amount,
        ejercicio,
        moment,
        position,
        comment,
        channel,
        delegation,
        department,
        section,
    ) in rows:
        if _text(company) != str(codigo_empresa):
            continue
        result.append(
            _movement(
                company,
                project,
                account,
                account_name,
                marker,
                amount,
                ejercicio,
                moment,
                position,
                comment,
                channel,
                delegation,
                department,
                section,
            )
        )
    return _attach_slices(codigo_empresa, result)


def fetch_period_movements(codigo_empresa, year, month=None):
    """Movimientos del ejercicio, con proyecto o sin él. Cada fila es un apunte."""

    if settings.SAMPLE_ERP:
        rows = [
            row
            for row in for_company(movements(), codigo_empresa)
            if (row.movement_date.year if row.movement_date is not None else row.ejercicio) == year
        ]
        if month is None:
            return rows
        return [
            row
            for row in rows
            if row.movement_date is not None and row.movement_date.month == int(month)
        ]
    if month is None:
        period_sql = """
              AND (
                (m.FechaAsiento IS NOT NULL AND YEAR(m.FechaAsiento) = ?)
                OR (m.FechaAsiento IS NULL AND m.Ejercicio = ?)
              )
        """
        period_params = (year, year)
    else:
        start, end = month_window(year, month)
        period_sql = "AND m.FechaAsiento >= ? AND m.FechaAsiento < ?"
        period_params = (start, end)
    with erp_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT m.CodigoEmpresa, m.CodigoProyecto, m.CodigoCuenta, p.Cuenta,
                   m.CargoAbono, m.ImporteAsiento, m.Ejercicio, m.FechaAsiento,
                   m.MovPosicion, m.Comentario, m.CodigoCanal, m.IdDelegacion,
                   m.CodigoDepartamento, m.CodigoSeccion, m.Asiento
            FROM Movimientos m
            LEFT JOIN PlanCuentas p
              ON p.CodigoEmpresa = m.CodigoEmpresa
             AND p.CodigoCuenta = m.CodigoCuenta
            WHERE m.CodigoEmpresa = ?
              {period_sql}
            """,
            codigo_empresa,
            *period_params,
        )
        rows = cursor.fetchall()
    result = []
    for (
        company,
        project,
        account,
        account_name,
        marker,
        amount,
        ejercicio,
        moment,
        position,
        comment,
        channel,
        delegation,
        department,
        section,
        asiento,
    ) in rows:
        if _text(company) != str(codigo_empresa):
            continue
        result.append(
            _movement(
                company,
                project,
                account,
                account_name,
                marker,
                amount,
                ejercicio,
                moment,
                position,
                comment,
                channel,
                delegation,
                department,
                section,
                asiento,
            )
        )
    return _attach_slices(codigo_empresa, result, year, month)


def fetch_account_groups(codigo_empresa):
    """Descripción de los grupos de 1 a 4 dígitos de la empresa.

    Si un código está en más de un plan, manda el plan 2008.
    """

    if settings.SAMPLE_ERP:
        return []
    with erp_cursor() as cursor:
        cursor.execute(
            """
            SELECT CodigoGrupo, DescripcionGrupo, TipoPlanCuenta
            FROM Grupos
            WHERE CodigoEmpresa = ?
              AND LEN(LTRIM(RTRIM(CodigoGrupo))) BETWEEN 1 AND 4
            """,
            codigo_empresa,
        )
        rows = cursor.fetchall()
    chosen = {}
    for code, description, plan in rows:
        normalized = _text(code)
        if not normalized or len(normalized) > 4:
            continue
        plan_name = _text(plan)
        current = chosen.get(normalized)
        if current is None or (plan_name == "2008" and current[1] != "2008"):
            chosen[normalized] = (_text(description), plan_name)
    return [(code, name) for code, (name, _plan) in chosen.items()]
