from django.db import models
from django.utils.text import slugify
from django.utils import timezone 
from django.contrib.auth.models import User     # Import the User model if you have a custom user model, otherwise use the default Django User model  
from django.utils.timezone import now
import qrcode
from django.core.files import File # Import File to save the QR code image
from django.urls import reverse # Import reverse to generate URLs for the QR code image
from io import BytesIO  # Import BytesIO to handle the image in memory
from django.dispatch import receiver    
from django.db.models.signals import post_save
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.

def normalize_sn(value: str | None) -> str | None:
    v = (value or "").strip()
    return v.upper() if v else None

# ✅ put this once at the top of models.py


def generate_qr_for_laptop(instance):
    """Generate a QR code for LaptopPackage and attach it to the model."""
    try:
        qr_url = f"{settings.SITE_URL}{reverse('laptop_details_view', args=[instance.id])}"
        qr = qrcode.make(qr_url)
        qr_io = BytesIO()
        qr.save(qr_io, format='PNG')
        qr_filename = f"laptop_qr_{instance.id}.png"
        instance.qr_code.save(qr_filename, File(qr_io), save=False)
    except Exception as e:
        print("❌ QR generation failed:", e)


#################
class Equipment_Package(models.Model):
    is_disposed = models.BooleanField(default=False)
    disposal_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True, null=True)

    pm_schedule_date = models.DateField(null=True, blank=True)
    pm_schedule_notes = models.TextField(null=True, blank=True)

    # Helper to get the first linked DesktopDetails's computer name
    @property
    def computer_name(self):
        desktop = self.desktop_details.first()
        return desktop.computer_name if desktop else "N/A"

    # Helper to get this package's ID
    @property
    def package_number(self):
        return self.id

    def __str__(self):
        return f"Desktop Package {self.pk}"

  

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_keyboard = models.BooleanField(default=False)
    is_mouse = models.BooleanField(default=False)
    is_monitor = models.BooleanField(default=False)
    is_ups = models.BooleanField(default=False)
    is_desktop = models.BooleanField(default=False)
    is_printer = models.BooleanField(default=False)
    is_laptop = models.BooleanField(default=False)

    def __str__(self):
        return self.name




class DesktopDetails(models.Model):
    equipment_package = models.ForeignKey(
        Equipment_Package, related_name='desktop_details', on_delete=models.CASCADE
    )

    serial_no = models.CharField(max_length=255)
    serial_no_norm = models.CharField(
        max_length=255, null=True, blank=True,
        db_index=True, editable=False, unique=True
    )

    def save(self, *args, **kwargs):
        self.serial_no_norm = normalize_sn(self.serial_no)
        super().save(*args, **kwargs)

    computer_name = models.CharField(max_length=255, unique=True, null=True)
    brand_name = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    model = models.CharField(max_length=255, null=True)
    processor = models.CharField(max_length=33, null=True)
    memory = models.CharField(max_length=100, null=True)
    drive = models.CharField(max_length=332, null=True)

    desktop_Graphics = models.CharField(max_length=100, blank=True, null=True)
    desktop_Graphics_Size = models.CharField(max_length=100, blank=True, null=True)

    desktop_OS = models.CharField(max_length=100, blank=True, null=True)
    desktop_Office = models.CharField(max_length=100, blank=True, null=True)
    desktop_OS_keys = models.CharField(max_length=100, blank=True, null=True)
    desktop_Office_keys = models.CharField(max_length=100, blank=True, null=True)

    is_disposed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.equipment_package} : {self.computer_name} | BRAND: {self.brand_name}"


class MonitorDetails(models.Model):
    equipment_package = models.ForeignKey(Equipment_Package, related_name='monitors', on_delete=models.CASCADE)
    monitor_sn_db = models.CharField(max_length=255)
    monitor_sn_norm = models.CharField(
        max_length=255, null=True, blank=True,
        db_index=True, editable=False, unique=True
    )

    def save(self, *args, **kwargs):
        self.monitor_sn_norm = normalize_sn(self.monitor_sn_db)
        super().save(*args, **kwargs)

    monitor_brand_db = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    monitor_model_db = models.CharField(max_length=255)
    monitor_size_db = models.CharField(max_length=255, null=True)
    monitor_photo = models.ImageField(upload_to="monitor_photos/", null=True, blank=True)
    is_disposed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.equipment_package} | BRAND: {self.monitor_brand_db}"


