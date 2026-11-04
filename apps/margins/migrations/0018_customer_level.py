from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("margins", "0017_tree_expense"),
    ]

    operations = [
        migrations.AddField(
            model_name="dashboardsnapshot",
            name="titulo_5",
            field=models.CharField(blank=True, default="", max_length=40),
        ),
        migrations.AddField(
            model_name="analyticalsummary",
            name="nivel_5",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="treeincome",
            name="nivel_5",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="treeexpense",
            name="nivel_5",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="projectexerciseshare",
            name="nivel_5",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
    ]
