# Generated by Django 5.0.4 on 2024-10-21 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0024_rename_keyboardbrand_keyboarddetails_keyboard_brand_db'),
    ]

    operations = [
        migrations.RenameField(
            model_name='keyboarddetails',
            old_name='model',
            new_name='keyboard_model_db',
        ),
    ]