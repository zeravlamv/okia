from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class DashboardSnapshot(models.Model):
    """Resumen de una empresa y un ejercicio. La página lo lee y no vuelve a calcularlo."""

    codigo_empresa = models.CharField(max_length=15)
    ejercicio = models.PositiveIntegerField()
    titulo_1 = models.CharField(max_length=40, blank=True)
    titulo_2 = models.CharField(max_length=40, blank=True)
    titulo_3 = models.CharField(max_length=40, blank=True)
    titulo_4 = models.CharField(max_length=40, blank=True)
    titulo_5 = models.CharField(max_length=40, blank=True, default="")
    sales_count = models.PositiveIntegerField(default=0)
    sales_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    purchase_order_count = models.PositiveIntegerField(default=0)
    purchase_order_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    sales_delivery_count = models.PositiveIntegerField(default=0)
    sales_delivery_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    purchase_delivery_count = models.PositiveIntegerField(default=0)
    purchase_delivery_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    income_count = models.PositiveIntegerField(default=0)
    income_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    expense_count = models.PositiveIntegerField(default=0)
    expense_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    purchase_cost_count = models.PositiveIntegerField(default=0)
    purchase_cost_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    pending_count = models.PositiveIntegerField(default=0)
    book_stored = models.BooleanField(default=False)
    income_stored = models.BooleanField(default=False)
    tree_income_stored = models.BooleanField(default=False)
    tree_expense_stored = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "resumen del cuadro de mando"
        verbose_name_plural = "resúmenes del cuadro de mando"
        constraints = [
            models.UniqueConstraint(
                fields=["codigo_empresa", "ejercicio"],
                name="unique_dashboard_snapshot",
            )
        ]


class AnalyticalSummary(models.Model):
    """Una combinación de los niveles del árbol analítico."""

    snapshot = models.ForeignKey(
        DashboardSnapshot,
        on_delete=models.CASCADE,
        related_name="rows",
    )
    nivel_1 = models.CharField(max_length=500, blank=True)
    nivel_2 = models.CharField(max_length=500, blank=True)
    nivel_3 = models.CharField(max_length=500, blank=True)
    nivel_4 = models.CharField(max_length=500, blank=True)
    nivel_5 = models.CharField(max_length=500, blank=True, default="")
    sales = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    income = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    purchases = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    expenses = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    margin = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    incomplete = models.BooleanField(default=False)

    class Meta:
        verbose_name = "fila del resumen analítico"
        verbose_name_plural = "filas del resumen analítico"


class AsideSummary(models.Model):
    snapshot = models.ForeignKey(
        DashboardSnapshot,
        on_delete=models.CASCADE,
        related_name="aside_rows",
    )
    identity = models.CharField(max_length=80)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    incomplete = models.BooleanField(default=False)

    class Meta:
        verbose_name = "pedido fuera de la jerarquía"
        verbose_name_plural = "pedidos fuera de la jerarquía"


REVIEW_PENDING = "Pdte. Revisar"
REVIEW_DONE = "Revisado"


class ProjectLife(models.Model):
    """Vida de un proyecto, desde la fecha del pedido, aunque cruce varios ejercicios."""

    codigo_empresa = models.CharField(max_length=15)
    codigo_proyecto = models.CharField(max_length=40)
    order_date = models.DateField(null=True, blank=True)
    order_base = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    customer_code = models.CharField(max_length=40, blank=True, default="")
    customer_name = models.CharField(max_length=160, blank=True, default="")
    incomplete = models.BooleanField(default=False)
    levels_stored = models.BooleanField(default=False)
    lines_stored = models.BooleanField(default=False)
    income_stored = models.BooleanField(default=False)
    review_status = models.CharField(
        max_length=20,
        choices=((REVIEW_PENDING, REVIEW_PENDING), (REVIEW_DONE, REVIEW_DONE)),
        default=REVIEW_PENDING,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "vida del proyecto"
        verbose_name_plural = "vidas de proyecto"
        constraints = [
            models.UniqueConstraint(
                fields=["codigo_empresa", "codigo_proyecto"],
                name="unique_project_life",
            )
        ]


class ProjectOrderShare(models.Model):
    """Base del pedido en su departamento y su sección."""

    life = models.ForeignKey(ProjectLife, on_delete=models.CASCADE, related_name="order_shares")
    department_code = models.CharField(max_length=40, blank=True, default="")
    department_name = models.CharField(max_length=160, blank=True, default="")
    section_code = models.CharField(max_length=40, blank=True, default="")
    section_name = models.CharField(max_length=160, blank=True, default="")
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True)

    class Meta:
        verbose_name = "pedido del proyecto"
        verbose_name_plural = "pedidos del proyecto"


