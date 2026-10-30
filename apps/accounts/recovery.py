from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm

GENERIC = (
    "Si la cuenta puede recuperar la contraseña, recibirá un enlace de un solo uso "
    "durante 60 minutos."
)


class RecoveryForm(PasswordResetForm):
    def __init__(self, *args, only_user=None, **kwargs):
        self.only_user = only_user
        super().__init__(*args, **kwargs)

    def get_users(self, email):
        """Sin correo no puede recuperar la contraseña por sí mismo."""

        if self.only_user is None or not (self.only_user.email or "").strip():
            return []
        return [
            user
            for user in super().get_users(email)
            if user.pk == self.only_user.pk
        ]


def send_recovery(request, username):
    """La respuesta no revela si la cuenta existe."""

    user_model = get_user_model()
    user = user_model.objects.filter(username=username, is_active=True).first()
    if user is None or not (user.email or "").strip():
        return
    form = RecoveryForm({"email": user.email}, only_user=user)
    if not form.is_valid():
        return
    form.save(
        request=request,
        use_https=request.is_secure(),
        email_template_name="accounts/recovery_email.txt",
        subject_template_name="accounts/recovery_subject.txt",
    )