class KeyboardDetails(models.Model):
    equipment_package = models.ForeignKey(Equipment_Package, related_name='keyboards', on_delete=models.CASCADE)
    keyboard_sn_db = models.CharField(max_length=255)
    keyboard_sn_norm = models.CharField(
        max_length=255, null=True, blank=True,
        db_index=True, editable=False, unique=True
    )

    def save(self, *args, **kwargs):
        self.keyboard_sn_norm = normalize_sn(self.keyboard_sn_db)
        super().save(*args, **kwargs)

    keyboard_brand_db = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    keyboard_model_db = models.CharField(max_length=255)
    is_disposed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.equipment_package} : - {self.keyboard_brand_db} {self.keyboard_model_db} ({self.keyboard_sn_db})"


class MouseDetails(models.Model):
    equipment_package = models.ForeignKey(Equipment_Package, related_name='mouse_db', on_delete=models.CASCADE)
    mouse_sn_db = models.CharField(max_length=255, null=True)
    mouse_sn_norm = models.CharField(
        max_length=255, null=True, blank=True,
        db_index=True, editable=False, unique=True
    )

    def save(self, *args, **kwargs):
        self.mouse_sn_norm = normalize_sn(self.mouse_sn_db)
        super().save(*args, **kwargs)

    mouse_brand_db = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    mouse_model_db = models.CharField(max_length=255, null=True)
    is_disposed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.equipment_package} {self.mouse_brand_db} {self.mouse_model_db} ({self.mouse_sn_db})"


class UPSDetails(models.Model):
    equipment_package = models.ForeignKey(Equipment_Package, related_name='ups', on_delete=models.CASCADE)
    ups_sn_db = models.CharField(max_length=255)
    ups_sn_norm = models.CharField(
        max_length=255, null=True, blank=True,
        db_index=True, editable=False, unique=True
    )

    def save(self, *args, **kwargs):
        self.ups_sn_norm = normalize_sn(self.ups_sn_db)
        super().save(*args, **kwargs)

    ups_brand_db = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    ups_model_db = models.CharField(max_length=255)
    ups_capacity_db = models.CharField(max_length=255, null=True)
    is_disposed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.equipment_package} {self.ups_brand_db} {self.ups_model_db} ({self.ups_sn_db})"

