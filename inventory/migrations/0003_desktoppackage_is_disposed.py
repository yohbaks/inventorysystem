# Generated by Django 5.0.4 on 2024-09-10 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_desktoppackage_desktop_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='desktoppackage',
            name='is_disposed',
            field=models.BooleanField(default=False),
        ),
    ]
