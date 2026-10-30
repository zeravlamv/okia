from apps.access.models import CompanyAccess


def allowed_companies(user):
    return list(
        CompanyAccess.objects.filter(user=user)
        .order_by("codigo_empresa")
        .values_list("codigo_empresa", flat=True)
    )


def selected_company(request):
    """Con una sola empresa, queda seleccionada al entrar.

    Sin empresas, no hay cifras económicas.
    """

    companies = allowed_companies(request.user)
    if not companies:
        return None
    current = request.session.get("okia_company")
    if current in companies:
        return current
    if len(companies) == 1:
        request.session["okia_company"] = companies[0]
        return companies[0]
    return None


def set_company(request, codigo_empresa):
    if codigo_empresa not in allowed_companies(request.user):
        raise PermissionError("La empresa no está asignada a esta persona.")
    request.session["okia_company"] = codigo_empresa
    return codigo_empresa


def has_groups(user, required):
    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, "profile", None)
    if profile is None:
        return False
    owned = set(profile.permissions.values_list("group", flat=True))
    return set(required).issubset(owned)


