COOKIE = "okia_user"
ONE_YEAR = 60 * 60 * 24 * 365


def remembered_username(request):
    value = request.COOKIES.get(COOKIE, "")
    if not value or any(character in value for character in "\r\n;"):
        return ""
    return value


def apply_remember(response, username, remember):
    """Guarda solo el identificador. Nunca la contraseña."""

    if remember and username:
        response.set_cookie(
            COOKIE,
            username,
            max_age=ONE_YEAR,
            httponly=True,
            samesite="Lax",
        )
        return
    response.delete_cookie(COOKIE)
