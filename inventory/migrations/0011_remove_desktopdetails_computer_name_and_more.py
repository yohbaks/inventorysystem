# Generated by Django 5.0.4 on 2024-10-08 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_desktop_package_asset_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='desktopdetails',
            name='computer_name',
        ),
        migrations.AddField(
            model_name='desktopdetails',
            name='drive',
            field=models.CharField(max_length=332, null=True),
        ),
        migrations.AddField(
            model_name='desktopdetails',
            name='memory',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='desktopdetails',
            name='processor',
            field=models.CharField(max_length=33, null=True),
        ),
        migrations.AlterField(
            model_name='desktopdetails',
            name='model',
            field=models.CharField(max_length=255, null=True),
        ),
    ]