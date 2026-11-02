from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("margins", "0015_tree_income"),
    ]

    operations = [
        migrations.CreateModel(
            name="FinancialReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=40, unique=True, verbose_name="código")),
                ("description", models.CharField(max_length=160, verbose_name="descripción")),
            ],
            options={
                "verbose_name": "informe financiero",
                "verbose_name_plural": "informes financieros",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="FinancialReportLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "position",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Si lo dejas vacío, se asigna el siguiente de 10 en 10. Un número intermedio inserta la línea.",
                        null=True,
                        verbose_name="orden",
                    ),
                ),
                ("text", models.CharField(max_length=200, verbose_name="texto")),
                (
                    "accounts",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Grupos de 1 a 4 dígitos o códigos completos, separados por comas.",
                        verbose_name="cuentas",
                    ),
                ),
                (
                    "is_total",
                    models.BooleanField(
                        default=False,
                        help_text="Marca la línea como total.",
                        verbose_name="total",
                    ),
                ),
                (
                    "report",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lines",
                        to="margins.financialreport",
                        verbose_name="informe",
                    ),
                ),
            ],
            options={
                "verbose_name": "línea de informe",
                "verbose_name_plural": "líneas de informe",
                "ordering": ["position", "id"],
            },
        ),
    ]
