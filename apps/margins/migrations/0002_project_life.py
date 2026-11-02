import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("margins", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectLife",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo_empresa", models.CharField(max_length=15)),
                ("codigo_proyecto", models.CharField(max_length=40)),
                ("order_date", models.DateField(blank=True, null=True)),
                ("order_base", models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ("incomplete", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "vida del proyecto",
                "verbose_name_plural": "vidas de proyecto",
            },
        ),
        migrations.CreateModel(
            name="ProjectMilestone",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ejercicio", models.IntegerField()),
                ("serie", models.CharField(max_length=10)),
                ("numero", models.CharField(max_length=20)),
                ("delivery_date", models.DateField(blank=True, null=True)),
                ("amount", models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ("billing", models.CharField(max_length=20)),
                (
                    "life",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="milestones",
                        to="margins.projectlife",
                    ),
                ),
            ],
            options={
                "verbose_name": "hito de albarán",
                "verbose_name_plural": "hitos de albarán",
            },
        ),
        migrations.CreateModel(
            name="ProjectPurchase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(max_length=20)),
                ("ejercicio", models.IntegerField()),
                ("serie", models.CharField(max_length=10)),
                ("numero", models.CharField(max_length=20)),
                ("supplier_code", models.CharField(blank=True, max_length=20)),
                ("supplier_name", models.CharField(blank=True, max_length=120)),
                ("document_date", models.DateField(blank=True, null=True)),
                ("amount", models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ("linked_ejercicio", models.CharField(blank=True, max_length=10)),
                ("linked_serie", models.CharField(blank=True, max_length=10)),
                ("linked_numero", models.CharField(blank=True, max_length=20)),
                (
                    "life",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="purchases",
                        to="margins.projectlife",
                    ),
                ),
            ],
            options={
                "verbose_name": "compra del proyecto",
                "verbose_name_plural": "compras del proyecto",
            },
        ),
        migrations.CreateModel(
            name="ProjectExpense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("account_code", models.CharField(max_length=20)),
                ("account_name", models.CharField(blank=True, max_length=120)),
                ("movement_date", models.DateField(blank=True, null=True)),
                ("amount", models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                (
                    "life",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expenses",
                        to="margins.projectlife",
                    ),
                ),
            ],
            options={
                "verbose_name": "gasto del proyecto",
                "verbose_name_plural": "gastos del proyecto",
            },
        ),
        migrations.AddConstraint(
            model_name="projectlife",
            constraint=models.UniqueConstraint(
                fields=("codigo_empresa", "codigo_proyecto"),
                name="unique_project_life",
            ),
        ),
    ]
