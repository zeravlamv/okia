from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from apps.access.services import selected_company
from apps.accounts.recovery import GENERIC, send_recovery
from apps.accounts.remember import apply_remember, remembered_username
from apps.accounts.sessions import apply_session

LOGIN_ERROR = "No se ha podido entrar."


def login_view(request):
    """Una cuenta inactiva no entra.

    Un acceso incorrecto no revela si el identificador existe.
    """

    if request.user.is_authenticated:
        return redirect("company-select")
    username = remembered_username(request)
    remembered = bool(username)
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember = request.POST.get("remember") == "on"
        remembered = remember
        keep = request.POST.get("keep") == "on"
        user = authenticate(request, username=username, password=password)
        if user is None or not user.is_active:
            error = LOGIN_ERROR
        else:
            login(request, user)
            apply_session(request, keep)
            selected_company(request)
            response = redirect("company-select")
            apply_remember(response, username, remember)
            return response
    return render(
        request,
        "accounts/login.html",
        {
            "username": username,
            "error": error,
            "remembered": remembered,
        },
    )


def recover_request(request):
    if request.method == "POST":
        send_recovery(request, request.POST.get("username", "").strip())
        return redirect("password-recover-done")
    return render(request, "accounts/recovery.html")


def recover_done(request):
    return render(request, "accounts/recovery_done.html", {"message": GENERIC})


class SpanishSetPassword(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Contraseña nueva"
        self.fields["new_password2"].label = "Repita la contraseña"


class RecoverConfirm(PasswordResetConfirmView):
    template_name = "accounts/recovery_confirm.html"
    form_class = SpanishSetPassword
    success_url = reverse_lazy("password-recover-complete")


class RecoverComplete(TemplateView):
    template_name = "accounts/recovery_complete.html"
