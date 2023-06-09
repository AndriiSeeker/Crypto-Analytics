# Generated by Django 4.2.1 on 2023-05-17 15:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cryptocurrency", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="crypto",
            name="circulating_supply",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="coin_id",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="percent_change_1h",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="percent_change_24h",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="percent_change_7d",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="price",
            field=models.IntegerField(),
        ),
    ]