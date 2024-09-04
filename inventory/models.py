from django.db import models

# Create your models here.


# old database
class Equipment(models.Model):

    

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
    desktop_Graphics = models.CharField(max_length=100)
    desktop_Graphics_Size = models.CharField(max_length=100)
    desktop_OS = models.CharField(max_length=100)
    desktop_Office = models.CharField(max_length=100)
    desktop_OS_keys = models.CharField(max_length=100)
    desktop_Office_keys = models.CharField(max_length=100, default="test")

    def __str__(self):
        return 'IT EQUPMENT: ' + self.name 
    
# new database try rani 

class DESKTOPPACKAGE(models.Model):

    id_number = models.AutoField(primary_key=True)

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
    desktop_Graphics = models.CharField(max_length=100)
    desktop_Graphics_Size = models.CharField(max_length=100)
    desktop_OS = models.CharField(max_length=100)
    desktop_Office = models.CharField(max_length=100)
    desktop_OS_keys = models.CharField(max_length=100)
    desktop_Office_keys = models.CharField(max_length=100, default="test")

    def __str__(self):
        return 'IT EQUPMENT: ' + self.name 












    #   modelname = models.CharField(max_length=100)
    # Parnumber = models.CharField(max_length=33)
    # PropertyNumber = models.CharField(max_length=100)
    # Purchasedate = models.CharField(max_length=332)
    # Computername = models.CharField(max_length=100)
    # Windowsversion = models.CharField(max_length=100)
    # UnitCost = models.CharField(max_length=100)
    # EndUser = models.CharField(max_length=100)
    # Designation = models.CharField(max_length=100)