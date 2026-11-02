from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("margins", "0010_cost_accounts"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectlife",
            name="income_stored",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="ProjectIncome",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("account_code", models.CharField(max_length=20)),
                ("account_name", models.CharField(blank=True, max_length=120)),
                ("movement_date", models.DateField(blank=True, null=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=18, null=True)),
                ("department_code", models.CharField(blank=True, default="", max_length=40)),
                ("department_name", models.CharField(blank=True, default="", max_length=160)),
                ("section_code", models.CharField(blank=True, default="", max_length=40)),
                ("section_name", models.CharField(blank=True, default="", max_length=160)),
                (
                    "life",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incomes",
                        to="margins.projectlife",
                    ),
                ),
            ],
            options={
                "verbose_name": "ingreso del proyecto",
                "verbose_name_plural": "ingresos del proyecto",
            },
        ),
    ]
