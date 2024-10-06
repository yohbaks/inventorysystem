from django.contrib import admin
from .models import DESKTOPPACKAGE
from .models import (
    Desktop_Package, DesktopDetails, MonitorDetails, DisposedMonitor, 
    KeyboardDetails, DisposedKeyboard, MouseDetails, DisposedMouse, 
    UPSDetails, DisposedUPS
)

# Register your models here.
admin.site.register(DESKTOPPACKAGE)
admin.site.register(Desktop_Package)
admin.site.register(DesktopDetails)
admin.site.register(MonitorDetails)
admin.site.register(DisposedMonitor)
admin.site.register(KeyboardDetails)
admin.site.register(DisposedKeyboard)
admin.site.register(MouseDetails)
admin.site.register(DisposedMouse)
admin.site.register(UPSDetails)
admin.site.register(DisposedUPS)