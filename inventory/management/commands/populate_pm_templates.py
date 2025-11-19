"""
Management command to populate PM Checklist Templates and Items
Usage: python manage.py populate_pm_templates
"""

from django.core.management.base import BaseCommand
from inventory.models import PMChecklistTemplate, PMChecklistItem


class Command(BaseCommand):
    help = 'Populate PM Checklist Templates and Items with default data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting PM template population...'))

        # Clear existing templates (optional - comment out if you want to keep existing data)
        # PMChecklistTemplate.objects.all().delete()
        # self.stdout.write(self.style.WARNING('Cleared existing templates'))

        # Create Annex A Template
        self.create_annex_a()

        # Create Annex B Template
        self.create_annex_b()

        # Create Annex C Template
        self.create_annex_c()

        # Create Annex F Template
        self.create_annex_f()

        self.stdout.write(self.style.SUCCESS('Successfully populated PM templates!'))

    def create_annex_a(self):
        """Create Annex A - Datacenter (Daily/Weekly) template"""
        template, created = PMChecklistTemplate.objects.get_or_create(
            annex_code='A',
            defaults={
                'title': 'Preventive Maintenance Checklist/Activities for the Datacenter (Daily/Weekly)',
                'frequency': 'DAILY',
                'description': 'Daily preventive maintenance checks for datacenter (Mon-Fri). Complete each day, weekly report aggregates all 5 days.',
                'schedule_note': 'Mondays - Fridays',
                'is_active': True
            }
        )

        # Update title if template already exists
        if not created:
            template.title = 'Preventive Maintenance Checklist/Activities for the Datacenter (Daily/Weekly)'
            template.schedule_note = 'Mondays - Fridays'
            template.frequency = 'DAILY'
            template.description = 'Daily preventive maintenance checks for datacenter (Mon-Fri). Complete each day, weekly report aggregates all 5 days.'
            template.save()
            # Clear existing items to recreate them
            template.items.all().delete()
            self.stdout.write(self.style.WARNING('Updating Annex A template and items'))
        else:
            self.stdout.write(self.style.SUCCESS('Created Annex A template'))

        # Add items for Annex A - properly numbered 1-11 without gaps
        items = [
            {
                'item_number': 1,
                'task_description': 'Check if WAN connectivity is up',
                'has_schedule_times': False,
                'requires_value_input': False
            },
            {
                'item_number': 2,
                'task_description': 'Check if the telephone system is up and running\nCheck if all servers are up and running',
                'has_schedule_times': False,
                'requires_value_input': False
            },
            {
                'item_number': 3,
                'task_description': "Check if servers' utilization (processor, memory and storage) is below 80%",
                'has_schedule_times': True,
                'schedule_times': ['9 AM', '2 PM'],
                'requires_value_input': False
            },
            {
                'item_number': 4,
                'task_description': 'Check if the temperature level in the network room is between 20°C to 27°C (68°F to 80.6°F)',
                'has_schedule_times': True,
                'schedule_times': ['8 AM', '10 AM', '12 PM', '2 PM', '4 PM'],
                'requires_value_input': False
            },
            {
                'item_number': 5,
                'task_description': 'Check if the humidity level in the network room is between 30% to 60%',
                'has_schedule_times': True,
                'schedule_times': ['8 AM', '10 AM', '12 PM', '2 PM', '4 PM'],
                'requires_value_input': False
            },
            {
                'item_number': 6,
                'task_description': "Check if servers' anti-virus definition files are up-to-date",
                'has_schedule_times': False,
                'requires_value_input': False
            },
            {
                'item_number': 7,
                'task_description': "Check if server's event logs for critical warnings or errors",
                'has_schedule_times': False,
                'requires_value_input': False
            },
            {
                'item_number': 8,
                'task_description': 'Check for signs of water leaks',
                'has_schedule_times': False,
                'requires_value_input': False
            },
            {
                'item_number': 9,
                'task_description': 'Check for signs of holes on the ceiling and walls',
                'has_schedule_times': False,
                'requires_value_input': False
            },
            {
                'item_number': 10,
                'task_description': 'Check for signs of pest infestation',
                'has_schedule_times': False,
                'requires_value_input': False
            },
            {
                'item_number': 11,
                'task_description': 'Remove any fire hazards.',
                'has_schedule_times': False,
                'requires_value_input': False
            },
        ]

        for item_data in items:
            PMChecklistItem.objects.create(
                template=template,
                **item_data,
                order=item_data['item_number']
            )

        self.stdout.write(f'  Added {len(items)} items to Annex A')
        self.stdout.write(self.style.SUCCESS('  Items 1-6, 12: Daily tasks (M-F)'))
        self.stdout.write(self.style.SUCCESS('  Items 7-11: Weekly tasks (once per week, dark gray shading)'))

    def create_annex_b(self):
        """Create Annex B - Datacenter (Monthly) template"""
        template, created = PMChecklistTemplate.objects.get_or_create(
            annex_code='B',
            defaults={
                'title': 'Annex B - Datacenter Monthly Preventive Maintenance',
                'frequency': 'MONTHLY',
                'description': 'Monthly preventive maintenance tasks for datacenter infrastructure',
                'schedule_note': 'First week of each month',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Created Annex B template'))

            items = [
                {
                    'item_number': 1,
                    'task_description': 'Clean and vacuum server room floors and under raised floors',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 2,
                    'task_description': 'Clean air conditioning filters and coils',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 3,
                    'task_description': 'Inspect and clean UPS battery terminals',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 4,
                    'task_description': 'Test emergency power shutdown procedures',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 5,
                    'task_description': 'Check and tighten all cable connections',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 6,
                    'task_description': 'Inspect server rack mounting hardware',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 7,
                    'task_description': 'Test fire alarm and suppression system',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 8,
                    'task_description': 'Review and update equipment inventory',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 9,
                    'task_description': 'Backup critical system configurations',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 10,
                    'task_description': 'Inspect and clean equipment fans and vents',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
            ]

            for item_data in items:
                PMChecklistItem.objects.create(
                    template=template,
                    **item_data,
                    order=item_data['item_number']
                )

            self.stdout.write(f'  Added {len(items)} items to Annex B')
        else:
            self.stdout.write(self.style.WARNING('Annex B template already exists'))

    def create_annex_c(self):
        """Create Annex C - Floor/Building Distributors (Weekly) template"""
        template, created = PMChecklistTemplate.objects.get_or_create(
            annex_code='C',
            defaults={
                'title': 'Annex C - Floor/Building Distributors Weekly Preventive Maintenance',
                'frequency': 'WEEKLY',
                'description': 'Weekly preventive maintenance for network distribution equipment on floors/buildings',
                'schedule_note': 'Check each week of the month',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Created Annex C template'))

            items = [
                {
                    'item_number': 1,
                    'task_description': 'Inspect network switch status lights and connections',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 2,
                    'task_description': 'Check patch panel cable organization',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 3,
                    'task_description': 'Verify WiFi access point functionality',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 4,
                    'task_description': 'Clean distribution frame and equipment',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 5,
                    'task_description': 'Check for unauthorized network connections',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 6,
                    'task_description': 'Inspect distribution cabinet locks and security',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 7,
                    'task_description': 'Test backup power for distribution equipment',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 8,
                    'task_description': 'Document any physical damage or wear',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
            ]

            for item_data in items:
                PMChecklistItem.objects.create(
                    template=template,
                    **item_data,
                    order=item_data['item_number']
                )

            self.stdout.write(f'  Added {len(items)} items to Annex C')
        else:
            self.stdout.write(self.style.WARNING('Annex C template already exists'))

    def create_annex_f(self):
        """Create Annex F - Datacenter (Semi-Annual) template"""
        template, created = PMChecklistTemplate.objects.get_or_create(
            annex_code='F',
            defaults={
                'title': 'Annex F - Datacenter Semi-Annual Preventive Maintenance',
                'frequency': 'SEMI_ANNUAL',
                'description': 'Semi-annual comprehensive preventive maintenance for datacenter',
                'schedule_note': 'Every 6 months (January and July)',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Created Annex F template'))

            items = [
                {
                    'item_number': 1,
                    'task_description': 'Deep clean entire datacenter facility',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 2,
                    'task_description': 'Comprehensive UPS battery testing and replacement as needed',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 3,
                    'task_description': 'Full HVAC system inspection and maintenance',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 4,
                    'task_description': 'Fire suppression system comprehensive testing',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 5,
                    'task_description': 'Electrical panel inspection and thermal imaging',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 6,
                    'task_description': 'Complete cable infrastructure audit',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 7,
                    'task_description': 'Server hardware inspection and firmware updates',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 8,
                    'task_description': 'Review and update disaster recovery procedures',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 9,
                    'task_description': 'Physical security system testing (cameras, access control)',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 10,
                    'task_description': 'Environmental monitoring system calibration',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 11,
                    'task_description': 'Generator load testing and maintenance',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
                {
                    'item_number': 12,
                    'task_description': 'Complete documentation review and updates',
                    'has_schedule_times': False,
                    'requires_value_input': False
                },
            ]

            for item_data in items:
                PMChecklistItem.objects.create(
                    template=template,
                    **item_data,
                    order=item_data['item_number']
                )

            self.stdout.write(f'  Added {len(items)} items to Annex F')
        else:
            self.stdout.write(self.style.WARNING('Annex F template already exists'))