class UserDetails(models.Model):
    # 💻 Desktop equipment
    equipment_package = models.ForeignKey(
        Equipment_Package, on_delete=models.CASCADE,
        null=True, blank=True, related_name='user_details'
    )

    # 💼 Laptop package
    laptop_package = models.ForeignKey(
        'LaptopPackage', on_delete=models.CASCADE,
        null=True, blank=True, related_name='user_details'
    )

    # 🖨 Printer package (NEW)
    printer_package = models.ForeignKey(
        'PrinterPackage', on_delete=models.CASCADE,
        null=True, blank=True, related_name='user_details'
    )

    # 👥 Assigned people
    user_Enduser = models.ForeignKey(
        'Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='enduser_details'
    )   
    user_Assetowner = models.ForeignKey(
        'Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assetowner_details'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = None
        if self.equipment_package:
            target = f"Desktop {self.equipment_package.id}"
        elif self.laptop_package:
            target = f"Laptop {self.laptop_package.id}"
        elif self.printer_package:
            target = f"Printer {self.printer_package.id}"
        else:
            target = "Unassigned"
        return f"{target} | Enduser: {self.user_Enduser or 'N/A'} | Owner: {self.user_Assetowner or 'N/A'}"


# =====================================
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++END OF DESKTOP,KEYBOARD,MOUSE,UPS DETAILS++++++++++++++++++++++++++++++++++++++
# ======================================

# ======================================
# +++++++++++++++++++++++++++++++++++++DISPOSED DETAILS DESKTOP, KEYBOARD, MOUSE, UPS++++++++++++
# ======================================

class DisposedDesktopDetail(models.Model):
    desktop = models.ForeignKey("DesktopDetails", on_delete=models.CASCADE)
    # equipment_package = models.CharField(max_length=255, blank=True, null=True)
    serial_no = models.CharField(max_length=255, blank=True, null=True)
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    asset_owner = models.CharField(max_length=255, blank=True, null=True)
    reason = models.TextField()
    date_disposed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" Disposed Desktop Package : -  {self.desktop}"

  
class DisposedMonitor(models.Model):
    monitor_disposed_db = models.ForeignKey("MonitorDetails", on_delete=models.CASCADE)
    equipment_package = models.ForeignKey(Equipment_Package, related_name='monitors_details', on_delete=models.CASCADE, null=True)
    disposed_under = models.ForeignKey(DisposedDesktopDetail, on_delete=models.CASCADE, related_name="disposed_monitors", null=True, blank=True)
    monitor_sn = models.CharField(max_length=255, blank=True, null=True)
    monitor_brand = models.CharField(max_length=255, blank=True, null=True)
    monitor_model = models.CharField(max_length=255, blank=True, null=True)
    monitor_size = models.CharField(max_length=255, blank=True, null=True)
    disposal_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    reason = models.TextField(blank=True, null=True)

    disposed_photo = models.ImageField(upload_to="disposed_monitor_photos/", null=True, blank=True)  # 👈 add this

    def __str__(self):
        return f"Disposed Monitor : - {self.monitor_disposed_db} "
    


class DisposedKeyboard(models.Model):
    keyboard_dispose_db = models.ForeignKey(KeyboardDetails, on_delete=models.CASCADE)
    equipment_package = models.ForeignKey(Equipment_Package, related_name='keyboards_details', on_delete=models.CASCADE, null=True)
    disposed_under = models.ForeignKey(DisposedDesktopDetail, on_delete=models.CASCADE, related_name="disposed_keyboards", null=True, blank=True)
    disposal_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Disposed: - {self.equipment_package} - {self.keyboard_dispose_db.keyboard_sn_db}"



class DisposedMouse(models.Model):
    mouse_db = models.ForeignKey(MouseDetails, on_delete=models.CASCADE)
    equipment_package = models.ForeignKey(Equipment_Package, related_name='mouse_details', on_delete=models.CASCADE, null=True)
    disposed_under = models.ForeignKey(DisposedDesktopDetail, on_delete=models.CASCADE, related_name="disposed_mice", null=True, blank=True)
    disposal_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Disposed: {self.mouse_db}"


# =============================
# UPS
# =============================


class DisposedUPS(models.Model):
    ups_db = models.ForeignKey(UPSDetails, on_delete=models.CASCADE)
    equipment_package = models.ForeignKey(Equipment_Package, related_name='ups_details', on_delete=models.CASCADE, null=True)
    disposed_under = models.ForeignKey(DisposedDesktopDetail, on_delete=models.CASCADE, related_name="disposed_ups", null=True, blank=True)
    
    disposal_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Disposed: {self.equipment_package} | Brand: {self.ups_db.ups_brand_db} | SN: {self.ups_db.ups_sn_db}  "
    



# =============================
# SALVAGED PERIPHERALS (Traceable)
# =============================

class SalvagedMonitor(models.Model):
    monitor = models.ForeignKey("MonitorDetails", on_delete=models.CASCADE)
    equipment_package = models.ForeignKey(
        Equipment_Package, related_name='salvaged_monitors',
        on_delete=models.CASCADE, null=True
    )
    computer_name = models.CharField(max_length=255, blank=True, null=True)
    asset_owner = models.CharField(max_length=255, blank=True, null=True)
    monitor_sn = models.CharField(max_length=255, blank=True, null=True)
    monitor_brand = models.CharField(max_length=255, blank=True, null=True)
    monitor_model = models.CharField(max_length=255, blank=True, null=True)
    monitor_size = models.CharField(max_length=255, blank=True, null=True)

    salvage_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    is_reassigned = models.BooleanField(default=False)
    reassigned_to = models.ForeignKey(
        Equipment_Package, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reassigned_monitors"
    )

    # ➕ new fields
    is_disposed = models.BooleanField(default=False)
    disposed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Salvaged Monitor: {self.monitor_sn or ''} {self.monitor_brand}"

    
class SalvagedMonitorHistory(models.Model):
    salvaged_monitor = models.ForeignKey("SalvagedMonitor", on_delete=models.CASCADE, related_name="history")
    reassigned_to = models.ForeignKey("Equipment_Package", on_delete=models.SET_NULL, null=True, blank=True)
    reassigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.salvaged_monitor.monitor_sn} → {self.reassigned_to} ({self.reassigned_at})"



