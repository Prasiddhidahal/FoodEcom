# Generated by Django 5.1.2 on 2024-12-11 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_rename_main_image_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='products/'),
        ),
        migrations.AlterField(
            model_name='productimages',
            name='image',
            field=models.ImageField(upload_to='products/images/'),
        ),
    ]