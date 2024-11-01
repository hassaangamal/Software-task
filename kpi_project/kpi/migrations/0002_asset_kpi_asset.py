# Generated by Django 5.1.2 on 2024-10-31 15:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kpi", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Asset",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("asset_id", models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="kpi",
            name="asset",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="kpis",
                to="kpi.asset",
            ),
        ),
    ]
