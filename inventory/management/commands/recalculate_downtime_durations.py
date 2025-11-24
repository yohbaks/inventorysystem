"""
Management command to recalculate duration for all downtime events
"""

from django.core.management.base import BaseCommand
from inventory.models import EquipmentDowntimeEvent


class Command(BaseCommand):
    help = 'Recalculate duration for all downtime events with start and end times'

    def handle(self, *args, **options):
        # Get all downtime events with both start and end times
        events = EquipmentDowntimeEvent.objects.filter(
            start_time__isnull=False,
            end_time__isnull=False
        )

        total_events = events.count()
        self.stdout.write(f'Found {total_events} downtime events with start and end times')

        updated_count = 0
        for event in events:
            old_duration = event.duration_minutes
            event.calculate_duration()

            # Only save if duration changed
            if event.duration_minutes != old_duration:
                event.save()
                updated_count += 1
                self.stdout.write(
                    f'Updated event {event.id}: {event.equipment_name} - '
                    f'{old_duration} -> {event.duration_minutes} minutes'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully recalculated duration for {updated_count} events'
            )
        )
