from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.access.services import allowed_companies, set_company
from apps.erp.companies import company_names


def _labels(codes):
    names = company_names(codes)
    return [(code, names.get(code) or code) for code in codes]


@login_required
def choose_company(request):
    """Con varias, no hay cifras hasta elegir. Con una, queda seleccionada.

    Sin empresas, no hay cifras económicas.
    """

    companies = allowed_companies(request.user)
    if not companies:
        return render(request, "access/company.html", {"companies": [], "empty": True})
    if request.method == "POST":
        code = request.POST.get("codigo_empresa", "").strip()
        try:
            set_company(request, code)
        except PermissionError:
            return render(
                request,
                "access/company.html",
                {
                    "companies": _labels(companies),
                    "empty": False,
                    "error": "La empresa no está asignada a esta persona.",
                },
            )
        return redirect("dashboard")
    if len(companies) == 1:
        set_company(request, companies[0])
        return redirect("dashboard")
    return render(
        request,
        "access/company.html",
        {
            "companies": _labels(companies),
            "empty": False,
            "current": request.session.get("okia_company"),
        },
    )
