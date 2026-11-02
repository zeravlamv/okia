from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("margins", "0014_account_groups"),
    ]

    operations = [
        migrations.AddField(
            model_name="dashboardsnapshot",
            name="tree_income_stored",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="TreeIncome",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo_empresa", models.CharField(max_length=15)),
                ("ejercicio", models.PositiveIntegerField()),
                ("movement_date", models.DateField(blank=True, null=True)),
                ("asiento", models.CharField(blank=True, default="", max_length=20)),
                ("account_code", models.CharField(blank=True, default="", max_length=20)),
                ("account_name", models.CharField(blank=True, default="", max_length=120)),
                ("invoice", models.CharField(blank=True, default="", max_length=40)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("nivel_1", models.CharField(blank=True, default="", max_length=500)),
                ("nivel_2", models.CharField(blank=True, default="", max_length=500)),
                ("nivel_3", models.CharField(blank=True, default="", max_length=500)),
                ("nivel_4", models.CharField(blank=True, default="", max_length=500)),
            ],
            options={
                "verbose_name": "ingreso del árbol",
                "verbose_name_plural": "ingresos del árbol",
            },
        ),
    ]
