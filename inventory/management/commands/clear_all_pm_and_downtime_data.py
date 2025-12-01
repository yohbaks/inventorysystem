"""
Management command to clear all PM checklist and downtime data
Use this to reset and start fresh with both PM checklists and downtime events
"""

from django.core.management.base import BaseCommand
from inventory.models import (
    PMChecklistCompletion,
    PMChecklistItemCompletion,
    PMChecklistReport,
    PMIssueLog,
    EquipmentDowntimeEvent,
    PMChecklistSchedule
)


class Command(BaseCommand):
    help = 'Clear all PM checklist and downtime data (completions, reports, issue logs, and downtime events)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all PM and downtime data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL:\n'
                    '  - PM checklist completions and item completions\n'
                    '  - PM checklist reports\n'
                    '  - PM issue logs\n'
                    '  - Equipment downtime events\n\n'
                    'Run with --confirm flag to proceed:\n'
                    'python manage.py clear_all_pm_and_downtime_data --confirm'
                )
            )
            return

        # Delete all item completions first (foreign key constraint)
        item_completions_count = PMChecklistItemCompletion.objects.all().count()
        PMChecklistItemCompletion.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {item_completions_count} PM checklist item completions')
        )

        # Delete all completions
        completions_count = PMChecklistCompletion.objects.all().count()
        PMChecklistCompletion.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {completions_count} PM checklist completions')
        )

        # Delete all PM reports
        reports_count = PMChecklistReport.objects.all().count()
        PMChecklistReport.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {reports_count} PM checklist reports')
        )

        # Delete all PM issue logs
        issues_count = PMIssueLog.objects.all().count()
        PMIssueLog.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {issues_count} PM issue logs')
        )

        # Delete all equipment downtime events
        downtime_count = EquipmentDowntimeEvent.objects.all().count()
        EquipmentDowntimeEvent.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {downtime_count} equipment downtime events')
        )

        # Reset all schedules to PENDING status
        updated = PMChecklistSchedule.objects.all().update(status='PENDING')
        self.stdout.write(
            self.style.SUCCESS(f'Reset {updated} PM schedules to PENDING status')
        )

        self.stdout.write(
            self.style.SUCCESS('\n✓ All PM checklist and downtime data cleared successfully!')
        )
