from django.contrib import admin
from .models import (
    Equipment_Package, DesktopDetails, MonitorDetails, UserDetails, DisposedMonitor,
    KeyboardDetails, DisposedKeyboard, MouseDetails, DisposedMouse,
    UPSDetails, DisposedUPS, DocumentsDetails, Employee, EndUserChangeHistory,
    AssetOwnerChangeHistory, DisposedDesktopDetail, Brand,
    PreventiveMaintenance, OfficeSection, QuarterSchedule, PMSectionSchedule,
    PMScheduleAssignment, MaintenanceChecklistItem, SalvagedMonitor,
    SalvagedMonitorHistory, SalvagedKeyboard, SalvagedKeyboardHistory, SalvagedMouse,
    SalvagedMouseHistory, SalvagedUPS, SalvagedUPSHistory,
    Profile, LaptopPackage, LaptopDetails, DisposedLaptop, PrinterPackage,
    PrinterDetails, DisposedPrinter, Notification,
    OfficeSuppliesPackage, OfficeSuppliesDetails, DisposedOfficeSupplies, DocumentPhoto,
    # New PM Checklist Models
    PMChecklistTemplate, PMChecklistItem, PMChecklistSchedule,
    PMChecklistCompletion, PMChecklistItemCompletion, PMChecklistReport, PMIssueLog,
    EquipmentDowntimeEvent,
    # SNMR Models
    SNMRAreaCategory, SNMRReport, SNMREntry
)

# Register your models here.
admin.site.register(Equipment_Package)
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
admin.site.register(LaptopPackage)
admin.site.register(LaptopDetails)
admin.site.register(DisposedLaptop)
admin.site.register(PrinterPackage)
admin.site.register(PrinterDetails)
admin.site.register(DisposedPrinter)
admin.site.register(Notification)
admin.site.register(OfficeSuppliesPackage)
admin.site.register(OfficeSuppliesDetails)
admin.site.register(DisposedOfficeSupplies)
admin.site.register(DocumentPhoto)

# PM Checklist System Models
admin.site.register(PMChecklistTemplate)
admin.site.register(PMChecklistItem)
admin.site.register(PMChecklistSchedule)
admin.site.register(PMChecklistCompletion)
admin.site.register(PMChecklistItemCompletion)
admin.site.register(PMChecklistReport)
admin.site.register(EquipmentDowntimeEvent)
admin.site.register(PMIssueLog)

# SNMR - Server and Network Monitoring Report
admin.site.register(SNMRAreaCategory)
admin.site.register(SNMRReport)
admin.site.register(SNMREntry)