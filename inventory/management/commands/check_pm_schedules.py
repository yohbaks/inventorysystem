# ==================== MANAGEMENT COMMAND ====================
# Create this file: inventory/management/commands/check_pm_schedules.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from inventory.models import PMScheduleAssignment, Notification, create_notification
from django.urls import reverse


class Command(BaseCommand):
    help = 'Check PM schedules and create notifications for overdue/due tasks'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Get all pending PM assignments (excluding disposed equipment/laptops)
        pending_assignments = PMScheduleAssignment.objects.filter(
            is_completed=False
        ).select_related(
            'equipment_package',
            'laptop_package',
            'pm_section_schedule',
            'pm_section_schedule__section'
        ).exclude(
            # Exclude disposed desktops
            equipment_package__is_disposed=True
        ).exclude(
            # Exclude disposed laptops
            laptop_package__is_disposed=True
        )
        
        overdue_count = 0
        due_soon_count = 0
        
        # Get all IT staff
        it_staff = User.objects.filter(is_staff=True)
        
        for assignment in pending_assignments:
            end_date = assignment.pm_section_schedule.end_date
            
            # Get device name
            device_name = "Unknown Device"
            link_url = "#"
            
            if assignment.equipment_package:
                desktop = assignment.equipment_package.desktop_details.first()
                device_name = desktop.computer_name if desktop else f"Desktop #{assignment.equipment_package.id}"
                link_url = reverse('maintenance_history', args=[assignment.equipment_package.id])
            elif assignment.laptop_package:
                laptop = assignment.laptop_package.laptop_details.first()
                device_name = laptop.computer_name if laptop else f"Laptop #{assignment.laptop_package.id}"
                link_url = reverse('maintenance_history_laptop', args=[assignment.laptop_package.id])
            
            # Check if overdue
            if end_date < today:
                days_overdue = (today - end_date).days
                
                for staff in it_staff:
                    # Check if notification already exists
                    existing = Notification.objects.filter(
                        user=staff,
                        notification_type='pm_overdue',
                        object_id=assignment.id,
                        is_read=False
                    ).exists()
                    
                    if not existing:
                        create_notification(
                            user=staff,
                            notification_type='pm_overdue',
                            title='URGENT: PM Maintenance Overdue',
                            message=f'Preventive maintenance for {device_name} is {days_overdue} days overdue!',
                            priority='urgent',
                            link_url=link_url,
                            link_text='Fix Now',
                            related_object=assignment
                        )
                        overdue_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'Created OVERDUE notification for {device_name}')
                        )
            
            # Check if due within 7 days
            elif end_date <= today + timedelta(days=7):
                days_until_due = (end_date - today).days
                
                for staff in it_staff:
                    # Check if notification already exists
                    existing = Notification.objects.filter(
                        user=staff,
                        notification_type='pm_due',
                        object_id=assignment.id,
                        is_read=False
                    ).exists()
                    
                    if not existing:
                        create_notification(
                            user=staff,
                            notification_type='pm_due',
                            title='PM Maintenance Due Soon',
                            message=f'Preventive maintenance for {device_name} is due in {days_until_due} days',
                            priority='high',
                            link_url=link_url,
                            link_text='View Details',
                            related_object=assignment
                        )
                        due_soon_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Created DUE notification for {device_name}')
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {overdue_count} overdue and {due_soon_count} due notifications'
            )
        )