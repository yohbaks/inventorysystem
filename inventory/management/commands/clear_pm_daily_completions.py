"""
Management command to clear all PM daily checklist completions
Use this to reset and start fresh
"""

from django.core.management.base import BaseCommand
from inventory.models import PMChecklistCompletion, PMChecklistItemCompletion, PMChecklistSchedule


class Command(BaseCommand):
    help = 'Clear all PM daily checklist completions (resets all data for fresh start)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all completions',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL PM daily checklist completions and item completions.\n'
                    'Run with --confirm flag to proceed:\n'
                    'python manage.py clear_pm_daily_completions --confirm'
                )
            )
            return

        # Delete all item completions first (foreign key constraint)
        item_completions_count = PMChecklistItemCompletion.objects.all().count()
        PMChecklistItemCompletion.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {item_completions_count} item completions')
        )

        # Delete all completions
        completions_count = PMChecklistCompletion.objects.all().count()
        PMChecklistCompletion.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {completions_count} completions')
        )

        # Reset all schedules to PENDING status
        updated = PMChecklistSchedule.objects.all().update(status='PENDING')
        self.stdout.write(
            self.style.SUCCESS(f'Reset {updated} schedules to PENDING status')
        )

        self.stdout.write(
            self.style.SUCCESS('\nAll PM daily completions cleared! You can now start fresh.')
        )
