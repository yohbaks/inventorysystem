# Generated by Django 5.0.7 on 2025-03-18 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_rename_status_employee_employee_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyboarddetails',
            name='keyboard_size_db',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
