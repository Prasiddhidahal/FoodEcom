# Generated by Django 5.1.2 on 2024-12-11 05:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_product_weight'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='image',
            new_name='main_image',
        ),
    ]
