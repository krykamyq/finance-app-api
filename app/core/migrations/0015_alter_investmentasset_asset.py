# Generated by Django 3.2.5 on 2023-11-18 20:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_investmentasset_total_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investmentasset',
            name='asset',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.asset'),
        ),
    ]
