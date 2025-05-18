from django.db import models
from django.utils.text import slugify
from django.utils import timezone 
from django.contrib.auth.models import User     # Import the User model if you have a custom user model, otherwise use the default Django User model  
from django.utils.timezone import now
import qrcode
from django.core.files import File # Import File to save the QR code image
from django.urls import reverse # Import reverse to generate URLs for the QR code image
from io import BytesIO  # Import BytesIO to handle the image in memory



# Create your models here.

#################
class Desktop_Package(models.Model):
    
    is_disposed = models.BooleanField(default=False)
    disposal_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True, null=True)

    def __str__(self):
        return f"Desktop Package {self.pk}"

    
# =============================
# ++++++++++++++++++++++++++++++Desktop Details , Monitor, Keyboard, Mouse, UPS
# =============================

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_keyboard = models.BooleanField(default=False)
    is_mouse = models.BooleanField(default=False)
    is_monitor = models.BooleanField(default=False)
    is_ups = models.BooleanField(default=False)
    is_desktop = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class DesktopDetails(models.Model):
    id = models.IntegerField(primary_key=True)  # Allow manual assignment
    desktop_package = models.ForeignKey(Desktop_Package, related_name='desktop_details', on_delete=models.CASCADE)
    
    serial_no = models.CharField(max_length=255)
    computer_name = models.CharField(max_length=255, unique=True, null=True)
    brand_name = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True) 
    model = models.CharField(max_length=255, null=True)
    processor = models.CharField(max_length=33, null=True)
    memory = models.CharField(max_length=100, null=True)
    drive = models.CharField(max_length=332, null=True)
    asset_owner = models.CharField(max_length=255, null=True)

    desktop_Graphics = models.CharField(max_length=100, blank=True, null=True)
    desktop_Graphics_Size = models.CharField(max_length=100, blank=True, null=True)
    
    desktop_OS = models.CharField(max_length=100, blank=True, null=True)
    desktop_Office = models.CharField(max_length=100, blank=True, null=True)
    desktop_OS_keys = models.CharField(max_length=100, blank=True, null=True)
    desktop_Office_keys = models.CharField(max_length=100, blank=True, null=True)
    is_disposed = models.BooleanField(default=False)  # To indicate if the Desktop is disposed
    created_at = models.DateTimeField(default=timezone.now)  # Date when the desktop was added
    

    def __str__(self):
        return f"{self.desktop_package} : {self.computer_name} | BRAND: {self.brand_name}"

  #monitor details  
class MonitorDetails(models.Model):
    # id = models.IntegerField(primary_key=True)  # Allow manual assignment
    desktop_package_db = models.ForeignKey(Desktop_Package, related_name='monitors', on_delete=models.CASCADE)
    monitor_sn_db = models.CharField(max_length=255)
    monitor_brand_db = models.CharField(max_length=255)
    monitor_model_db = models.CharField(max_length=255)
    monitor_size_db = models.CharField(max_length=255, null=True)
    is_disposed = models.BooleanField(default=False)  # To indicate if the monitor is dispose
    created_at = models.DateTimeField(default=timezone.now)  # Date when the monitor was added

    def __str__(self):
        return f"{self.desktop_package_db} | BRAND: {self.monitor_brand_db}"

#keyboard details
class KeyboardDetails(models.Model):
    # id = models.IntegerField(primary_key=True)  # Allow manual assignment
    desktop_package = models.ForeignKey(Desktop_Package, related_name='keyboards', on_delete=models.CASCADE)
    keyboard_sn_db = models.CharField(max_length=255)
    keyboard_brand_db = models.CharField(max_length=255)
    keyboard_model_db = models.CharField(max_length=255)
    is_disposed = models.BooleanField(default=False)  # To indicate if the keyboard is disposed
    created_at = models.DateTimeField(default=timezone.now)  # Date when the keyboard was added

    def __str__(self):
        return f"{self.desktop_package} : - {self.keyboard_brand_db} {self.keyboard_model_db} ({self.keyboard_sn_db})"   
    
#mouse details
class MouseDetails(models.Model):
    id = models.IntegerField(primary_key=True)  # Allow manual assignment
    desktop_package = models.ForeignKey(Desktop_Package, related_name='mouse_db', on_delete=models.CASCADE)
    mouse_sn_db = models.CharField(max_length=255, null=True)
    mouse_brand_db = models.CharField(max_length=255, null=True)
    mouse_model_db = models.CharField(max_length=255, null=True)
    is_disposed = models.BooleanField(default=False)  # To indicate if the mouse is disposed
    created_at = models.DateTimeField(default=timezone.now)  # Date when the mouse was added
    

    def __str__(self):
        return f"{self.desktop_package} {self.mouse_brand_db} {self.mouse_model_db} ({self.mouse_sn_db})"
    
 #ups details
class UPSDetails(models.Model):
    id = models.IntegerField(primary_key=True)  # Allow manual assignment
    desktop_package = models.ForeignKey(Desktop_Package, related_name='ups', on_delete=models.CASCADE)
    ups_sn_db = models.CharField(max_length=255)
    ups_brand_db = models.CharField(max_length=255)
    ups_model_db = models.CharField(max_length=255)
    ups_capacity_db = models.CharField(max_length=255, null=True)
    is_disposed = models.BooleanField(default=False)  # To indicate if the mouse is disposed
    created_at = models.DateTimeField(default=timezone.now)  # Date when the UPS was added

    def __str__(self):
        return f" {self.desktop_package} {self.ups_brand_db} {self.ups_model_db} ({self.ups_sn_db}) "

