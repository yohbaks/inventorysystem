# Generated by Django 5.0.4 on 2024-10-20 10:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0020_mousedetails_is_disposed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mousedetails',
            name='desktop_package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mouse', to='inventory.desktop_package'),
        ),
    ]