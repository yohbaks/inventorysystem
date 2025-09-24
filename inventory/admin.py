from django.contrib import admin
from .models import (
    Desktop_Package, DesktopDetails, MonitorDetails, UserDetails, DisposedMonitor, 
    KeyboardDetails, DisposedKeyboard, MouseDetails, DisposedMouse, 
    UPSDetails, DisposedUPS, DocumentsDetails, Employee, EndUserChangeHistory, AssetOwnerChangeHistory, DisposedDesktopDetail, Brand,
    PreventiveMaintenance, OfficeSection, QuarterSchedule, PMSectionSchedule, PMScheduleAssignment, MaintenanceChecklistItem, SalvagedMonitor,
    SalvagedMonitorHistory, SalvagedKeyboard, SalvagedKeyboardHistory, SalvagedMouse, SalvagedMouseHistory, SalvagedUPS, SalvagedUPSHistory,
    Profile
)

# Register your models here.
# admin.site.register(DESKTOPPACKAGE)
admin.site.register(Desktop_Package)
admin.site.register(DesktopDetails)
admin.site.register(MonitorDetails)
admin.site.register(UserDetails)
admin.site.register(DisposedMonitor)
admin.site.register(KeyboardDetails)
admin.site.register(DisposedKeyboard)
admin.site.register(MouseDetails)
admin.site.register(DisposedMouse)
admin.site.register(UPSDetails)
admin.site.register(DisposedUPS)
admin.site.register(DocumentsDetails)
admin.site.register(Employee)
admin.site.register(EndUserChangeHistory)
admin.site.register(AssetOwnerChangeHistory)
admin.site.register(DisposedDesktopDetail)
admin.site.register(Brand)
admin.site.register(PreventiveMaintenance)
admin.site.register(OfficeSection)
admin.site.register(QuarterSchedule)
admin.site.register(PMSectionSchedule)
admin.site.register(PMScheduleAssignment)
admin.site.register(MaintenanceChecklistItem)
admin.site.register(SalvagedMonitor)
admin.site.register(SalvagedMonitorHistory)
admin.site.register(SalvagedKeyboard)
admin.site.register(SalvagedMouse)
admin.site.register(SalvagedUPS)
admin.site.register(SalvagedKeyboardHistory)
admin.site.register(SalvagedMouseHistory)
admin.site.register(SalvagedUPSHistory)
admin.site.register(Profile)





