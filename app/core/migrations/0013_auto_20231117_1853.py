# Generated by Django 3.2.5 on 2023-11-17 18:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_investmenttransaction_asset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investmentasset',
            name='total_value',
        ),
        migrations.AlterField(
            model_name='investmenttransaction',
            name='asset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.investmentasset'),
        ),
    ]
