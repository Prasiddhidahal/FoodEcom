# Generated by Django 5.1.2 on 2025-01-29 07:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0064_advertisement_aid'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advertisementimage',
            name='advertisement',
        ),
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='category')),
                ('status', models.CharField(choices=[('Active', 'Active'), ('outofstock', 'Out of Stock'), ('Pending', 'Pending'), ('Discontinued', 'Discontinued'), ('Inactive', 'Inactive')], default='Active', max_length=20)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_Ad', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Ad',
            },
        ),
        migrations.CreateModel(
            name='Adimage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='Ad/images/')),
                ('Ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='core.ad')),
            ],
        ),
        migrations.DeleteModel(
            name='Advertisement',
        ),
        migrations.DeleteModel(
            name='AdvertisementImage',
        ),
    ]
