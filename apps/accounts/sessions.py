THIRTY_DAYS = 60 * 60 * 24 * 30


def apply_session(request, keep):
    """Mantener la sesión, si la persona lo pide, dura 30 días.

    Si no lo pide, la sesión termina al cerrar el navegador.
    """

    if keep:
        request.session.set_expiry(THIRTY_DAYS)
        return
    request.session.set_expiry(0)