# Salvaged Keyboard
class SalvagedKeyboard(models.Model):
    keyboard = models.ForeignKey("KeyboardDetails", on_delete=models.CASCADE)
    equipment_package = models.ForeignKey(
        Equipment_Package, related_name='salvaged_keyboards',
        on_delete=models.CASCADE, null=True
    )

    computer_name = models.CharField(max_length=255, blank=True, null=True)
    asset_owner = models.CharField(max_length=255, blank=True, null=True)
    keyboard_sn = models.CharField(max_length=255, blank=True, null=True)
    keyboard_brand = models.CharField(max_length=255, blank=True, null=True)
    keyboard_model = models.CharField(max_length=255, blank=True, null=True)

    salvage_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    is_reassigned = models.BooleanField(default=False)
    reassigned_to = models.ForeignKey(
        Equipment_Package, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reassigned_keyboards"
    )

    # ➕ same as SalvagedMonitor
    is_disposed = models.BooleanField(default=False)
    disposed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Salvaged Keyboard: {self.keyboard_sn or ''} {self.keyboard_brand}"


class SalvagedKeyboardHistory(models.Model):
    salvaged_keyboard = models.ForeignKey(
        "SalvagedKeyboard", on_delete=models.CASCADE, related_name="history"
    )
    reassigned_to = models.ForeignKey("Equipment_Package", on_delete=models.SET_NULL, null=True, blank=True)
    reassigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.salvaged_keyboard.keyboard_sn} → {self.reassigned_to} ({self.reassigned_at})"


# Salvaged Mouse
class SalvagedMouse(models.Model):
    mouse = models.ForeignKey("MouseDetails", on_delete=models.CASCADE)
    equipment_package = models.ForeignKey(
        Equipment_Package, related_name='salvaged_mice',
        on_delete=models.CASCADE, null=True
    )

    computer_name = models.CharField(max_length=255, blank=True, null=True)
    asset_owner = models.CharField(max_length=255, blank=True, null=True)
    mouse_sn = models.CharField(max_length=255, blank=True, null=True)
    mouse_brand = models.CharField(max_length=255, blank=True, null=True)
    mouse_model = models.CharField(max_length=255, blank=True, null=True)

    salvage_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    is_reassigned = models.BooleanField(default=False)
    reassigned_to = models.ForeignKey(
        Equipment_Package, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reassigned_mice"
    )

    # ➕ same as SalvagedMonitor
    is_disposed = models.BooleanField(default=False)
    disposed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Salvaged Mouse: {self.mouse_sn or ''} {self.mouse_brand}"


class SalvagedMouseHistory(models.Model):
    salvaged_mouse = models.ForeignKey(
        "SalvagedMouse", on_delete=models.CASCADE, related_name="history"
    )
    reassigned_to = models.ForeignKey("Equipment_Package", on_delete=models.SET_NULL, null=True, blank=True)
    reassigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.salvaged_mouse.mouse_sn} → {self.reassigned_to} ({self.reassigned_at})"


# Salvaged UPS
class SalvagedUPS(models.Model):
    ups = models.ForeignKey("UPSDetails", on_delete=models.CASCADE)
    equipment_package = models.ForeignKey(
        Equipment_Package, related_name='salvaged_ups',
        on_delete=models.CASCADE, null=True
    )

    computer_name = models.CharField(max_length=255, blank=True, null=True)
    asset_owner = models.CharField(max_length=255, blank=True, null=True)
    ups_sn = models.CharField(max_length=255, blank=True, null=True)
    ups_brand = models.CharField(max_length=255, blank=True, null=True)
    ups_model = models.CharField(max_length=255, blank=True, null=True)
    ups_capacity = models.CharField(max_length=255, blank=True, null=True)

    salvage_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    is_reassigned = models.BooleanField(default=False)
    reassigned_to = models.ForeignKey(
        Equipment_Package, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reassigned_ups"
    )

    # ➕ same as SalvagedMonitor
    is_disposed = models.BooleanField(default=False)
    disposed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Salvaged UPS: {self.ups_sn or ''} {self.ups_brand}"


