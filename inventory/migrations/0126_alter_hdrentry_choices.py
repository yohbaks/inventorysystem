# Generated manually for job sheet form updates

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0125_hdrreport_hdrentry'),
    ]

    operations = [
        # No database operations needed - choices are Python-level only
        # This migration documents the change to HDREntry field choices:
        # - TYPE_CHOICES: Updated to 'Service Request' and 'Failure'
        # - CATEGORY_CHOICES: Updated to 'Business Apps', 'Hardware', 'Software', 'Services'
        # - STATUS_CHOICES: Updated to 'fixed', 'For Repair', 'For disposal'
    ]
