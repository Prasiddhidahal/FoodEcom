# Generated by Django 5.1.2 on 2024-10-24 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0004_remove_user_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
