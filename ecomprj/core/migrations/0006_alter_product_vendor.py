# Generated by Django 5.1.2 on 2024-11-13 15:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_product_vendor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='Vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.vendor'),
        ),
    ]
