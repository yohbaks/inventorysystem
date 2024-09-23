from django.db import models
from django.utils.text import slugify
# Create your models here.



class DESKTOPPACKAGE(models.Model):

    id = models.AutoField(primary_key=True)

    EQUIPMENT_CHOICES = [
        ('Desktop', 'Desktop'),
        ('Laptop', 'Laptop'),
        ('UPS', 'UPS'),
        ('Mouse', 'Mouse'),
    ]

    name = models.CharField(
        max_length=100,
        choices=EQUIPMENT_CHOICES,  # Use choices here
        default='desktop'  # Default value if needed
    )
    desktop_SerialNo = models.CharField(max_length=100)
    desktop_BrandName = models.CharField(max_length=100)
    desktop_Model = models.CharField(max_length=100)
    desktop_Processor = models.CharField(max_length=33)
    desktop_Memory = models.CharField(max_length=100)
    desktop_Drive = models.CharField(max_length=332)

    #Graphics
    desktop_Graphics = models.CharField(max_length=100, blank=True, null=True)
    desktop_Graphics_Size = models.CharField(max_length=100, blank=True, null=True)
    
    desktop_OS = models.CharField(max_length=100, blank=True, null=True)
    desktop_Office = models.CharField(max_length=100, blank=True, null=True)
    desktop_OS_keys = models.CharField(max_length=100, blank=True, null=True)
    desktop_Office_keys = models.CharField(max_length=100, blank=True, null=True)
    desktop_Image = models.ImageField(upload_to='equipment_images/', blank=True, null=True)  # Add this line
    
    # monitor
    desktop_Monitor_SN = models.CharField(max_length=100, blank=True, null=True)
    desktop_Monitor_Brand = models.CharField(max_length=100, blank=True, null=True)
    desktop_Monitor_Model = models.CharField(max_length=100, blank=True, null=True)
    desktop_Monitor_Size = models.CharField(max_length=100, blank=True, null=True)
    
    # keyboard
    desktop_Keyboard_SN = models.CharField(max_length=100, blank=True, null=True)
    desktop_keyboard_Brand = models.CharField(max_length=100, blank=True, null=True)
    desktop_keyboard_Model = models.CharField(max_length=100, blank=True, null=True)

    # Mouse
    desktop_Mouse_SN = models.CharField(max_length=100, blank=True, null=True)
    desktop_Mouse_Brand = models.CharField(max_length=100, blank=True, null=True)
    desktop_Mouse_Model = models.CharField(max_length=100, blank=True, null=True)

    # UPS
    desktop_UPS_SN = models.CharField(max_length=100, blank=True, null=True)
    desktop_UPS_Brand = models.CharField(max_length=100, blank=True, null=True)
    desktop_UPS_Model = models.CharField(max_length=100, blank=True, null=True)

    # User details
    desktop_Asset_owner = models.CharField(max_length=100, blank=True, null=True)
    desktop_Asset_designation = models.CharField(max_length=100, blank=True, null=True)
    desktop_Asset_section = models.CharField(max_length=100, blank=True, null=True)
    desktop_Enduser = models.CharField(max_length=100, blank=True, null=True)
    desktop_Enduser_designation = models.CharField(max_length=100, blank=True, null=True)
    desktop_Enduser_section = models.CharField(max_length=100, blank=True, null=True)

    #Documents

    desktop_PAR = models.CharField(max_length=100, blank=True, null=True)
    desktop_Propertyno = models.CharField(max_length=100, blank=True, null=True)
    desktop_Acquisition_Type = models.CharField(max_length=100, blank=True, null=True)
    desktop_Value = models.CharField(max_length=100, blank=True, null=True)
    desktop_Datereceived= models.CharField(max_length=100, blank=True, null=True)
    desktop_Dateinspected = models.CharField(max_length=100, blank=True, null=True)
    desktop_Supplier = models.CharField(max_length=100, blank=True, null=True)
    desktop_Status = models.CharField(max_length=100, blank=True, null=True)
    desktop_Computer_name = models.CharField(max_length=100, blank=True, null=True)


     # New field to track disposed status

    is_disposed = models.BooleanField(default=False)  # Field to indicate disposal status, Default is False (not disposed)
    disposal_date = models.DateField(null=True, blank=True)  # Optional: Track the date of disposal
    
    def __str__(self):
        return 'IT EQUPMENT: ' + self.name 


