# Generated by Django 5.0.4 on 2025-05-10 03:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0028_disposedmonitor_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='disposedkeyboard',
            name='disposed_under',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disposed_keyboards', to='inventory.disposeddesktopdetail'),
        ),
    ]
