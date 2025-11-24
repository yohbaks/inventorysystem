#!/usr/bin/env python
"""
Migrate downtime information from problems_encountered field to EquipmentDowntimeEvent records
"""
import os
import django
import re
from datetime import datetime, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventorysystem.settings')
django.setup()

from inventory.models import PMChecklistItemCompletion, EquipmentDowntimeEvent
from django.db.models import Q

def parse_downtime_from_problems(problems_text, item_completion):
    """
    Parse problems_encountered text to extract downtime information
    Returns list of downtime event dictionaries
    """
    events = []

    # Patterns to match downtime descriptions
    # Pattern 1: "Nov 03: Network Down due to..."
    # Pattern 2: "Nov 03 (Mon): Network and IP phone Down..."

    # Look for date patterns and "down" keywords
    downtime_indicators = ['down', 'downtime', 'offline', 'outage', 'not working', 'failed']

    lines = problems_text.split('\n')
    current_year = date.today().year

    for line in lines:
        line = line.strip()
        if not line or line.lower() in ['none', 'no problems', 'good condition', 'n/a']:
            continue

        # Check if line indicates downtime
        line_lower = line.lower()
        if not any(indicator in line_lower for indicator in downtime_indicators):
            continue

        # Try to extract date
        # Pattern: "Nov 03" or "Nov 03 (Mon)"
        date_match = re.search(r'([A-Z][a-z]{2})\s+(\d{1,2})', line)
        occurrence_date = None

        if date_match:
            month_str = date_match.group(1)
            day = int(date_match.group(2))

            # Convert month abbreviation to number
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            month = month_map.get(month_str)

            if month:
                try:
                    occurrence_date = date(current_year, month, day)
                except ValueError:
                    # Try previous year
                    try:
                        occurrence_date = date(current_year - 1, month, day)
                    except ValueError:
                        pass

        # If no date found, skip this line
        if not occurrence_date:
            continue

        # Extract equipment name and cause
        # Look for what's mentioned as down
        equipment_keywords = {
            'network': 'Wide Area Network',
            'wan': 'Wide Area Network',
            'internet': 'Wide Area Network',
            'ip phone': 'PABX System',
            'phone': 'PABX System',
            'telephone': 'PABX System',
            'pabx': 'PABX System',
            'server': 'Admin Server',
        }

        equipment_name = 'Network Equipment'  # Default
        for keyword, equip in equipment_keywords.items():
            if keyword in line_lower:
                equipment_name = equip
                break

        # Extract cause description (everything after the date part)
        cause_description = line
        if date_match:
            cause_description = line[date_match.end():].strip()
            if cause_description.startswith(':'):
                cause_description = cause_description[1:].strip()

        # Determine severity
        severity = 'MODERATE'  # Default
        if 'critical' in line_lower or 'complete' in line_lower:
            severity = 'CRITICAL'
        elif 'major' in line_lower or 'significant' in line_lower:
            severity = 'MAJOR'
        elif 'minor' in line_lower:
            severity = 'MINOR'

        events.append({
            'occurrence_date': occurrence_date,
            'equipment_name': equipment_name,
            'cause_description': cause_description,
            'severity': severity,
        })

    return events


def migrate_downtime_data(dry_run=True):
    """
    Migrate downtime information from problems_encountered to EquipmentDowntimeEvent
    """
    print("=" * 80)
    print("DOWNTIME DATA MIGRATION UTILITY")
    print("=" * 80)
    print(f"Mode: {'DRY RUN (no changes will be saved)' if dry_run else 'LIVE (will create records)'}")
    print()

    # Find PM completions with problems that mention downtime
    downtime_keywords = ['down', 'downtime', 'offline', 'outage', 'not working', 'failed']

    query = Q()
    for keyword in downtime_keywords:
        query |= Q(problems_encountered__icontains=keyword)

    items_with_downtime = PMChecklistItemCompletion.objects.filter(query).order_by('-id')

    print(f"Found {items_with_downtime.count()} PM completion items mentioning downtime")
    print()

    total_events_to_create = 0
    created_events = []

    for item in items_with_downtime:
        print(f"\nProcessing Item ID {item.id}:")
        print(f"  Task: {item.item.task_description if item.item else 'N/A'}")
        print(f"  Problems: {item.problems_encountered[:100]}...")

        # Parse events from problems text
        events = parse_downtime_from_problems(item.problems_encountered, item)

        if events:
            print(f"  → Found {len(events)} downtime event(s) to create:")
            for event_data in events:
                print(f"    - {event_data['occurrence_date']}: {event_data['equipment_name']}")
                print(f"      Severity: {event_data['severity']}")
                print(f"      Cause: {event_data['cause_description'][:80]}...")

                if not dry_run:
                    # Create the downtime event
                    downtime_event = EquipmentDowntimeEvent.objects.create(
                        item_completion=item,
                        occurrence_date=event_data['occurrence_date'],
                        start_time=datetime.strptime('08:00', '%H:%M').time(),  # Default start time
                        end_time=None,  # Unknown end time
                        equipment_name=event_data['equipment_name'],
                        severity=event_data['severity'],
                        cause_description=event_data['cause_description'],
                        resolution_notes='Migrated from problems_encountered field',
                        services_affected='',
                        reported_by=item.completion.completed_by if hasattr(item, 'completion') and item.completion else None
                    )
                    created_events.append(downtime_event)
                    print(f"      ✓ Created EquipmentDowntimeEvent ID {downtime_event.id}")
                else:
                    print(f"      [DRY RUN] Would create EquipmentDowntimeEvent")

                total_events_to_create += 1
        else:
            print(f"  → No parseable downtime events found")

    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print(f"Total events identified: {total_events_to_create}")
    if not dry_run:
        print(f"Successfully created: {len(created_events)} downtime event records")
    else:
        print(f"Would create: {total_events_to_create} downtime event records")
        print("\nRun with dry_run=False to actually create the records")
    print("=" * 80)

    return created_events if not dry_run else []


if __name__ == '__main__':
    import sys

    # Check if --live flag is passed
    dry_run = '--live' not in sys.argv

    if not dry_run:
        confirm = input("\n⚠️  WARNING: This will create downtime event records in the database.\nType 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)

    migrate_downtime_data(dry_run=dry_run)
