# signals.py - FIXED VERSION

import qrcode
from io import BytesIO
from django.core.files import File
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse
from .models import (
    Equipment_Package, LaptopPackage, PrinterPackage,
    DesktopDetails, LaptopDetails, PrinterDetails,
    DisposedDesktopDetail, DisposedLaptop, DisposedPrinter,
    Employee, PreventiveMaintenance, PMScheduleAssignment,
    Notification, create_notification
)

# This signal will generate a QR code when a new Equipment_Package instance is created
@receiver(post_save, sender=Equipment_Package)
def generate_qr_code(sender, instance, created, **kwargs):
    if created and not instance.qr_code:
        # Build full URL for this desktop package
        url = reverse('desktop_details_view', kwargs={'package_id': instance.pk})
        full_url = f"http://127.0.0.1:8000{url}"  # Replace with your domain in production

        # Generate the QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Save QR code image into the model
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f'desktop_qr_{instance.pk}.png'

        instance.qr_code.save(filename, File(buffer), save=False)
        instance.save(update_fields=['qr_code'])  # Save only the qr_code field




# ============================ NOTIFICATION SIGNALS ===================

# ==================== PM MAINTENANCE SIGNALS ====================

@receiver(post_save, sender=PreventiveMaintenance)
def notify_pm_completed(sender, instance, created, **kwargs):
    """Notify when PM maintenance is completed"""
    if created and instance.is_completed:
        # Get all IT staff
        it_staff = User.objects.filter(is_staff=True)
        
        # Get device name
        device_name = "Unknown Device"
        link_url = "#"
        
        if instance.equipment_package:
            desktop = instance.equipment_package.desktop_details.first()
            device_name = desktop.computer_name if desktop else f"Desktop #{instance.equipment_package.id}"
            link_url = reverse('maintenance_history', args=[instance.equipment_package.id])
        elif instance.laptop_package:
            laptop = instance.laptop_package.laptop_details.first()
            device_name = laptop.computer_name if laptop else f"Laptop #{instance.laptop_package.id}"
            link_url = reverse('maintenance_history_laptop', args=[instance.laptop_package.id])
        
        # Create notification for all IT staff
        for staff in it_staff:
            create_notification(
                user=staff,
                notification_type='pm_completed',
                title='PM Maintenance Completed',
                message=f'Preventive maintenance for {device_name} has been successfully completed',
                priority='normal',
                link_url=link_url,
                link_text='View Report',
                related_object=instance
            )


@receiver(post_save, sender=PMScheduleAssignment)
def check_pm_schedule_status(sender, instance, created, **kwargs):
    """Check PM schedule and create notifications for overdue/due tasks"""
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    
    # Skip if already completed
    if instance.is_completed:
        return
    
    # Get device name
    device_name = "Unknown Device"
    link_url = "#"
    package_id = None
    
    if instance.equipment_package:
        desktop = instance.equipment_package.desktop_details.first()
        device_name = desktop.computer_name if desktop else f"Desktop #{instance.equipment_package.id}"
        link_url = reverse('maintenance_history', args=[instance.equipment_package.id])
        package_id = instance.equipment_package.id
    elif instance.laptop_package:
        laptop = instance.laptop_package.laptop_details.first()
        device_name = laptop.computer_name if laptop else f"Laptop #{instance.laptop_package.id}"
        link_url = reverse('maintenance_history_laptop', args=[instance.laptop_package.id])
        package_id = instance.laptop_package.id
    
    # Get all IT staff
    it_staff = User.objects.filter(is_staff=True)
    
    # Check if overdue
    if instance.pm_section_schedule.end_date < today:
        days_overdue = (today - instance.pm_section_schedule.end_date).days
        
        # Check if notification already exists (avoid duplicates)
        for staff in it_staff:
            existing = Notification.objects.filter(
                user=staff,
                notification_type='pm_overdue',
                object_id=instance.id,
                is_read=False
            ).exists()
            
            if not existing:
                create_notification(
                    user=staff,
                    notification_type='pm_overdue',
                    title='URGENT: PM Maintenance Overdue',
                    message=f'Preventive maintenance for {device_name} is {days_overdue} days overdue! Please complete immediately.',
                    priority='urgent',
                    link_url=link_url,
                    link_text='Fix Now',
                    related_object=instance
                )
    
    # Check if due soon (within 7 days)
    elif instance.pm_section_schedule.end_date <= today + timedelta(days=7):
        days_until_due = (instance.pm_section_schedule.end_date - today).days
        
        for staff in it_staff:
            existing = Notification.objects.filter(
                user=staff,
                notification_type='pm_due',
                object_id=instance.id,
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
                    related_object=instance
                )


