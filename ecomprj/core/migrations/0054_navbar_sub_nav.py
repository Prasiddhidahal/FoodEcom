# Generated by Django 5.1.2 on 2025-01-22 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_alter_navbar_created_by_alter_navbar_parent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='navbar',
            name='sub_nav',
            field=models.BooleanField(default=False),
        ),
    ]
