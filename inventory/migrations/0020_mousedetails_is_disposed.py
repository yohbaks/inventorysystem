# Generated by Django 5.0.4 on 2024-10-15 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_alter_desktopdetails_id_alter_keyboarddetails_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mousedetails',
            name='is_disposed',
            field=models.BooleanField(default=False),
        ),
    ]