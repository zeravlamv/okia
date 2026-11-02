from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("margins", "0008_projectpurchase_billing"),
    ]

    operations = [
        migrations.CreateModel(
            name="MonthLedger",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo_empresa", models.CharField(max_length=15)),
                ("ejercicio", models.PositiveIntegerField()),
                ("mes", models.PositiveSmallIntegerField(choices=[(1, "enero"), (2, "febrero"), (3, "marzo"), (4, "abril"), (5, "mayo"), (6, "junio"), (7, "julio"), (8, "agosto"), (9, "septiembre"), (10, "octubre"), (11, "noviembre"), (12, "diciembre")])),
                ("income_count", models.PositiveIntegerField(default=0)),
                ("income_amount", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("expense_count", models.PositiveIntegerField(default=0)),
                ("expense_amount", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
            ],
            options={
                "verbose_name": "mes del libro",
                "verbose_name_plural": "meses del libro",
            },
        ),
        migrations.AddConstraint(
            model_name="monthledger",
            constraint=models.UniqueConstraint(fields=("codigo_empresa", "ejercicio", "mes"), name="unique_month_ledger"),
        ),
        migrations.AddConstraint(
            model_name="monthledger",
            constraint=models.CheckConstraint(condition=Q(mes__gte=1) & Q(mes__lte=12), name="month_ledger_month"),
        ),
    ]
