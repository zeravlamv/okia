from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("margins", "0007_project_exercise_share"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectpurchase",
            name="billing",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
    ]
