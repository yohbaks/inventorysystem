# Generated by Django 5.0.4 on 2024-10-21 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_rename_brand_keyboarddetails_keyboard_sn_db_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='keyboarddetails',
            old_name='keyboardbrand',
            new_name='keyboard_brand_db',
        ),
    ]