# ==================== ASSET SIGNALS ====================

@receiver(post_save, sender=DesktopDetails)
def notify_desktop_added(sender, instance, created, **kwargs):
    """Notify when new desktop is added"""
    if created:
        it_staff = User.objects.filter(is_staff=True)
        
        for staff in it_staff:
            create_notification(
                user=staff,
                notification_type='asset_added',
                title='New Desktop Added',
                message=f'Desktop {instance.computer_name or "PC-" + str(instance.equipment_package.id)} has been added to inventory',
                priority='normal',
                # 🔧 FIX: Changed from 'equipment_package_detail' to 'desktop_details_view'
                link_url=reverse('desktop_details_view', kwargs={'package_id': instance.equipment_package.id}),
                link_text='View Asset',
                related_object=instance
            )


@receiver(post_save, sender=LaptopDetails)
def notify_laptop_added(sender, instance, created, **kwargs):
    """Notify when new laptop is added"""
    if created:
        it_staff = User.objects.filter(is_staff=True)
        
        for staff in it_staff:
            create_notification(
                user=staff,
                notification_type='asset_added',
                title='New Laptop Added',
                message=f'Laptop {instance.computer_name or "LT-" + str(instance.laptop_package.id)} has been added to inventory',
                priority='normal',
                # ✅ This one was already correct
                link_url=reverse('laptop_details_view', kwargs={'package_id': instance.laptop_package.id}),
                link_text='View Asset',
                related_object=instance
            )


@receiver(post_save, sender=PrinterDetails)
def notify_printer_added(sender, instance, created, **kwargs):
    """Notify when new printer is added"""
    if created:
        it_staff = User.objects.filter(is_staff=True)
        
        for staff in it_staff:
            create_notification(
                user=staff,
                notification_type='asset_added',
                title='New Printer Added',
                message=f'Printer {instance.printer_brand_db} {instance.printer_model_db} has been added to inventory',
                priority='normal',
                # 🔧 FIX: Added proper printer URL
                link_url=reverse('printer_details_view', kwargs={'printer_id': instance.id}),
                link_text='View Asset',
                related_object=instance
            )


# ==================== DISPOSAL SIGNALS ====================

@receiver(post_save, sender=DisposedDesktopDetail)
def notify_desktop_disposed(sender, instance, created, **kwargs):
    """Notify when desktop is disposed"""
    if created:
        it_staff = User.objects.filter(is_staff=True)
        
        for staff in it_staff:
            create_notification(
                user=staff,
                notification_type='asset_disposed',
                title='Desktop Moved to Disposal',
                message=f'Desktop {instance.desktop.computer_name if instance.desktop else "Unknown"} has been moved to disposal area',
                priority='normal',
                link_url=reverse('disposal_overview'),
                link_text='View Disposal Area',
                related_object=instance
            )


@receiver(post_save, sender=DisposedLaptop)
def notify_laptop_disposed(sender, instance, created, **kwargs):
    """Notify when laptop is disposed"""
    if created:
        it_staff = User.objects.filter(is_staff=True)
        
        for staff in it_staff:
            create_notification(
                user=staff,
                notification_type='asset_disposed',
                title='Laptop Moved to Disposal',
                message=f'Laptop {instance.laptop.computer_name if instance.laptop else "Unknown"} has been moved to disposal area',
                priority='normal',
                link_url=reverse('disposal_overview'),
                link_text='View Disposal Area',
                related_object=instance
            )


@receiver(post_save, sender=DisposedPrinter)
def notify_printer_disposed(sender, instance, created, **kwargs):
    """Notify when printer is disposed"""
    if created:
        it_staff = User.objects.filter(is_staff=True)
        
        for staff in it_staff:
            create_notification(
                user=staff,
                notification_type='asset_disposed',
                title='Printer Moved to Disposal',
                message=f'Printer {instance.printer_brand} {instance.printer_model} has been moved to disposal area',
                priority='normal',
                link_url=reverse('disposal_overview'),
                link_text='View Disposal Area',
                related_object=instance
            )


# ==================== EMPLOYEE SIGNALS ====================

