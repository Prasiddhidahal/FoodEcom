# Generated by Django 5.1.2 on 2025-01-01 13:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_address_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]