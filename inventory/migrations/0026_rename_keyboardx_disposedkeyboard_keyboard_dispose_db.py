# Generated by Django 5.0.4 on 2024-10-21 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_rename_model_keyboarddetails_keyboard_model_db'),
    ]

    operations = [
        migrations.RenameField(
            model_name='disposedkeyboard',
            old_name='keyboardx',
            new_name='keyboard_dispose_db',
        ),
    ]
