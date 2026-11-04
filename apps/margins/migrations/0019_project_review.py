from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("margins", "0018_customer_level"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectlife",
            name="review_status",
            field=models.CharField(
                choices=[("Pdte. Revisar", "Pdte. Revisar"), ("Revisado", "Revisado")],
                default="Pdte. Revisar",
                max_length=20,
            ),
        ),
    ]
