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
    desktop_Graphics = models.CharField(max_length=100)
    desktop_Graphics_Size = models.CharField(max_length=100)
    desktop_OS = models.CharField(max_length=100)
    desktop_Office = models.CharField(max_length=100)
    desktop_OS_keys = models.CharField(max_length=100)
    desktop_Office_keys = models.CharField(max_length=100)
    desktop_Image = models.ImageField(upload_to='equipment_images/', blank=True, null=True)  # Add this line

    
    def __str__(self):
        return 'IT EQUPMENT: ' + self.name 


