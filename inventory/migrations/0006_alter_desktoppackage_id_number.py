# Generated by Django 5.0.4 on 2024-09-04 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_remove_desktoppackage_id_desktoppackage_id_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='desktoppackage',
            name='id_number',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
