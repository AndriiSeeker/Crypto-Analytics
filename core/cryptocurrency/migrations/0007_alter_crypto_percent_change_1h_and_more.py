# Generated by Django 4.2.1 on 2023-05-29 06:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cryptocurrency", "0006_news"),
    ]

    operations = [
        migrations.AlterField(
            model_name="crypto",
            name="percent_change_1h",
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="percent_change_24h",
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="percent_change_7d",
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