#user details 
class UserDetails(models.Model):  
    id = models.AutoField(primary_key=True)  
    desktop_package_db = models.ForeignKey("Desktop_Package", on_delete=models.CASCADE, null=True)  
    user_Enduser = models.ForeignKey("Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name='enduser_details')
    user_Assetowner = models.ForeignKey("Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name='assetowner_details')
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user_Enduser}"

# =====================================
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++END OF DESKTOP,KEYBOARD,MOUSE,UPS DETAILS++++++++++++++++++++++++++++++++++++++
# ======================================

# ======================================
# +++++++++++++++++++++++++++++++++++++DISPOSED DETAILS DESKTOP, KEYBOARD, MOUSE, UPS++++++++++++
# ======================================

class DisposedDesktopDetail(models.Model):
    desktop = models.ForeignKey("DesktopDetails", on_delete=models.CASCADE)
    # desktop_package_number = models.CharField(max_length=255, blank=True, null=True)
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
    desktop_package_db = models.ForeignKey(Desktop_Package, related_name='monitors_details', on_delete=models.CASCADE, null=True)
    disposed_under = models.ForeignKey(DisposedDesktopDetail, on_delete=models.CASCADE, related_name="disposed_monitors", null=True, blank=True)
    monitor_sn = models.CharField(max_length=255, blank=True, null=True)
    monitor_brand = models.CharField(max_length=255, blank=True, null=True)
    monitor_model = models.CharField(max_length=255, blank=True, null=True)
    monitor_size = models.CharField(max_length=255, blank=True, null=True)
    disposal_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Disposed Monitor : - {self.monitor_disposed_db} "
    


class DisposedKeyboard(models.Model):
    keyboard_dispose_db = models.ForeignKey(KeyboardDetails, on_delete=models.CASCADE)
    desktop_package = models.ForeignKey(Desktop_Package, related_name='keyboards_details', on_delete=models.CASCADE, null=True)
    disposed_under = models.ForeignKey(DisposedDesktopDetail, on_delete=models.CASCADE, related_name="disposed_keyboards", null=True, blank=True)
    disposal_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Disposed: - {self.desktop_package} - {self.keyboard_dispose_db.keyboard_sn_db}"



class DisposedMouse(models.Model):
    mouse_db = models.ForeignKey(MouseDetails, on_delete=models.CASCADE)
    desktop_package = models.ForeignKey(Desktop_Package, related_name='mouse_details', on_delete=models.CASCADE, null=True)
    disposed_under = models.ForeignKey(DisposedDesktopDetail, on_delete=models.CASCADE, related_name="disposed_ups", null=True, blank=True)
    disposal_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Disposed: {self.mouse_db}"


# =============================
# UPS
# =============================


class DisposedUPS(models.Model):
    ups_db = models.ForeignKey(UPSDetails, on_delete=models.CASCADE)
    desktop_package = models.ForeignKey(Desktop_Package, related_name='ups_details', on_delete=models.CASCADE, null=True)
    disposed_under = models.ForeignKey(DisposedDesktopDetail, on_delete=models.CASCADE, related_name="disposed_mice", null=True, blank=True)
    disposal_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Disposed: {self.desktop_package} | Brand: {self.ups_db.ups_brand_db} | SN: {self.ups_db.ups_sn_db}  "
    

class DocumentsDetails(models.Model):
    id = models.IntegerField(primary_key=True)  # Allow manual assignment
    desktop_package = models.ForeignKey(Desktop_Package, related_name='docs', on_delete=models.CASCADE)
    docs_PAR = models.CharField(max_length=100, blank=True, null=True)
    docs_Propertyno = models.CharField(max_length=100, blank=True, null=True)
    docs_Acquisition_Type = models.CharField(max_length=100, blank=True, null=True)
    docs_Value = models.CharField(max_length=100, blank=True, null=True)
    docs_Datereceived= models.CharField(max_length=100, blank=True, null=True)
    docs_Dateinspected = models.CharField(max_length=100, blank=True, null=True)
    docs_Supplier = models.CharField(max_length=100, blank=True, null=True)
    docs_Status = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.docs_PAR} {self.docs_Datereceived} ({self.docs_Status})"
    
    

class Employee(models.Model):
    desktop_package = models.ForeignKey(Desktop_Package, on_delete=models.CASCADE, null=True)
    employee_fname = models.CharField(max_length=100, blank=True, null=True)
    employee_mname = models.CharField(max_length=100, blank=True, null=True)
    employee_lname = models.CharField(max_length=100, blank=True, null=True)
    employee_position = models.CharField(max_length=100, blank=True, null=True)   
    employee_office = models.CharField(max_length=100, blank=True, null=True)
    employee_status = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.employee_fname} {self.employee_lname} - {self.employee_office}"
    

#This tracks which user changed the End User and when.
   
class EndUserChangeHistory(models.Model):
    desktop_package = models.ForeignKey(Desktop_Package, on_delete=models.CASCADE)
    old_enduser = models.ForeignKey(Employee, related_name="old_enduser", on_delete=models.SET_NULL, null=True, blank=True)
    new_enduser = models.ForeignKey(Employee, related_name="new_enduser", on_delete=models.CASCADE, null=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)  # Use auto_now_add to save the time automatically

class AssetOwnerChangeHistory(models.Model):
    desktop_package = models.ForeignKey(Desktop_Package, on_delete=models.CASCADE)
    old_assetowner = models.ForeignKey(Employee, related_name="old_assetowner", on_delete=models.SET_NULL, null=True, blank=True)
    new_assetowner = models.ForeignKey(Employee, related_name="new_assetowner", on_delete=models.CASCADE, null=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)  # Use auto_now_add to save the time automatically
