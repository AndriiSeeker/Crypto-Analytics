# Generated by Django 4.2.1 on 2023-06-01 14:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0009_alter_profile_avatar"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=models.CharField(max_length=300, null=True),
        ),
    ]