class SalvagedUPSHistory(models.Model):
    salvaged_ups = models.ForeignKey(
        "SalvagedUPS", on_delete=models.CASCADE, related_name="history"
    )
    reassigned_to = models.ForeignKey("Equipment_Package", on_delete=models.SET_NULL, null=True, blank=True)
    reassigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.salvaged_ups.ups_sn} → {self.reassigned_to} ({self.reassigned_at})"





class DocumentsDetails(models.Model):
    equipment_package = models.ForeignKey(
        Equipment_Package, related_name='docs',
        on_delete=models.CASCADE, null=True, blank=True
    )
    laptop_package = models.ForeignKey(
        "LaptopPackage", related_name='docs',
        on_delete=models.CASCADE, null=True, blank=True
    )
    printer_package = models.ForeignKey(
        "PrinterPackage", related_name='docs',
        on_delete=models.CASCADE, null=True, blank=True
    )


    docs_PAR = models.CharField(max_length=100, blank=True, null=True)
    docs_Propertyno = models.CharField(max_length=100, blank=True, null=True)
    docs_Acquisition_Type = models.CharField(max_length=100, blank=True, null=True)
    docs_Value = models.CharField(max_length=100, blank=True, null=True)
    docs_Datereceived = models.CharField(max_length=100, blank=True, null=True)
    docs_Dateinspected = models.CharField(max_length=100, blank=True, null=True)
    docs_Supplier = models.CharField(max_length=100, blank=True, null=True)
    docs_Status = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        if self.equipment_package:
            return f"Docs for Desktop Package {self.equipment_package.id}"
        elif self.laptop_package:
            return f"Docs for Laptop Package {self.laptop_package.id}"
        elif self.printer_package:
            return f"Docs for Printer Package {self.printer_package.id}"
        return "Docs (unlinked)"
    
    

class Employee(models.Model):
    equipment_package = models.ForeignKey(Equipment_Package, on_delete=models.CASCADE, null=True)
    employee_fname = models.CharField(max_length=100, blank=True, null=True)
    employee_mname = models.CharField(max_length=100, blank=True, null=True)
    employee_lname = models.CharField(max_length=100, blank=True, null=True)
    employee_position = models.CharField(max_length=100, blank=True, null=True)   

    employee_office_section = models.ForeignKey('OfficeSection', on_delete=models.SET_NULL, null=True, blank=True)
    employee_level = models.CharField(max_length=100, blank=True, null=True)
    employee_status = models.CharField(max_length=100, blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.employee_fname} {self.employee_lname}".strip()
    
    def __str__(self):
        return f"{self.employee_fname} {self.employee_lname} - {self.employee_office_section}"
    

#This tracks which user changed the End User and when.
   


class PreventiveMaintenance(models.Model):
    equipment_package = models.ForeignKey(
        'Equipment_Package', related_name='maintenances',
        on_delete=models.CASCADE, null=True, blank=True
    )
    laptop_package = models.ForeignKey(
        'LaptopPackage', related_name='maintenances',
        on_delete=models.CASCADE, null=True, blank=True
    )
    pm_schedule_assignment = models.ForeignKey(
        'PMScheduleAssignment', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='maintenances'
    )
    maintenance_date = models.DateField(null=True, blank=True)
    next_schedule = models.DateField(blank=True, null=True)
    performed_by = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_accomplished = models.DateField(null=True, blank=True)
    office = models.CharField(max_length=255, blank=True, null=True)
    end_user = models.CharField(max_length=255, blank=True, null=True)

    task_1 = models.BooleanField(default=False)
    note_1 = models.TextField(blank=True, null=True)
    task_2 = models.BooleanField(default=False)
    note_2 = models.TextField(blank=True, null=True)
    task_3 = models.BooleanField(default=False)
    note_3 = models.TextField(blank=True, null=True)
    task_4 = models.BooleanField(default=False)
    note_4 = models.TextField(blank=True, null=True)
    task_5 = models.BooleanField(default=False)
    note_5 = models.TextField(blank=True, null=True)
    task_6 = models.BooleanField(default=False)
    note_6 = models.TextField(blank=True, null=True)
    task_7 = models.BooleanField(default=False)
    note_7 = models.TextField(blank=True, null=True)
    task_8 = models.BooleanField(default=False)
    note_8 = models.TextField(blank=True, null=True)
    task_9 = models.BooleanField(default=False)
    note_9 = models.TextField(blank=True, null=True)

    def __str__(self):
        device = self.equipment_package or self.laptop_package
        return f"PM for {device} on {self.date_accomplished or 'N/A'}"



