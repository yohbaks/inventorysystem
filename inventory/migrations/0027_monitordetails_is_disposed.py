# Generated by Django 5.0.4 on 2024-10-28 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0026_rename_keyboardx_disposedkeyboard_keyboard_dispose_db'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitordetails',
            name='is_disposed',
            field=models.BooleanField(default=False),
        ),
    ]
