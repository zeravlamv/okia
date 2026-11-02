from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("margins", "0006_period_close"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectExerciseShare",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo_empresa", models.CharField(max_length=15)),
                ("codigo_proyecto", models.CharField(max_length=40)),
                ("ejercicio", models.PositiveIntegerField()),
                ("sales_count", models.PositiveIntegerField(default=0)),
                ("sales_amount", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("purchase_order_count", models.PositiveIntegerField(default=0)),
                ("purchase_order_amount", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("sales_delivery_count", models.PositiveIntegerField(default=0)),
                ("sales_delivery_amount", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("purchase_delivery_count", models.PositiveIntegerField(default=0)),
                ("purchase_delivery_amount", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("income_count", models.PositiveIntegerField(default=0)),
                ("income_amount", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("expense_count", models.PositiveIntegerField(default=0)),
                ("expense_amount", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("nivel_1", models.CharField(blank=True, default="", max_length=500)),
                ("nivel_2", models.CharField(blank=True, default="", max_length=500)),
                ("nivel_3", models.CharField(blank=True, default="", max_length=500)),
                ("nivel_4", models.CharField(blank=True, default="", max_length=500)),
                ("sales", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("income", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("purchases", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("expenses", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("margin", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("incomplete", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "aportación del proyecto",
                "verbose_name_plural": "aportaciones del proyecto",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("codigo_empresa", "codigo_proyecto", "ejercicio"),
                        name="unique_project_exercise_share",
                    )
                ],
            },
        ),
    ]
