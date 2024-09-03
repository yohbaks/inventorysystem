from django.db import models

# Create your models here.


# old
class Equipment(models.Model):

    EQUIPMENT_CHOICES = [
        ('Desktop', 'Desktop'),
        ('Laptop', 'Laptop'),
        ('UPS', 'UPS'),
        ('Mouse', 'Mouse'),
    ]

    # serialno = models.AutoField(primary_key=True, default="1")
    name = models.CharField(
        max_length=100,
        choices=EQUIPMENT_CHOICES,  # Use choices here
        default='desktop'  # Default value if needed
    )
    serialE = models.CharField(max_length=100)
    brandname = models.CharField(max_length=100)
    modelname = models.CharField(max_length=100)
    Parnumber = models.CharField(max_length=33)
    PropertyNumber = models.CharField(max_length=100)
    Purchasedate = models.CharField(max_length=332)
    Computername = models.CharField(max_length=100)
    Windowsversion = models.CharField(max_length=100)
    UnitCost = models.CharField(max_length=100)
    EndUser = models.CharField(max_length=100)
    Designation = models.CharField(max_length=100)

  
    

    def __str__(self):
        return 'IT EQUPMENT: ' + self.name 