# Generated by Django 5.0.7 on 2025-03-17 11:35

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_delete_ownershiptransfer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('employee_fname', models.CharField(blank=True, max_length=100, null=True)),
                ('employee_mname', models.CharField(blank=True, max_length=100, null=True)),
                ('employee_lname', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OwnershipHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('previous_owner', models.CharField(max_length=100)),
                ('previous_designation', models.CharField(max_length=100)),
                ('previous_section', models.CharField(max_length=100)),
                ('transfer_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('desktop_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.desktop_package')),
            ],
        ),
        migrations.CreateModel(
            name='OwnershipTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transferred_from', models.CharField(blank=True, max_length=100, null=True)),
                ('transferred_to', models.CharField(max_length=100)),
                ('owner_designation', models.CharField(blank=True, max_length=100, null=True)),
                ('owner_section', models.CharField(blank=True, max_length=100, null=True)),
                ('transfer_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True, null=True)),
                ('desktop_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.desktop_package')),
            ],
        ),
    ]
