# Generated by Django 3.2.5 on 2023-11-10 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20231110_1731'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='balacne',
            new_name='balance',
        ),
    ]
