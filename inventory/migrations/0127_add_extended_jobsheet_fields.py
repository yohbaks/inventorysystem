# Generated manually for extended job sheet fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0126_alter_hdrentry_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='hdrentry',
            name='section_division',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='contact_no',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='hardware_type',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='hardware_brand_model',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='hardware_serial_number',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='computer_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='application_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='application_version',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='connectivity_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='user_account_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='assessment',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='mode_of_filing',
            field=models.CharField(blank=True, choices=[('Walk-in', 'Walk-in'), ('Telephone Call', 'Telephone Call'), ('Email', 'Email')], max_length=50),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='fulfilled_by',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='reviewed_by',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='concern_addressed',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='satisfaction_service',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='satisfaction_solution',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='hdrentry',
            name='client_comments',
            field=models.TextField(blank=True),
        ),
    ]
