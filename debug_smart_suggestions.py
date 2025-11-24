#!/usr/bin/env python
"""Debug script to check smart suggestions for SNMR"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventorysystem.settings')
django.setup()

from datetime import date
from inventory.models import EquipmentDowntimeEvent, SNMRReport

# Check all downtime events
print("=" * 80)
print("ALL DOWNTIME EVENTS IN DATABASE")
print("=" * 80)
all_events = EquipmentDowntimeEvent.objects.all().order_by('-occurrence_date')
print(f"Total downtime events: {all_events.count()}")
print()

for event in all_events[:10]:  # Show first 10
    print(f"ID: {event.id}")
    print(f"Equipment: {event.equipment_name}")
    print(f"Date: {event.occurrence_date}")
    print(f"Time: {event.start_time} - {event.end_time or 'Ongoing'}")
    print(f"Severity: {event.severity}")
    print(f"Cause: {event.cause_description}")
    print(f"Duration: {event.duration_minutes} mins")
    print("-" * 40)

# Check latest SNMR report
print("\n" + "=" * 80)
print("LATEST SNMR REPORT")
print("=" * 80)
latest_report = SNMRReport.objects.order_by('-year', '-month').first()
if latest_report:
    print(f"Report ID: {latest_report.id}")
    print(f"Period: {latest_report.month}/{latest_report.year}")
    print(f"Office: {latest_report.office}")

    # Calculate month boundaries for this report
    month_start = date(latest_report.year, latest_report.month, 1)
    if latest_report.month == 12:
        month_end = date(latest_report.year + 1, 1, 1)
    else:
        month_end = date(latest_report.year, latest_report.month + 1, 1)

    print(f"Date range: {month_start} to {month_end}")

    # Check events in this period
    print("\n" + "=" * 80)
    print("DOWNTIME EVENTS IN REPORT PERIOD")
    print("=" * 80)
    events_in_period = EquipmentDowntimeEvent.objects.filter(
        occurrence_date__gte=month_start,
        occurrence_date__lt=month_end
    )
    print(f"Events in period: {events_in_period.count()}")
    print()

    for event in events_in_period:
        print(f"ID: {event.id}")
        print(f"Equipment: {event.equipment_name}")
        print(f"Date: {event.occurrence_date}")
        print(f"Severity: {event.severity}")
        print(f"Cause: {event.cause_description}")
        print("-" * 40)

    # Test keyword matching
    print("\n" + "=" * 80)
    print("KEYWORD MATCHING TEST")
    print("=" * 80)
    category_keywords = {
        'Wide Area Network': ['wan', 'wide area', 'network', 'internet', 'connectivity', 'router', 'switch'],
        'PABX': ['pabx', 'pbx', 'phone', 'telephone', 'voip', 'extension'],
        'Admin Server': ['server', 'admin', 'mail', 'database', 'storage'],
        'Trunkline': ['trunkline', 'trunk', 'line', 'connection']
    }

    for category_name, keywords in category_keywords.items():
        print(f"\n{category_name}:")
        print(f"Keywords: {', '.join(keywords)}")
        category_events = []
        for event in events_in_period:
            equipment_lower = event.equipment_name.lower()
            matched_keywords = [kw for kw in keywords if kw in equipment_lower]
            if matched_keywords:
                category_events.append(event)
                print(f"  ✓ MATCH: {event.equipment_name} (matched: {', '.join(matched_keywords)})")

        if not category_events:
            print(f"  ✗ No matches found")
        else:
            print(f"  Total matches: {len(category_events)}")

    # Test the actual function
    print("\n" + "=" * 80)
    print("TESTING generate_snmr_suggestions() FUNCTION")
    print("=" * 80)
    from inventory.views import generate_snmr_suggestions
    suggestions = generate_snmr_suggestions(latest_report)

    for category, suggestion in suggestions.items():
        print(f"\n{category}:")
        print(f"  Has Data: {suggestion.get('has_data', False)}")
        print(f"  Total Events: {suggestion.get('total_events', 0)}")
        if suggestion.get('has_data'):
            print(f"  Status: {suggestion.get('status')}")
            print(f"  Reason: {suggestion.get('reason')}")
            print(f"  Equipment: {suggestion.get('equipment_affected', [])}")
else:
    print("No SNMR reports found in database")

print("\n" + "=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)