class ProjectMilestone(models.Model):
    life = models.ForeignKey(ProjectLife, on_delete=models.CASCADE, related_name="milestones")
    ejercicio = models.IntegerField()
    serie = models.CharField(max_length=10)
    numero = models.CharField(max_length=20)
    delivery_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    billing = models.CharField(max_length=20)
    department_code = models.CharField(max_length=40, blank=True, default="")
    department_name = models.CharField(max_length=160, blank=True, default="")
    section_code = models.CharField(max_length=40, blank=True, default="")
    section_name = models.CharField(max_length=160, blank=True, default="")

    class Meta:
        verbose_name = "hito de albarán"
        verbose_name_plural = "hitos de albarán"


class ProjectPurchase(models.Model):
    life = models.ForeignKey(ProjectLife, on_delete=models.CASCADE, related_name="purchases")
    kind = models.CharField(max_length=20)
    ejercicio = models.IntegerField()
    serie = models.CharField(max_length=10)
    numero = models.CharField(max_length=20)
    supplier_code = models.CharField(max_length=20, blank=True)
    supplier_name = models.CharField(max_length=120, blank=True)
    document_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    billing = models.CharField(max_length=20, blank=True, default="")
    linked_ejercicio = models.CharField(max_length=10, blank=True)
    linked_serie = models.CharField(max_length=10, blank=True)
    linked_numero = models.CharField(max_length=20, blank=True)
    department_code = models.CharField(max_length=40, blank=True, default="")
    department_name = models.CharField(max_length=160, blank=True, default="")
    section_code = models.CharField(max_length=40, blank=True, default="")
    section_name = models.CharField(max_length=160, blank=True, default="")

    class Meta:
        verbose_name = "compra del proyecto"
        verbose_name_plural = "compras del proyecto"


class ProjectExpense(models.Model):
    life = models.ForeignKey(ProjectLife, on_delete=models.CASCADE, related_name="expenses")
    account_code = models.CharField(max_length=20)
    account_name = models.CharField(max_length=120, blank=True)
    movement_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    department_code = models.CharField(max_length=40, blank=True, default="")
    department_name = models.CharField(max_length=160, blank=True, default="")
    section_code = models.CharField(max_length=40, blank=True, default="")
    section_name = models.CharField(max_length=160, blank=True, default="")

    class Meta:
        verbose_name = "gasto del proyecto"
        verbose_name_plural = "gastos del proyecto"


class AccountGroup(models.Model):
    """Descripción de un grupo de 1 a 4 dígitos. Se guarda al actualizar."""

    codigo_empresa = models.CharField(max_length=15)
    code = models.CharField(max_length=4)
    description = models.CharField(max_length=160, blank=True)

    class Meta:
        verbose_name = "grupo de cuenta"
        verbose_name_plural = "grupos de cuenta"
        constraints = [
            models.UniqueConstraint(
                fields=["codigo_empresa", "code"],
                name="unique_account_group",
            )
        ]


class BookExpense(models.Model):
    """Apunte del libro que no entró en las compras de un proyecto. Se guarda al actualizar."""

    codigo_empresa = models.CharField(max_length=15)
    ejercicio = models.PositiveIntegerField()
    account_code = models.CharField(max_length=20)
    account_name = models.CharField(max_length=120, blank=True)
    movement_date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    project_code = models.CharField(max_length=40, blank=True, default="")
    department_code = models.CharField(max_length=40, blank=True, default="")
    department_name = models.CharField(max_length=160, blank=True, default="")
    section_code = models.CharField(max_length=40, blank=True, default="")
    section_name = models.CharField(max_length=160, blank=True, default="")

    class Meta:
        verbose_name = "gasto del libro"
        verbose_name_plural = "gastos del libro"


class TreeIncome(models.Model):
    """Ingreso del árbol analítico, con el nivel donde cayó el apunte."""

    codigo_empresa = models.CharField(max_length=15)
    ejercicio = models.PositiveIntegerField()
    movement_date = models.DateField(null=True, blank=True)
    asiento = models.CharField(max_length=20, blank=True, default="")
    account_code = models.CharField(max_length=20, blank=True, default="")
    account_name = models.CharField(max_length=120, blank=True, default="")
    invoice = models.CharField(max_length=40, blank=True, default="")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    nivel_1 = models.CharField(max_length=500, blank=True, default="")
    nivel_2 = models.CharField(max_length=500, blank=True, default="")
    nivel_3 = models.CharField(max_length=500, blank=True, default="")
    nivel_4 = models.CharField(max_length=500, blank=True, default="")
    nivel_5 = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        verbose_name = "ingreso del árbol"
        verbose_name_plural = "ingresos del árbol"


