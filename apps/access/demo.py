from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from apps.access.models import (
    AnalyticalLevel,
    CompanyAccess,
    ErpConnection,
    InformationGroup,
    Profile,
    ProfilePermission,
)

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo"


def ensure_demo():
    """Cuenta local para ver el margen con datos de ejemplo."""

    user_model = get_user_model()
    user, created = user_model.objects.get_or_create(
        username=DEMO_USERNAME,
        defaults={"email": "demo@example.com", "is_active": True},
    )
    if created or not user.check_password(DEMO_PASSWORD):
        user.email = "demo@example.com"
        user.is_active = True
        user.set_password(DEMO_PASSWORD)
        user.save()
    profile, _ = Profile.objects.get_or_create(user=user)
    for group in InformationGroup.values:
        ProfilePermission.objects.get_or_create(profile=profile, group=group)
    CompanyAccess.objects.get_or_create(user=user, codigo_empresa="1")
    user.is_staff = True
    user.save()
    for model in (
        user.__class__,
        Profile,
        ProfilePermission,
        CompanyAccess,
        ErpConnection,
        AnalyticalLevel,
    ):
        content_type = ContentType.objects.get_for_model(model)
        user.user_permissions.add(*Permission.objects.filter(content_type=content_type))
    return user