class MaintenanceChecklistItem(models.Model):
    maintenance = models.ForeignKey(PreventiveMaintenance, on_delete=models.CASCADE, related_name='items')
    item_text = models.CharField(max_length=255)
    is_checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.item_text} ({'✔' if self.is_checked else '✘'})"



# ==========================
# 🧭 OFFICE & QUARTER MODELS
# ==========================

class OfficeSection(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class QuarterSchedule(models.Model):
    QUARTERS = [
        ('Q1', '1st Quarter'),
        ('Q2', '2nd Quarter'),
        ('Q3', '3rd Quarter'),
        ('Q4', '4th Quarter'),
    ]
    year = models.IntegerField()
    quarter = models.CharField(max_length=2, choices=QUARTERS)

    class Meta:
        unique_together = ('year', 'quarter')

    def __str__(self):
        return f"{self.get_quarter_display()} {self.year}"  
    
    
class PMSectionSchedule(models.Model):
    quarter_schedule = models.ForeignKey(QuarterSchedule, on_delete=models.CASCADE, related_name='schedules')
    section = models.ForeignKey(OfficeSection, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('quarter_schedule', 'section')

    def __str__(self):
        return f"{self.section.name} – {self.quarter_schedule}"
    

class PMScheduleAssignment(models.Model):
    equipment_package = models.ForeignKey(
        Equipment_Package, on_delete=models.CASCADE,
        related_name='pm_assignments', null=True, blank=True
    )
    laptop_package = models.ForeignKey(
        'LaptopPackage', on_delete=models.CASCADE,
        related_name='pm_assignments', null=True, blank=True
    )
    pm_section_schedule = models.ForeignKey(
        'PMSectionSchedule', on_delete=models.CASCADE,
        related_name='schedule_assignments', 
    )
    assigned_date = models.DateField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        target = self.equipment_package or self.laptop_package
        return f"{target} -> {self.pm_section_schedule}"

    # ✅ Validation logic goes here
    def clean(self):
        if not self.equipment_package and not self.laptop_package:
            raise ValidationError("Either equipment_package or laptop_package must be set.")
        if self.equipment_package and self.laptop_package:
            raise ValidationError("Only one of equipment_package or laptop_package can be set.")

#END - Preventivemaintenance REAL - END


#profile model to extend the User model

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    # Optional linkage to your business entity
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)

    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    office_section = models.ForeignKey(OfficeSection, on_delete=models.SET_NULL, null=True, blank=True)

    # NEW: QR
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True, blank=True)
    qr_code = models.ImageField(upload_to="qr/users/", null=True, blank=True)

    # Preferences
    theme = models.CharField(max_length=16, choices=[("light","Light"), ("dark","Dark")], default="light")
    timezone_str = models.CharField(max_length=64, default="Asia/Manila")
    notify_pm_due = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} Profile"

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        # fallback image under your static files
        return "/static/img/default-avatar.png"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()



# ======================================
# ++++++++++++++++++++++++ LAPTOP MODELS ++++++++++++++++++++++++
# ======================================

class LaptopPackage(models.Model):
    """Container for laptop, with PM, QR, disposal flags (like Equipment_Package but simpler)."""
    is_disposed = models.BooleanField(default=False)
    disposal_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    qr_code = models.ImageField(upload_to='qr_codes/laptops', blank=True, null=True)

    pm_schedule_date = models.DateField(null=True, blank=True)
    pm_schedule_notes = models.TextField(null=True, blank=True)

    @property
    def computer_name(self):
        laptop = self.laptop_details.first()
        return laptop.computer_name if laptop else "N/A"

    def __str__(self):
        return f"Laptop Package {self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code:
            generate_qr_for_laptop(self)
            super().save(update_fields=["qr_code"])  

    def __str__(self):
        return f"Laptop Package {self.pk}"           
             

