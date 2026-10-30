from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.accounts.views import (
    RecoverComplete,
    RecoverConfirm,
    login_view,
    recover_done,
    recover_request,
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("recuperar/", recover_request, name="password-recover"),
    path("recuperar/enviado/", recover_done, name="password-recover-done"),
    path("recuperar/hecho/", RecoverComplete.as_view(), name="password-recover-complete"),
    path(
        "recuperar/<uidb64>/<token>/",
        RecoverConfirm.as_view(),
        name="password-recover-confirm",
    ),
]
