# Generated by Django 5.0.4 on 2025-03-18 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_employee_employee_office_employee_employee_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='status',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
