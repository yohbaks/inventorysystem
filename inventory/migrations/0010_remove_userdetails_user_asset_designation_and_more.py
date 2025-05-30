# Generated by Django 5.0.7 on 2025-04-01 10:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_rename_brand_db_upsdetails_ups_brand_db_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdetails',
            name='user_Asset_designation',
        ),
        migrations.RemoveField(
            model_name='userdetails',
            name='user_Asset_owner',
        ),
        migrations.RemoveField(
            model_name='userdetails',
            name='user_Asset_section',
        ),
        migrations.AlterField(
            model_name='userdetails',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='userdetails',
            name='desktop_package_db',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.desktop_package'),
        ),
        migrations.AlterField(
            model_name='userdetails',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='userdetails',
            name='user_Enduser',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.employee'),
        ),
    ]
