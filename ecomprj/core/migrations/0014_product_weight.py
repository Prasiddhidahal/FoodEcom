# Generated by Django 5.1.2 on 2024-12-11 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_vendor_old_price_vendor_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.FloatField(default=0),
        ),
    ]
