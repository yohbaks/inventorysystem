#!/usr/bin/env python
"""Check SNMR reports"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventorysystem.settings')
django.setup()

from inventory.models import SNMRReport

reports = SNMRReport.objects.all().order_by('-year', '-month')
print(f"Total SNMR Reports: {reports.count()}")
print()

for report in reports[:10]:
    print(f"ID: {report.id}")
    print(f"Period: {report.month}/{report.year}")
    print(f"Office: {report.office}")
    print(f"Region: {report.region}")
    print("-" * 40)
