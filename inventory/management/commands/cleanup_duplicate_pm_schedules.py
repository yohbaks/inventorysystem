"""
Management command to clean up duplicate PM schedules
Usage: python manage.py cleanup_duplicate_pm_schedules
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from inventory.models import PMChecklistSchedule


class Command(BaseCommand):
    help = 'Remove duplicate PM schedules (keeps the first, removes others)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting cleanup of duplicate PM schedules...'))

        # Find schedules with duplicates (same template + scheduled_date)
        duplicates = PMChecklistSchedule.objects.values(
            'template', 'scheduled_date'
        ).annotate(
            count=Count('id')
        ).filter(count__gt=1)

        total_removed = 0

        for dup in duplicates:
            # Get all schedules for this template + date combination
            schedules = PMChecklistSchedule.objects.filter(
                template_id=dup['template'],
                scheduled_date=dup['scheduled_date']
            ).order_by('id')

            # Keep the first one, delete the rest
            first_schedule = schedules.first()
            duplicates_to_delete = schedules.exclude(id=first_schedule.id)

            count = duplicates_to_delete.count()
            if count > 0:
                self.stdout.write(
                    f"  Template {dup['template']}, Date {dup['scheduled_date']}: "
                    f"Keeping schedule {first_schedule.id}, removing {count} duplicates"
                )
                duplicates_to_delete.delete()
                total_removed += count

        if total_removed > 0:
            self.stdout.write(self.style.SUCCESS(
                f'Successfully removed {total_removed} duplicate schedules!'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('No duplicate schedules found. Database is clean!'))
