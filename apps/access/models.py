from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class InformationGroup(models.TextChoices):
    EMPRESAS = "empresas", "Empresas"
    CLIENTES = "clientes", "Clientes"
    PROVEEDORES = "proveedores", "Proveedores"
    ARTICULOS = "articulos", "Artículos"
    PROYECTOS = "proyectos", "Proyectos"
    CANALES = "canales", "Canales"
    DELEGACIONES = "delegaciones", "Delegaciones"
    DEPARTAMENTOS = "departamentos", "Departamentos"
    SECCIONES = "secciones", "Secciones"
    PEDIDOS_VENTA = "pedidos_venta", "Pedidos de venta"
    PEDIDOS_COMPRA = "pedidos_compra", "Pedidos de compra"
    ALBARANES_VENTA = "albaranes_venta", "Albaranes de venta"
    ALBARANES_COMPRA = "albaranes_compra", "Albaranes de compra"
    MOVIMIENTOS = "movimientos", "Movimientos contables"
    PLAN_CUENTAS = "plan_cuentas", "Plan de cuentas"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfiles"

    def __str__(self):
        return self.user.get_username()


class ProfilePermission(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="permissions",
    )
    group = models.CharField(max_length=32, choices=InformationGroup.choices)

    class Meta:
        verbose_name = "permiso del perfil"
        verbose_name_plural = "permisos del perfil"
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "group"],
                name="unique_profile_group",
            )
        ]


class CompanyAccess(models.Model):
    """Una persona solo elige y consulta empresas de esta lista.

    Quien administra también queda limitado a sus empresas.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies",
    )
    codigo_empresa = models.CharField(max_length=15)

    class Meta:
        verbose_name = "empresa autorizada"
        verbose_name_plural = "empresas autorizadas"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "codigo_empresa"],
                name="unique_user_company",
            )
        ]

    def __str__(self):
        return f"{self.user.get_username()} → {self.codigo_empresa}"


class AnalyticalLevel(models.Model):
    """Orden de los niveles que usan las consultas y los informes.

    Los cinco niveles son fijos. Solo cambia la posición.
    """

    class Level(models.TextChoices):
        CANAL = "channel", "Canal"
        DELEGACION = "delegation", "Delegación"
        DEPARTAMENTO = "department", "Departamento"
        PROYECTO = "project", "Proyecto"
        SECCION = "section", "Sección"

    code = models.CharField("Nivel", max_length=32, choices=Level.choices, unique=True)
    position = models.PositiveSmallIntegerField("Posición", validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "nivel del árbol analítico"
        verbose_name_plural = "árbol analítico"
        ordering = ["position", "code"]

    def __str__(self):
        return f"{self.position}. {self.get_code_display()}"


class ErpConnection(models.Model):
    """Parámetros de lectura del origen. El secreto no se muestra de nuevo en claro."""

    name = models.CharField(max_length=80, default="principal")
    host = models.CharField(max_length=200)
    database = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)

    class Meta:
        verbose_name = "conexión al origen"
        verbose_name_plural = "conexiones al origen"

    def __str__(self):
        return self.name
