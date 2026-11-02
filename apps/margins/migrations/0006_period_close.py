import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("margins", "0005_projectlife_lines_stored_projectdocumentline"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PeriodClosure",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo_empresa", models.CharField(max_length=15, verbose_name="Empresa")),
                ("ejercicio", models.PositiveIntegerField(verbose_name="Ejercicio")),
                (
                    "mes",
                    models.PositiveSmallIntegerField(
                        choices=[
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
                        ],
                        verbose_name="Mes",
                    ),
                ),
                ("cerrado", models.BooleanField(default=True, verbose_name="Cerrado")),
                ("changed_at", models.DateTimeField(auto_now=True, verbose_name="Cambiado el")),
                (
                    "changed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="period_closures",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Cambiado por",
                    ),
                ),
            ],
            options={
                "verbose_name": "cierre de mes",
                "verbose_name_plural": "cierres de mes",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("codigo_empresa", "ejercicio", "mes"),
                        name="unique_period_closure",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(mes__gte=1) & models.Q(mes__lte=12),
                        name="period_closure_month",
                    ),
                ],
            },
        ),
    ]
