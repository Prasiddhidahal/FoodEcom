# Generated by Django 5.1.2 on 2025-02-28 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0071_alter_footer_options_remove_footer_created_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='footer',
            name='content_status',
        ),
        migrations.AddField(
            model_name='footer',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('outofstock', 'Out of Stock'), ('Pending', 'Pending'), ('Discontinued', 'Discontinued'), ('Inactive', 'Inactive')], default='Active', max_length=20),
        ),
    ]
