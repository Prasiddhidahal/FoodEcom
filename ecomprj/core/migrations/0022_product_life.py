# Generated by Django 5.1.2 on 2024-12-11 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_product_mfd'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='life',
            field=models.IntegerField(default=30),
        ),
    ]