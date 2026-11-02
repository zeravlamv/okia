from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from apps.access.models import CompanyAccess
from apps.margins.filters import year_options
from apps.margins.models import FinancialReport, FinancialReportLine, PeriodClosure, renumber_report_lines
from apps.margins.project_life import set_exercise_closure


class StaffOnly:
    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


class FinancialReportLineInline(StaffOnly, admin.TabularInline):
    model = FinancialReportLine
    extra = 1
    fields = ("position", "text", "accounts", "is_total")
    ordering = ("position", "id")


@admin.register(FinancialReport)
class FinancialReportAdmin(StaffOnly, admin.ModelAdmin):
    list_display = ("code", "description", "line_count")
    search_fields = ("code", "description")
    inlines = [FinancialReportLineInline]
    change_form_template = "admin/margins/financialreport/change_form.html"

    @admin.display(description="Líneas")
    def line_count(self, obj):
        return obj.lines.count()

    def response_change(self, request, obj):
        if "_renumber" in request.POST:
            renumber_report_lines(obj)
            messages.success(request, "Las líneas quedan numeradas de 10 en 10.")
            return HttpResponseRedirect(request.path)
        return super().response_change(request, obj)


@admin.register(PeriodClosure)
class PeriodClosureAdmin(admin.ModelAdmin):
    list_display = ("codigo_empresa", "ejercicio", "month_name", "cerrado", "changed_by", "changed_at")
    list_filter = ("codigo_empresa", "ejercicio", "cerrado")
    exclude = ("changed_by",)
    readonly_fields = ("changed_at",)
    change_list_template = "admin/margins/periodclosure/change_list.html"

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff

    @admin.display(description="Mes")
    def month_name(self, obj):
        return obj.get_mes_display()

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST" and request.POST.get("exercise_action") in {"close", "open"}:
            return self._apply_exercise(request)
        context = extra_context or {}
        context["exercise_companies"] = _exercise_companies()
        context["exercise_years"] = year_options()
        return super().changelist_view(request, extra_context=context)

    def _apply_exercise(self, request):
        if not self.has_change_permission(request):
            messages.error(request, "No puedes cerrar ni abrir un ejercicio.")
            return HttpResponseRedirect(reverse("admin:margins_periodclosure_changelist"))
        company = request.POST.get("codigo_empresa", "").strip()
        year_text = request.POST.get("ejercicio", "").strip()
        years = set(year_options())
        try:
            year = int(year_text)
        except (TypeError, ValueError):
            year = None
        if company not in _exercise_companies() or year not in years:
            messages.error(request, "Elige una empresa y un ejercicio de la lista.")
            return HttpResponseRedirect(reverse("admin:margins_periodclosure_changelist"))
        closed = request.POST.get("exercise_action") == "close"
        set_exercise_closure(company, year, closed, request.user)
        if closed:
            messages.success(request, f"Se ha cerrado el ejercicio {year} de la empresa {company}. Los doce meses quedan cerrados.")
        else:
            messages.success(request, f"Se ha abierto el ejercicio {year} de la empresa {company}. Los doce meses quedan abiertos.")
        return HttpResponseRedirect(reverse("admin:margins_periodclosure_changelist"))


def _exercise_companies():
    codes = set(CompanyAccess.objects.values_list("codigo_empresa", flat=True))
    codes.update(PeriodClosure.objects.values_list("codigo_empresa", flat=True))
    return sorted(code for code in codes if code)
