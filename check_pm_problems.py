#!/usr/bin/env python
"""Check if there are any problems logged in PM completions"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventorysystem.settings')
django.setup()

from inventory.models import PMChecklistItemCompletion
from django.db.models import Q

# Check for PM completions with problems
print("=" * 80)
print("PM COMPLETIONS WITH PROBLEMS ENCOUNTERED")
print("=" * 80)

problems = PMChecklistItemCompletion.objects.filter(
    Q(problems_encountered__isnull=False) & ~Q(problems_encountered='')
).order_by('-id')[:20]

print(f"Found {problems.count()} PM items with problems logged")
print()

for item in problems:
    print(f"ID: {item.id}")
    print(f"Item: {item.item.task_description if item.item else 'N/A'}")
    print(f"Problems: {item.problems_encountered[:200]}")
    if hasattr(item, 'downtime_events'):
        dt_count = item.downtime_events.count()
        print(f"Associated Downtime Events: {dt_count}")
        if dt_count > 0:
            for dt in item.downtime_events.all():
                print(f"  - {dt.equipment_name}: {dt.occurrence_date}")
    print("-" * 40)
