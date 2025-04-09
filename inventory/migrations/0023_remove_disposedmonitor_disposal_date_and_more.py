# Generated by Django 5.0.7 on 2025-04-09 01:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0022_disposedmonitor_disposed_under'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='disposedmonitor',
            name='disposal_date',
        ),
        migrations.AddField(
            model_name='disposeddesktopdetail',
            name='asset_owner',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='disposeddesktopdetail',
            name='brand_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='disposeddesktopdetail',
            name='desktop_package_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='disposeddesktopdetail',
            name='model',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='disposeddesktopdetail',
            name='serial_no',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='disposedmonitor',
            name='date_disposed',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='disposedmonitor',
            name='monitor_brand',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='disposedmonitor',
            name='monitor_model',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='disposedmonitor',
            name='monitor_size',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='disposedmonitor',
            name='monitor_sn',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='disposedmonitor',
            name='disposed_under',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disposed_monitors', to='inventory.disposeddesktopdetail'),
        ),
    ]
