# Generated by Django 5.1.2 on 2025-01-07 16:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_cartorder_in_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=2025, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='core.category'),
            preserve_default=False,
        ),
    ]