from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q

from apps.access.models import (
    AnalyticalLevel,
    CompanyAccess,
    ErpConnection,
    Profile,
    ProfilePermission,
)
from apps.access.services import allowed_companies

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


def _visible_users(request):
    companies = allowed_companies(request.user)
    return User.objects.filter(
        Q(companies__codigo_empresa__in=companies) | Q(companies__isnull=True)
    ).distinct()


class LimitedUserAdmin(UserAdmin):
    def get_queryset(self, request):
        return _visible_users(request)


class ProfilePermissionInline(admin.TabularInline):
    model = ProfilePermission
    extra = 0


class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProfilePermissionInline]

    def get_queryset(self, request):
        companies = allowed_companies(request.user)
        return (
            super()
            .get_queryset(request)
            .filter(user__companies__codigo_empresa__in=companies)
            .distinct()
        )


class CompanyAccessForm(forms.ModelForm):
    class Meta:
        model = CompanyAccess
        fields = ("user", "codigo_empresa")

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        if request is not None:
            self.fields["user"].queryset = _visible_users(request)

    def clean_codigo_empresa(self):
        code = (self.cleaned_data.get("codigo_empresa") or "").strip()
        if self.request is not None and code not in allowed_companies(self.request.user):
            raise forms.ValidationError("La empresa no está asignada a esta persona.")
        return code


class CompanyAccessAdmin(admin.ModelAdmin):
    form = CompanyAccessForm
    list_display = ("user", "codigo_empresa")

    def get_queryset(self, request):
        companies = allowed_companies(request.user)
        return super().get_queryset(request).filter(codigo_empresa__in=companies)

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)

        class RequestForm(form_class):
            def __init__(self, *args, **form_kwargs):
                form_kwargs["request"] = request
                super().__init__(*args, **form_kwargs)

        return RequestForm


class ErpConnectionForm(forms.ModelForm):
    """El secreto no se muestra de nuevo en claro."""

    password = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(render_value=False),
    )

    class Meta:
        model = ErpConnection
        fields = ("name", "host", "database", "username", "password")

    def save(self, commit=True):
        instance = super().save(commit=False)
        typed = (self.cleaned_data.get("password") or "").strip()
        if instance.pk and not typed:
            instance.password = ErpConnection.objects.get(pk=instance.pk).password
        elif typed:
            instance.password = typed
        if commit:
            instance.save()
        return instance


class ErpConnectionAdmin(admin.ModelAdmin):
    form = ErpConnectionForm
    list_display = ("name", "host", "database", "username")


class AnalyticalLevelForm(forms.ModelForm):
    class Meta:
        model = AnalyticalLevel
        fields = ("code", "position")

    def clean_position(self):
        position = self.cleaned_data["position"]
        clash = AnalyticalLevel.objects.filter(position=position)
        if self.instance.pk:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise forms.ValidationError("Cada nivel ha de tener una posición distinta.")
        return position


class AnalyticalLevelAdmin(admin.ModelAdmin):
    form = AnalyticalLevelForm
    list_display = ("position", "code")
    list_display_links = ("code",)
    list_editable = ("position",)
    ordering = ("position", "code")
    readonly_fields = ("code",)
    fields = ("code", "position")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_changelist_formset(self, request, **kwargs):
        formset = super().get_changelist_formset(request, **kwargs)

        class UniquePositionFormSet(formset):
            def clean(self):
                super().clean()
                if any(form.errors for form in self.forms):
                    return
                positions = [
                    form.cleaned_data.get("position")
                    for form in self.forms
                    if form.cleaned_data and not form.cleaned_data.get("DELETE")
                ]
                if len(positions) != len(set(positions)):
                    raise ValidationError("Cada nivel ha de tener una posición distinta.")

        return UniquePositionFormSet


admin.site.site_header = "OKIA"
admin.site.site_title = "OKIA"
admin.site.index_title = "Administración"
admin.site.register(User, LimitedUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(CompanyAccess, CompanyAccessAdmin)
admin.site.register(ErpConnection, ErpConnectionAdmin)
admin.site.register(AnalyticalLevel, AnalyticalLevelAdmin)