class TreeExpense(models.Model):
    """Gasto del árbol analítico, con el nivel donde cayó el apunte."""

    codigo_empresa = models.CharField(max_length=15)
    ejercicio = models.PositiveIntegerField()
    movement_date = models.DateField(null=True, blank=True)
    asiento = models.CharField(max_length=20, blank=True, default="")
    account_code = models.CharField(max_length=20, blank=True, default="")
    account_name = models.CharField(max_length=120, blank=True, default="")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    nivel_1 = models.CharField(max_length=500, blank=True, default="")
    nivel_2 = models.CharField(max_length=500, blank=True, default="")
    nivel_3 = models.CharField(max_length=500, blank=True, default="")
    nivel_4 = models.CharField(max_length=500, blank=True, default="")
    nivel_5 = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        verbose_name = "gasto del árbol"
        verbose_name_plural = "gastos del árbol"


class BookIncome(models.Model):
    """Apunte de ingreso del grupo 7. Se guarda al actualizar."""

    codigo_empresa = models.CharField(max_length=15)
    ejercicio = models.PositiveIntegerField()
    account_code = models.CharField(max_length=20)
    account_name = models.CharField(max_length=120, blank=True)
    movement_date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    project_code = models.CharField(max_length=40, blank=True, default="")
    department_code = models.CharField(max_length=40, blank=True, default="")
    department_name = models.CharField(max_length=160, blank=True, default="")
    section_code = models.CharField(max_length=40, blank=True, default="")
    section_name = models.CharField(max_length=160, blank=True, default="")

    class Meta:
        verbose_name = "ingreso del libro"
        verbose_name_plural = "ingresos del libro"


class ProjectIncome(models.Model):
    """Ingreso del grupo 7 imputado al proyecto. Se guarda al actualizar."""

    life = models.ForeignKey(ProjectLife, on_delete=models.CASCADE, related_name="incomes")
    account_code = models.CharField(max_length=20)
    account_name = models.CharField(max_length=120, blank=True)
    movement_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    department_code = models.CharField(max_length=40, blank=True, default="")
    department_name = models.CharField(max_length=160, blank=True, default="")
    section_code = models.CharField(max_length=40, blank=True, default="")
    section_name = models.CharField(max_length=160, blank=True, default="")

    class Meta:
        verbose_name = "ingreso del proyecto"
        verbose_name_plural = "ingresos del proyecto"


class ProjectDocumentLine(models.Model):
    """Línea de un pedido o de un albarán del proyecto."""

    life = models.ForeignKey(ProjectLife, on_delete=models.CASCADE, related_name="lines")
    kind = models.CharField(max_length=20)
    document_key = models.CharField(max_length=80)
    position = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=160, blank=True, default="")
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    line_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "línea de documento"
        verbose_name_plural = "líneas de documento"


MONTH_NAMES = (
    (1, "enero"),
    (2, "febrero"),
    (3, "marzo"),
    (4, "abril"),
    (5, "mayo"),
    (6, "junio"),
    (7, "julio"),
    (8, "agosto"),
    (9, "septiembre"),
    (10, "octubre"),
    (11, "noviembre"),
    (12, "diciembre"),
)


class PeriodClosure(models.Model):
    """Un mes de un ejercicio. Si no hay fila, el mes está abierto."""

    codigo_empresa = models.CharField("Empresa", max_length=15)
    ejercicio = models.PositiveIntegerField("Ejercicio")
    mes = models.PositiveSmallIntegerField("Mes", choices=MONTH_NAMES)
    cerrado = models.BooleanField("Cerrado", default=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Cambiado por",
        on_delete=models.PROTECT,
        related_name="period_closures",
    )
    changed_at = models.DateTimeField("Cambiado el", auto_now=True)

    class Meta:
        verbose_name = "cierre de mes"
        verbose_name_plural = "cierres de mes"
        constraints = [
            models.UniqueConstraint(
                fields=["codigo_empresa", "ejercicio", "mes"],
                name="unique_period_closure",
            ),
            models.CheckConstraint(
                condition=Q(mes__gte=1) & Q(mes__lte=12),
                name="period_closure_month",
            ),
        ]

    def clean(self):
        super().clean()
        if self.mes not in range(1, 13):
            raise ValidationError({"mes": "Un valor fuera de ese rango no se guarda."})

    def __str__(self):
        state = "cerrado" if self.cerrado else "abierto"
        return f"{self.codigo_empresa} {self.ejercicio} {self.get_mes_display()} {state}"


