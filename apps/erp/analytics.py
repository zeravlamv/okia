from django.conf import settings

from apps.erp.mapping import erp_cursor

_QUERIES = (
    ("channel", "SELECT CodigoCanal, Canal FROM CanalesEmpresa WHERE CodigoEmpresa = ?"),
    ("delegation", "SELECT IdDelegacion, Delegacion FROM Delegaciones WHERE CodigoEmpresa = ?"),
    ("department", "SELECT CodigoDepartamento, Departamento FROM Departamentos WHERE CodigoEmpresa = ?"),
    ("project", "SELECT CodigoProyecto, Proyecto FROM Proyectos WHERE CodigoEmpresa = ?"),
    ("section", "SELECT CodigoSeccion, Seccion FROM Secciones WHERE CodigoEmpresa = ?"),
)


def _text(value):
    if value is None:
        return ""
    return str(value).strip()


def fetch_dimension_labels(codigo_empresa):
    """Descripción de cada código analítico, limitada a la empresa elegida."""

    labels = {key: {} for key, _sql in _QUERIES}
    if settings.SAMPLE_ERP:
        return labels
    try:
        with erp_cursor() as cursor:
            for key, sql in _QUERIES:
                cursor.execute(sql, codigo_empresa)
                for code, description in cursor.fetchall():
                    normalized = _text(code)
                    if normalized:
                        labels[key][normalized] = _text(description)
    except Exception:
        return labels
    return labels
