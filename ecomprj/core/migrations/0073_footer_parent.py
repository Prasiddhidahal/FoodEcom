# Generated by Django 5.1.2 on 2025-02-28 08:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0072_remove_footer_content_status_footer_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='footer',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='core.footer'),
        ),
    ]
