# Generated by Django 5.1.2 on 2024-12-11 05:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_rename_image_product_main_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='main_image',
            new_name='image',
        ),
    ]