class MonthLedger(models.Model):
    """Ingresos y gastos de un mes, por la fecha del apunte. No dependen del proyecto."""

    codigo_empresa = models.CharField(max_length=15)
    ejercicio = models.PositiveIntegerField()
    mes = models.PositiveSmallIntegerField(choices=MONTH_NAMES)
    income_count = models.PositiveIntegerField(default=0)
    income_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    expense_count = models.PositiveIntegerField(default=0)
    expense_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    purchase_count = models.PositiveIntegerField(default=0)
    purchase_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "mes del libro"
        verbose_name_plural = "meses del libro"
        constraints = [
            models.UniqueConstraint(
                fields=["codigo_empresa", "ejercicio", "mes"],
                name="unique_month_ledger",
            ),
            models.CheckConstraint(
                condition=Q(mes__gte=1) & Q(mes__lte=12),
                name="month_ledger_month",
            ),
        ]


class ProjectExerciseShare(models.Model):
    """Aportación de un proyecto al ejercicio la última vez que se actualizó abierto."""

    codigo_empresa = models.CharField(max_length=15)
    codigo_proyecto = models.CharField(max_length=40)
    ejercicio = models.PositiveIntegerField()
    sales_count = models.PositiveIntegerField(default=0)
    sales_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    purchase_order_count = models.PositiveIntegerField(default=0)
    purchase_order_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    sales_delivery_count = models.PositiveIntegerField(default=0)
    sales_delivery_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    purchase_delivery_count = models.PositiveIntegerField(default=0)
    purchase_delivery_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    income_count = models.PositiveIntegerField(default=0)
    income_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    expense_count = models.PositiveIntegerField(default=0)
    expense_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    nivel_1 = models.CharField(max_length=500, blank=True, default="")
    nivel_2 = models.CharField(max_length=500, blank=True, default="")
    nivel_3 = models.CharField(max_length=500, blank=True, default="")
    nivel_4 = models.CharField(max_length=500, blank=True, default="")
    nivel_5 = models.CharField(max_length=500, blank=True, default="")
    sales = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    income = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    purchases = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    expenses = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    margin = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    incomplete = models.BooleanField(default=False)

    class Meta:
        verbose_name = "aportación del proyecto"
        verbose_name_plural = "aportaciones del proyecto"
        constraints = [
            models.UniqueConstraint(
                fields=["codigo_empresa", "codigo_proyecto", "ejercicio"],
                name="unique_project_exercise_share",
            )
        ]


class FinancialReport(models.Model):
    """Definición de un informe. Todavía no calcula importes."""

    code = models.CharField("código", max_length=40, unique=True)
    description = models.CharField("descripción", max_length=160)

    class Meta:
        verbose_name = "informe financiero"
        verbose_name_plural = "informes financieros"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.description}"


class FinancialReportLine(models.Model):
    """Una línea del informe: texto, cuentas y, si corresponde, la marca de total."""

    report = models.ForeignKey(
        FinancialReport,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="informe",
    )
    position = models.PositiveIntegerField(
        "orden",
        null=True,
        blank=True,
        help_text="Si lo dejas vacío, se asigna el siguiente de 10 en 10. Un número intermedio inserta la línea.",
    )
    text = models.CharField("texto", max_length=200)
    accounts = models.TextField(
        "cuentas",
        blank=True,
        default="",
        help_text="Grupos de 1 a 4 dígitos o códigos completos, separados por comas.",
    )
    is_total = models.BooleanField("total", default=False, help_text="Marca la línea como total.")

    class Meta:
        verbose_name = "línea de informe"
        verbose_name_plural = "líneas de informe"
        ordering = ["position", "id"]

    def __str__(self):
        return self.text

    def clean(self):
        tokens = []
        for piece in str(self.accounts or "").replace(";", ",").replace("\n", ",").split(","):
            token = piece.strip()
            if not token:
                continue
            if not token.isdigit():
                raise ValidationError({"accounts": "Cada cuenta o grupo debe ser numérico."})
            tokens.append(token)
        self.accounts = ", ".join(tokens)

    def save(self, *args, **kwargs):
        if not self.position:
            self.position = _next_report_position(self.report)
        super().save(*args, **kwargs)


def _next_report_position(report):
    last = report.lines.order_by("-position").values_list("position", flat=True).first()
    if not last:
        return 10
    return int(last) + 10


def renumber_report_lines(report):
    """Deja las líneas en 10, 20, 30… según el orden actual."""

    for index, line in enumerate(report.lines.order_by("position", "id"), start=1):
        wanted = index * 10
        if line.position != wanted:
            FinancialReportLine.objects.filter(pk=line.pk).update(position=wanted)


class OrderSummary(models.Model):
    snapshot = models.ForeignKey(
        DashboardSnapshot,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    identity = models.CharField(max_length=80)
    project = models.CharField(max_length=40)
    price = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    cost = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    margin = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    income = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    incomplete = models.BooleanField(default=False)

    class Meta:
        verbose_name = "margen de pedido guardado"
        verbose_name_plural = "márgenes de pedido guardados"
