# Generated by Django 5.1.2 on 2024-11-13 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rename_productimage_productimages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartorderitems',
            name='image',
            field=models.ImageField(upload_to='product_images'),
        ),
    ]