from django.db import models
from django.utils.text import slugify
from django.utils import timezone
# Create your models here.




#################
class Desktop_Package(models.Model):
    
    is_disposed = models.BooleanField(default=False)
    disposal_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        

    def __str__(self):
        return f"Desktop Package No.({self.pk})"

    

class DesktopDetails(models.Model):
    id = models.IntegerField(primary_key=True)  # Allow manual assignment
    desktop_package = models.ForeignKey(Desktop_Package, related_name='desktop_details', on_delete=models.CASCADE)
    
    serial_no = models.CharField(max_length=255)
    computer_name = models.CharField(max_length=255, unique=True, null=True)
    brand_name = models.CharField(max_length=255)
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
        return f"{self.brand_name} {self.model} ({self.serial_no})"

class MonitorDetails(models.Model):
    id = models.IntegerField(primary_key=True)  # Allow manual assignment
    desktop_package_db = models.ForeignKey(Desktop_Package, related_name='monitors', on_delete=models.CASCADE)
    monitor_sn_db = models.CharField(max_length=255)
    monitor_brand_db = models.CharField(max_length=255)
    monitor_model_db = models.CharField(max_length=255)
    monitor_size_db = models.CharField(max_length=255, null=True)
    is_disposed = models.BooleanField(default=False)  # To indicate if the monitor is dispose
    created_at = models.DateTimeField(default=timezone.now)  # Date when the monitor was added

    def __str__(self):
        return f"{self.monitor_brand_db} {self.monitor_model_db} ({self.monitor_sn_db})"
    
 #userdetails   
class UserDetails(models.Model):  
    id = models.IntegerField(primary_key=True)  # Allow manual assignment 
    desktop_package_db = models.ForeignKey(Desktop_Package, related_name='user', on_delete=models.CASCADE, null=True) 
    user_Asset_owner = models.CharField(max_length=100, blank=True, null=True)
    user_Asset_designation = models.CharField(max_length=100, blank=True, null=True)
    user_Asset_section = models.CharField(max_length=100, blank=True, null=True)
    user_Enduser = models.CharField(max_length=100, blank=True, null=True)
    user_Enduser_designation = models.CharField(max_length=100, blank=True, null=True)
    user_Enduser_section = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)  # Date when the user was added

    def __str__(self):
        return f"{self.user_Asset_owner} {self.user_Asset_designation} ({self.user_Asset_section})" 
    
 

class DisposedMonitor(models.Model):
    monitor_disposed_db = models.ForeignKey(MonitorDetails, on_delete=models.CASCADE)
    disposal_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Disposed: {self.monitor}"

class KeyboardDetails(models.Model):
    id = models.IntegerField(primary_key=True)  # Allow manual assignment
    desktop_package = models.ForeignKey(Desktop_Package, related_name='keyboards', on_delete=models.CASCADE)
    keyboard_sn_db = models.CharField(max_length=255)
    keyboard_brand_db = models.CharField(max_length=255)
    keyboard_model_db = models.CharField(max_length=255)
    keyboard_size_db = models.CharField(max_length=255, null=True)
    is_disposed = models.BooleanField(default=False)  # To indicate if the keyboard is disposed
    created_at = models.DateTimeField(default=timezone.now)  # Date when the keyboard was added

    def __str__(self):
        return f"{self.keyboard_brand_db} {self.keyboard_model_db} ({self.keyboard_sn_db})"
    

    

class DisposedKeyboard(models.Model):
    keyboard_dispose_db = models.ForeignKey(KeyboardDetails, on_delete=models.CASCADE)
    disposal_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Disposed: {self.keyboard}"

class MouseDetails(models.Model):
    id = models.IntegerField(primary_key=True)  # Allow manual assignment
    desktop_package = models.ForeignKey(Desktop_Package, related_name='mouse_db', on_delete=models.CASCADE)
    mouse_sn_db = models.CharField(max_length=255, null=True)
    mouse_brand_db = models.CharField(max_length=255, null=True)
    mouse_model_db = models.CharField(max_length=255, null=True)
    is_disposed = models.BooleanField(default=False)  # To indicate if the mouse is disposed
    created_at = models.DateTimeField(default=timezone.now)  # Date when the mouse was added
    

    def __str__(self):
        return f"{self.mouse_brand_db} {self.mouse_model_db} ({self.mouse_sn_db})"

class DisposedMouse(models.Model):
    mouse_db = models.ForeignKey(MouseDetails, on_delete=models.CASCADE)
    disposal_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Disposed: {self.mouse_db}"

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
        return f"{self.ups_brand_db} {self.ups_model_db} ({self.ups_sn_db})"

class DisposedUPS(models.Model):
    ups_db = models.ForeignKey(UPSDetails, on_delete=models.CASCADE)
    disposal_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Disposed: {self.ups}"
    

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
    
    

class OwnershipTransfer(models.Model):
    desktop_package = models.ForeignKey(Desktop_Package, on_delete=models.CASCADE)
    transferred_from = models.CharField(max_length=100, blank=True, null=True)
    transferred_to = models.CharField(max_length=100)
    owner_designation = models.CharField(max_length=100, null=True, blank=True)  # Add this field
    owner_section = models.CharField(max_length=100, null=True, blank=True)      # Add this field
    transfer_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transfer from {self.transferred_from} to {self.transferred_to} on {self.transfer_date}"
    
class OwnershipHistory(models.Model):
    desktop_package = models.ForeignKey(Desktop_Package, on_delete=models.CASCADE)
    previous_owner = models.CharField(max_length=100)
    previous_designation = models.CharField(max_length=100)
    previous_section = models.CharField(max_length=100)
    transfer_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transfer of {self.desktop_package} on {self.transfer_date}"
    
class Employee(models.Model):
    id = models.IntegerField(primary_key=True)  # Allow manual assignment
    employee_fname = models.CharField(max_length=100, blank=True, null=True)
    employee_mname = models.CharField(max_length=100, blank=True, null=True)
    employee_lname = models.CharField(max_length=100, blank=True, null=True)
    employee_position = models.CharField(max_length=100, blank=True, null=True)   
    employee_office = models.CharField(max_length=100, blank=True, null=True)
    employee_status = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.employee_fname} {self.employee_office}"