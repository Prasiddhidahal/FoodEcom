# Generated by Django 5.1.2 on 2024-10-24 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='address',
        ),
        migrations.RemoveField(
            model_name='user',
            name='city',
        ),
        migrations.RemoveField(
            model_name='user',
            name='country',
        ),
        migrations.RemoveField(
            model_name='user',
            name='date_of_birth',
        ),
        migrations.RemoveField(
            model_name='user',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='user',
            name='profile_pic',
        ),
        migrations.RemoveField(
            model_name='user',
            name='state',
        ),
        migrations.RemoveField(
            model_name='user',
            name='zip_code',
        ),
    ]