class LaptopDetails(models.Model):
    """Main laptop specs"""
    laptop_package = models.ForeignKey(
        LaptopPackage, related_name='laptop_details', on_delete=models.CASCADE
    )

    laptop_sn_db = models.CharField(max_length=255)
    serial_no_norm = models.CharField(
        max_length=255, null=True, blank=True, db_index=True, editable=False, unique=True
    )

    def save(self, *args, **kwargs):
        self.serial_no_norm = normalize_sn(self.laptop_sn_db)
        super().save(*args, **kwargs)

    computer_name = models.CharField(max_length=255, unique=True, null=True)

    brand_name = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    processor = models.CharField(max_length=100, null=True, blank=True)
    memory = models.CharField(max_length=100, null=True, blank=True)
    drive = models.CharField(max_length=255, null=True, blank=True)

    laptop_OS = models.CharField(max_length=100, blank=True, null=True)
    laptop_Office = models.CharField(max_length=100, blank=True, null=True)
    laptop_OS_keys = models.CharField(max_length=100, blank=True, null=True)
    laptop_Office_keys = models.CharField(max_length=100, blank=True, null=True)

    is_disposed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.laptop_package} : {self.computer_name} | BRAND: {self.brand_name}"


class DisposedLaptop(models.Model):
    laptop = models.ForeignKey("LaptopDetails", on_delete=models.CASCADE)
    serial_no = models.CharField(max_length=255, blank=True, null=True)
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    asset_owner = models.CharField(max_length=255, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    date_disposed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Disposed Laptop : {self.laptop.computer_name if self.laptop else self.serial_no}"
    

#==========================
# CHANGE HISTORY MODELS
class EndUserChangeHistory(models.Model):
    """
    Tracks end user changes for ANY device type (Desktop, Laptop, Printer, etc.)
    Uses GenericForeignKey for flexibility and scalability.
    """
    # Generic relation to any device package
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    device = GenericForeignKey('content_type', 'object_id')
    
    # Change details
    old_enduser = models.ForeignKey(
        Employee, 
        related_name="old_enduser_history", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    new_enduser = models.ForeignKey(
        Employee, 
        related_name="new_enduser_history", 
        on_delete=models.CASCADE, 
        null=True
    )
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = "End User Change History"
        verbose_name_plural = "End User Change Histories"

    def __str__(self):
        device_name = f"{self.content_type.model.capitalize()} #{self.object_id}"
        return f"End User Change: {device_name} on {self.changed_at}"

    @property
    def device_display(self):
        """Returns a readable device name"""
        if hasattr(self.device, 'computer_name'):
            return self.device.computer_name
        elif hasattr(self.device, 'printer_name'):
            return self.device.printer_name
        return f"{self.content_type.model.capitalize()} #{self.object_id}"


class AssetOwnerChangeHistory(models.Model):
    """
    Tracks asset owner changes for ANY device type (Desktop, Laptop, Printer, etc.)
    Uses GenericForeignKey for flexibility and scalability.
    """
    # Generic relation to any device package
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    device = GenericForeignKey('content_type', 'object_id')
    
    # Change details
    old_assetowner = models.ForeignKey(
        Employee, 
        related_name="old_assetowner_history", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    new_assetowner = models.ForeignKey(
        Employee, 
        related_name="new_assetowner_history", 
        on_delete=models.CASCADE, 
        null=True
    )
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = "Asset Owner Change History"
        verbose_name_plural = "Asset Owner Change Histories"

    def __str__(self):
        device_name = f"{self.content_type.model.capitalize()} #{self.object_id}"
        return f"Asset Owner Change: {device_name} on {self.changed_at}"

    @property
    def device_display(self):
        """Returns a readable device name"""
        if hasattr(self.device, 'computer_name'):
            return self.device.computer_name
        elif hasattr(self.device, 'printer_name'):
            return self.device.printer_name
        return f"{self.content_type.model.capitalize()} #{self.object_id}"

################################################## PRINTER MODELS

class PrinterPackage(models.Model):
    """Standalone printer package (separate from desktop equipment)."""
    is_disposed = models.BooleanField(default=False)
    disposal_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    qr_code = models.ImageField(upload_to='qr_codes/printers', blank=True, null=True)
    pm_schedule_date = models.DateField(null=True, blank=True)
    pm_schedule_notes = models.TextField(null=True, blank=True)

    @property
    def printer_name(self):
        printer = self.printer_details.first()
        return printer.printer_model_db if printer else "N/A"

    def __str__(self):
        return f"Printer Package {self.pk}"

class PrinterDetails(models.Model):
    printer_package = models.ForeignKey(
        PrinterPackage, related_name='printers',
        on_delete=models.CASCADE, null=True
    )
    printer_sn_db = models.CharField(max_length=255)
    printer_sn_norm = models.CharField(
        max_length=255, null=True, blank=True, db_index=True,
        editable=False, unique=True
    )

    def save(self, *args, **kwargs):
        self.printer_sn_norm = normalize_sn(self.printer_sn_db)
        super().save(*args, **kwargs)

    printer_brand_db = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    printer_model_db = models.CharField(max_length=255, null=True, blank=True)

    # ✅ Printer-specific specs
    printer_type = models.CharField(max_length=100, blank=True, null=True, help_text="Inkjet, Laser, Dot Matrix, etc.")
    printer_color = models.BooleanField(default=True, help_text="Color or Mono")
    printer_duplex = models.BooleanField(default=False, help_text="Duplex/Double-sided capable?")
    printer_resolution = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 1200x1200 dpi")
    printer_monthly_duty = models.CharField(max_length=100, blank=True, null=True, help_text="Recommended monthly duty cycle")

    is_disposed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def end_user(self):
        """Get the end user (Employee) assigned to this printer's package."""
        if self.printer_package:
            # ✅ Use .all() to leverage prefetched data instead of .filter() which causes new query
            user_details = self.printer_package.user_details.all()
            if user_details:
                return user_details[0].user_Enduser if user_details[0].user_Enduser else None
        return None
    
    @property
    def asset_owner(self):
        """Get the asset owner (Employee) assigned to this printer's package."""
        if self.printer_package:
            # ✅ Use .all() to leverage prefetched data
            user_details = self.printer_package.user_details.all()
            if user_details:
                return user_details[0].user_Assetowner if user_details[0].user_Assetowner else None
        return None
    
    @property
    def user_assignment(self):
        """Get the full UserDetails object for this printer."""
        if self.printer_package:
            # ✅ Use .all() to leverage prefetched data
            user_details = self.printer_package.user_details.all()
            return user_details[0] if user_details else None
        return None

    def __str__(self):
        return f"{self.printer_package} | {self.printer_brand_db} {self.printer_model_db} ({self.printer_sn_db})"
    
    
class DisposedPrinter(models.Model):
    printer_db = models.ForeignKey("PrinterDetails", on_delete=models.CASCADE)
    printer_package = models.ForeignKey(
        PrinterPackage, related_name='disposed_printers',
        on_delete=models.CASCADE, null=True
    )
    disposed_under = models.ForeignKey(
        DisposedDesktopDetail, on_delete=models.CASCADE,
        related_name="disposed_printers", null=True, blank=True
    )

    printer_sn = models.CharField(max_length=255, blank=True, null=True)
    printer_brand = models.CharField(max_length=255, blank=True, null=True)
    printer_model = models.CharField(max_length=255, blank=True, null=True)
    printer_type = models.CharField(max_length=255, blank=True, null=True)
    printer_resolution = models.CharField(max_length=255, blank=True, null=True)
    printer_monthly_duty = models.CharField(max_length=100, blank=True, null=True)

    reason = models.TextField(blank=True, null=True)
    disposal_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    disposed_photo = models.ImageField(upload_to="disposed_printer_photos/", null=True, blank=True)

    def __str__(self):
        return f"Disposed Printer: {self.printer_brand} {self.printer_model} ({self.printer_sn})"