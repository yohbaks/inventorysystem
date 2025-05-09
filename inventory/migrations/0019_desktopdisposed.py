# Generated by Django 5.0.7 on 2025-04-07 12:31

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_alter_monitordetails_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='DesktopDisposed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disposal_date', models.DateField(default=django.utils.timezone.now)),
                ('disposal_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('is_full_disposal', models.BooleanField(default=True)),
                ('desktop_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.desktop_package')),
            ],
        ),
    ]
