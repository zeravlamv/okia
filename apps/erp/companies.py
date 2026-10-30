from django.conf import settings

from apps.erp.mapping import erp_cursor


def company_names(codes):
    if not codes or settings.SAMPLE_ERP:
        return {}
    placeholders = ",".join("?" for _ in codes)
    try:
        with erp_cursor() as cursor:
            cursor.execute(
                f"SELECT CodigoEmpresa, Empresa FROM Empresas WHERE CodigoEmpresa IN ({placeholders})",
                list(codes),
            )
            rows = cursor.fetchall()
    except Exception:
        return {}
    return {str(row[0]).strip(): str(row[1] or "").strip() for row in rows}