@receiver(post_save, sender=Employee)
def notify_employee_added_or_updated(sender, instance, created, **kwargs):
    """Notify when employee is added or updated"""
    admins = User.objects.filter(is_staff=True, is_superuser=True)
    
    if created:
        # New employee added
        for admin in admins:
            create_notification(
                user=admin,
                notification_type='employee_added',
                title='New Employee Added',
                message=f'{instance.full_name} has been added to {instance.employee_office_section or "the system"}',
                priority='low',
                # 🔧 NOTE: You'll need to check if 'employee_detail' URL exists in your urls.py
                # If not, change this to '#' or the correct URL name
                link_url=reverse('employee_list'),  # Changed to employee_list since employee_detail might not exist
                link_text='View Employees',
                related_object=instance
            )
    else:
        # Employee updated
        for admin in admins:
            # Only create notification if significant fields changed
            # You can add more logic here if needed
            create_notification(
                user=admin,
                notification_type='employee_updated',
                title='Employee Information Updated',
                message=f'{instance.full_name} profile has been updated',
                priority='low',
                link_url=reverse('employee_list'),  # Changed to employee_list since employee_detail might not exist
                link_text='View Employees',
                related_object=instance
            )


# ==================== ASSET UPDATE DETECTION ====================

@receiver(pre_save, sender=DesktopDetails)
def track_desktop_changes(sender, instance, **kwargs):
    """Track changes to desktop details"""
    if instance.pk:  # Only for existing objects
        try:
            old_instance = DesktopDetails.objects.get(pk=instance.pk)
            # Store old values for comparison in post_save
            instance._old_values = {
                'computer_name': old_instance.computer_name,
                'processor': old_instance.processor,
                'memory': old_instance.memory,
            }
        except DesktopDetails.DoesNotExist:
            pass


@receiver(post_save, sender=DesktopDetails)
def notify_desktop_updated(sender, instance, created, **kwargs):
    """Notify when desktop is updated"""
    if not created and hasattr(instance, '_old_values'):
        # Check if significant fields changed
        changed = False
        changes = []
        
        if instance._old_values['computer_name'] != instance.computer_name:
            changed = True
            changes.append('computer name')
        if instance._old_values['processor'] != instance.processor:
            changed = True
            changes.append('processor')
        if instance._old_values['memory'] != instance.memory:
            changed = True
            changes.append('memory')
        
        if changed:
            it_staff = User.objects.filter(is_staff=True)
            changes_text = ', '.join(changes)
            
            for staff in it_staff:
                create_notification(
                    user=staff,
                    notification_type='asset_updated',
                    title='Desktop Information Updated',
                    message=f'Desktop {instance.computer_name} has been updated ({changes_text})',
                    priority='low',
                    # 🔧 FIX: Changed from 'equipment_package_detail' to 'desktop_details_view'
                    link_url=reverse('desktop_details_view', kwargs={'package_id': instance.equipment_package.id}),
                    link_text='View Changes',
                    related_object=instance
                )


# ==================== DISPOSAL APPROVAL SYSTEM ====================

def check_pending_disposals():
    """
    Call this function periodically (e.g., daily via cron or Celery)
    to notify about pending disposal approvals
    """
    from django.db.models import Count
    
    # Count pending disposals (you'll need to add approval_status field to your disposal models)
    desktop_count = DisposedDesktopDetail.objects.filter(is_approved=False).count()
    laptop_count = DisposedLaptop.objects.filter(is_approved=False).count()
    printer_count = DisposedPrinter.objects.filter(is_approved=False).count()
    
    total_count = desktop_count + laptop_count + printer_count
    
    if total_count > 0:
        # Notify approvers
        approvers = User.objects.filter(is_staff=True, is_superuser=True)
        
        for approver in approvers:
            # Check if notification already exists
            existing = Notification.objects.filter(
                user=approver,
                notification_type='disposal_pending',
                is_read=False
            ).exists()
            
            if not existing:
                create_notification(
                    user=approver,
                    notification_type='disposal_pending',
                    title='Disposal Approval Needed',
                    message=f'{total_count} items are waiting for disposal approval',
                    priority='high',
                    link_url=reverse('disposal_overview'),
                    link_text='Review Items'
                )

# ==========================NOTIFICATION SIGNALS END==========================


# ============================================================================
# 🔧 CHANGES MADE IN THIS FILE:
# ============================================================================
# Line 215: Changed 'equipment_package_detail' → 'desktop_details_view'
# Line 247: Added proper printer URL (was just '#')
# Line 289: Changed 'employee_detail' → 'employee_list' (verify this URL exists)
# Line 301: Changed 'employee_detail' → 'employee_list' (verify this URL exists)  
# Line 313: Changed 'equipment_package_detail' → 'desktop_details_view'
# ============================================================================