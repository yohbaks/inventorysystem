from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, FileResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import now
from django.utils.dateformat import DateFormat
from django.db import transaction
from django.db.models import Count, Prefetch, Max
from django.db.models.functions import TruncMonth, TruncDay
from django.conf import settings
from django.templatetags.static import static

# Python standard library
import io
import os
import traceback
from datetime import datetime, timedelta
from calendar import month_abbr
from collections import defaultdict

# Third-party libraries
from weasyprint import HTML
from openpyxl import load_workbook, Workbook
from openpyxl.styles import PatternFill
from fpdf import FPDF
from docx import Document
from docx2pdf import convert
import pythoncom  # for Windows COM support (docx2pdf)
from win32com.client import Dispatch  # Windows COM (docx2pdf)

# Local models
from inventory.models import (
    Desktop_Package, DesktopDetails, KeyboardDetails, MouseDetails, MonitorDetails,
    UPSDetails, UserDetails, DocumentsDetails, Employee, Brand,
    DisposedDesktopDetail, DisposedKeyboard, DisposedMouse, DisposedMonitor, DisposedUPS,
    SalvagedMonitor, SalvagedKeyboard, SalvagedMouse, SalvagedUPS,
    SalvagedMonitorHistory, SalvagedKeyboardHistory, SalvagedMouseHistory, SalvagedUPSHistory,
    EndUserChangeHistory, AssetOwnerChangeHistory,
    PreventiveMaintenance, PMScheduleAssignment, MaintenanceChecklistItem,
    QuarterSchedule, PMSectionSchedule, OfficeSection,
)



##############################################################################
def salvage_monitor_logic(monitor, new_package=None, notes=None):
    # Ensure uniqueness by monitor_sn
    salvaged_monitor, created = SalvagedMonitor.objects.get_or_create(
        monitor_sn=monitor.monitor_sn_db,
        defaults={
            'monitor': monitor,
            'desktop_package': monitor.desktop_package,
            'monitor_brand': str(monitor.monitor_brand_db) if monitor.monitor_brand_db else None,
            'monitor_model': monitor.monitor_model_db,
            'monitor_size': monitor.monitor_size_db,
            'computer_name': monitor.desktop_package.computer_name,
            'asset_owner': getattr(monitor.desktop_package.desktop_details.first(), "asset_owner", None),
            'notes': notes or "Salvaged instead of disposed",
        }
    )

    # If row already exists, update it with latest info
    if not created:
        salvaged_monitor.monitor = monitor
        salvaged_monitor.desktop_package = monitor.desktop_package
        salvaged_monitor.monitor_brand = str(monitor.monitor_brand_db) if monitor.monitor_brand_db else None
        salvaged_monitor.monitor_model = monitor.monitor_model_db
        salvaged_monitor.monitor_size = monitor.monitor_size_db
        salvaged_monitor.computer_name = monitor.desktop_package.computer_name
        salvaged_monitor.asset_owner = getattr(monitor.desktop_package.desktop_details.first(), "asset_owner", None)
        if notes:
            salvaged_monitor.notes = notes

    if new_package:  # reassignment
        salvaged_monitor.is_reassigned = True
        salvaged_monitor.reassigned_to = new_package
        salvaged_monitor.computer_name = new_package.computer_name
        salvaged_monitor.asset_owner = getattr(new_package.desktop_details.first(), "asset_owner", None)
        salvaged_monitor.save()

        SalvagedMonitorHistory.objects.create(
            salvaged_monitor=salvaged_monitor,
            reassigned_to=new_package
        )
    else:  # available in salvage stock
        salvaged_monitor.is_reassigned = False
        salvaged_monitor.reassigned_to = None
        salvaged_monitor.save()

    return salvaged_monitor

def salvage_keyboard_logic(keyboard, new_package=None, notes=None):
    salvaged_keyboard, created = SalvagedKeyboard.objects.get_or_create(
        keyboard_sn=keyboard.keyboard_sn_db,
        defaults={
            'keyboard': keyboard,
            'desktop_package': keyboard.desktop_package,
            'keyboard_brand': str(keyboard.keyboard_brand_db) if keyboard.keyboard_brand_db else None,
            'keyboard_model': keyboard.keyboard_model_db,
            'computer_name': keyboard.desktop_package.computer_name,
            'asset_owner': getattr(keyboard.desktop_package.desktop_details.first(), "asset_owner", None),
            'notes': notes or "Salvaged instead of disposed",
        }
    )

    if not created:
        salvaged_keyboard.keyboard = keyboard
        salvaged_keyboard.desktop_package = keyboard.desktop_package
        salvaged_keyboard.keyboard_brand = str(keyboard.keyboard_brand_db) if keyboard.keyboard_brand_db else None
        salvaged_keyboard.keyboard_model = keyboard.keyboard_model_db
        salvaged_keyboard.computer_name = keyboard.desktop_package.computer_name
        salvaged_keyboard.asset_owner = getattr(keyboard.desktop_package.desktop_details.first(), "asset_owner", None)
        if notes:
            salvaged_keyboard.notes = notes

    if new_package:
        salvaged_keyboard.is_reassigned = True
        salvaged_keyboard.reassigned_to = new_package
        salvaged_keyboard.computer_name = new_package.computer_name
        salvaged_keyboard.asset_owner = getattr(new_package.desktop_details.first(), "asset_owner", None)
        salvaged_keyboard.save()

        SalvagedKeyboardHistory.objects.create(
            salvaged_keyboard=salvaged_keyboard,
            reassigned_to=new_package
        )
    else:
        salvaged_keyboard.is_reassigned = False
        salvaged_keyboard.reassigned_to = None
        salvaged_keyboard.save()

    return salvaged_keyboard


def salvage_mouse_logic(mouse, new_package=None, notes=None):
    salvaged_mouse, created = SalvagedMouse.objects.get_or_create(
        mouse_sn=mouse.mouse_sn_db,
        defaults={
            'mouse': mouse,
            'desktop_package': mouse.desktop_package,
            'mouse_brand': str(mouse.mouse_brand_db) if mouse.mouse_brand_db else None,
            'mouse_model': mouse.mouse_model_db,
            'computer_name': mouse.desktop_package.computer_name,
            'asset_owner': getattr(mouse.desktop_package.desktop_details.first(), "asset_owner", None),
            'notes': notes or "Salvaged instead of disposed",
        }
    )

    if not created:
        salvaged_mouse.mouse = mouse
        salvaged_mouse.desktop_package = mouse.desktop_package
        salvaged_mouse.mouse_brand = str(mouse.mouse_brand_db) if mouse.mouse_brand_db else None
        salvaged_mouse.mouse_model = mouse.mouse_model_db
        salvaged_mouse.computer_name = mouse.desktop_package.computer_name
        salvaged_mouse.asset_owner = getattr(mouse.desktop_package.desktop_details.first(), "asset_owner", None)
        if notes:
            salvaged_mouse.notes = notes

    if new_package:
        salvaged_mouse.is_reassigned = True
        salvaged_mouse.reassigned_to = new_package
        salvaged_mouse.computer_name = new_package.computer_name
        salvaged_mouse.asset_owner = getattr(new_package.desktop_details.first(), "asset_owner", None)
        salvaged_mouse.save()

        SalvagedMouseHistory.objects.create(
            salvaged_mouse=salvaged_mouse,
            reassigned_to=new_package
        )
    else:
        salvaged_mouse.is_reassigned = False
        salvaged_mouse.reassigned_to = None
        salvaged_mouse.save()

    return salvaged_mouse


def salvage_ups_logic(ups, new_package=None, notes=None):
    salvaged_ups, created = SalvagedUPS.objects.get_or_create(
        ups_sn=ups.ups_sn_db,
        defaults={
            'ups': ups,
            'desktop_package': ups.desktop_package,
            'ups_brand': str(ups.ups_brand_db) if ups.ups_brand_db else None,
            'ups_model': ups.ups_model_db,
            'ups_capacity': ups.ups_capacity_db,
            'computer_name': ups.desktop_package.computer_name,
            'asset_owner': getattr(ups.desktop_package.desktop_details.first(), "asset_owner", None),
            'notes': notes or "Salvaged instead of disposed",
        }
    )

    if not created:
        salvaged_ups.ups = ups
        salvaged_ups.desktop_package = ups.desktop_package
        salvaged_ups.ups_brand = str(ups.ups_brand_db) if ups.ups_brand_db else None
        salvaged_ups.ups_model = ups.ups_model_db
        salvaged_ups.ups_capacity = ups.ups_capacity_db
        salvaged_ups.computer_name = ups.desktop_package.computer_name
        salvaged_ups.asset_owner = getattr(ups.desktop_package.desktop_details.first(), "asset_owner", None)
        if notes:
            salvaged_ups.notes = notes

    if new_package:
        salvaged_ups.is_reassigned = True
        salvaged_ups.reassigned_to = new_package
        salvaged_ups.computer_name = new_package.computer_name
        salvaged_ups.asset_owner = getattr(new_package.desktop_details.first(), "asset_owner", None)
        salvaged_ups.save()

        SalvagedUPSHistory.objects.create(
            salvaged_ups=salvaged_ups,
            reassigned_to=new_package
        )
    else:
        salvaged_ups.is_reassigned = False
        salvaged_ups.reassigned_to = None
        salvaged_ups.save()

    return salvaged_ups


@login_required  
def success_page(request, desktop_id):
    return render(request, 'success_add.html', {'desktop_id': desktop_id})  # Render the success page template
    
    


#Template: Desktop_details_view
@login_required
def desktop_package_base(request):
    # Fetch all desktop details
    desktop_details = DesktopDetails.objects.all()
    
    # Create a combined list where each desktop is paired with its keyboards
    desktops_with_items = []
    for desktop in desktop_details:
        keyboards = KeyboardDetails.objects.filter(desktop_package=desktop.desktop_package, is_disposed=False)
        user = UserDetails.objects.filter(desktop_package=desktop.desktop_package)
        desktops_with_items.append({
            'desktop': desktop,
            'keyboards': keyboards,  # This can have multiple entries per desktop
            'user': user
        })

    return render(request, 'desktop_details.html', {
        'desktops_with_items': desktops_with_items,
    })   



@login_required
def desktop_details_view(request, package_id):
    desktop_package = get_object_or_404(Desktop_Package, id=package_id)
    desktop_details = DesktopDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).first()
    # Generate QR code if missing
    if not desktop_package.qr_code:
        desktop_package.generate_qr_code()
        desktop_package.save()

    # Active component details
    keyboard_detailsx = KeyboardDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    mouse_details = MouseDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    monitor_detailsx = MonitorDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    ups_details = UPSDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    documents_details = DocumentsDetails.objects.filter(desktop_package=desktop_package)
    user_details = UserDetails.objects.filter(desktop_package=desktop_package).first()

    # Disposed components
    disposed_desktop = DisposedDesktopDetail.objects.filter(desktop__desktop_package=desktop_package)
    disposed_keyboards = DisposedKeyboard.objects.filter(keyboard_dispose_db__desktop_package=desktop_package)
    disposed_mouse = DisposedMouse.objects.filter(mouse_db__desktop_package=desktop_package)
    disposed_monitor = DisposedMonitor.objects.filter(monitor_disposed_db__desktop_package=desktop_package)
    disposed_ups = DisposedUPS.objects.filter(ups_db__desktop_package=desktop_package)

    # Flags for existence
    has_active_desktop = DesktopDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).exists()
    has_active_keyboards = keyboard_detailsx.exists()
    has_active_mouse = mouse_details.exists()
    has_active_monitor = monitor_detailsx.exists()
    has_active_ups = ups_details.exists()
    desktops_disposed_filter = DesktopDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)

    # Brand filters
    desktop_brands  = Brand.objects.filter(is_desktop=True)
    monitor_brands  = Brand.objects.filter(is_monitor=True)
    keyboard_brands = Brand.objects.filter(is_keyboard=True)
    mouse_brands    = Brand.objects.filter(is_mouse=True)
    ups_brands      = Brand.objects.filter(is_ups=True)

    #Preventive Maintenance
    # Preventive Maintenance Schedule Assignments
    pm_assignments = PMScheduleAssignment.objects.filter(
        desktop_package=desktop_package
    ).select_related(
        'pm_section_schedule__section',
        'pm_section_schedule__quarter_schedule'
    )


    # Change history
    enduser_history = EndUserChangeHistory.objects.filter(desktop_package=desktop_package)
    assetowner_history = AssetOwnerChangeHistory.objects.filter(desktop_package=desktop_package)

    # Employees for dropdowns
    employees = Employee.objects.all()

     # ✅ Salvaged for re-adding
    salvaged_monitors = SalvagedMonitor.objects.filter(is_reassigned=False).order_by("-salvage_date")
    salvaged_keyboards = SalvagedKeyboard.objects.filter(is_reassigned=False).order_by("-salvage_date")
    salvaged_mice = SalvagedMouse.objects.filter(is_reassigned=False).order_by("-salvage_date")
    salvaged_ups = SalvagedUPS.objects.filter(is_reassigned=False).order_by("-salvage_date")
    
    # ✅ Salvaged components in view details
    salvaged_monitors_view = SalvagedMonitor.objects.filter(
        desktop_package=desktop_package,
        is_reassigned=False,
        is_disposed=False
    ).order_by("-salvage_date")

    salvaged_keyboards_view = SalvagedKeyboard.objects.filter(
        desktop_package=desktop_package,
        is_reassigned=False,
        is_disposed=False
    ).order_by("-salvage_date")

    salvaged_mice_view = SalvagedMouse.objects.filter(
        desktop_package=desktop_package,
        is_reassigned=False,
        is_disposed=False
    ).order_by("-salvage_date")

    salvaged_ups_view = SalvagedUPS.objects.filter(
        desktop_package=desktop_package,
        is_reassigned=False,
        is_disposed=False
    ).order_by("-salvage_date")

    return render(request, 'desktop_details_view.html', {
        'desktop_detailsx': desktop_details,
        'desktop_package': desktop_package,
        'keyboard_detailse': keyboard_detailsx.first(),
        'monitor_detailse': monitor_detailsx.first(),
        'mouse_detailse': mouse_details.first(),
        'ups_detailse': ups_details.first(),
        'documents_detailse': documents_details.first(),
        'user_details': user_details,
        'disposed_desktop': disposed_desktop,
        'disposed_keyboards': disposed_keyboards,
        'disposed_mouse': disposed_mouse,
        'disposed_monitor': disposed_monitor,
        'disposed_ups': disposed_ups,
        'has_active_desktop': has_active_desktop,
        'has_active_keyboards': has_active_keyboards,
        'has_active_mouse': has_active_mouse,
        'has_active_monitor': has_active_monitor,
        'has_active_ups': has_active_ups,
        'desktops_disposed_filter': desktops_disposed_filter,
        'desktop_brands': desktop_brands,
        'monitor_brands': monitor_brands,
        'keyboard_brands': keyboard_brands,
        'mouse_brands': mouse_brands,
        'ups_brands': ups_brands,

        'employees': employees,
        'enduser_history': enduser_history,
        'assetowner_history': assetowner_history,
        'pm_assignments': pm_assignments,
        'salvaged_monitors': salvaged_monitors,
        'salvaged_keyboards': salvaged_keyboards,
        'salvaged_mice': salvaged_mice,
        'salvaged_ups': salvaged_ups,
        'salvaged_monitors_view': salvaged_monitors_view,
        'salvaged_keyboards_view': salvaged_keyboards_view,
        'salvaged_mice_view': salvaged_mice_view,
        'salvaged_ups_view': salvaged_ups_view,
    })






def keyboard_detailed_view(request, keyboard_id):
    # Get the specific keyboard using its ID
    keyboard = get_object_or_404(KeyboardDetails, id=keyboard_id)
    # Render the detailed view of the keyboard
    return render(request, 'keyboard_detailed_view.html', {'keyboard': keyboard})

def keyboard_update(request, keyboard_id):
    keyboard = get_object_or_404(KeyboardDetails, id=keyboard_id)
    




#update desktop details
@require_POST
def update_desktop(request, pk):
    desktop = get_object_or_404(DesktopDetails, pk=pk)
    desktop.serial_no = request.POST.get('desktop_sn_form')
   
    brand_id = request.POST.get('desktop_brand_form')#check if the brand_id is valid
    desktop.brand_name = get_object_or_404(Brand, pk=brand_id)#update the brand_name

    desktop.model = request.POST.get('desktop_model_form')
    desktop.processor = request.POST.get('desktop_proccessor_form')
    desktop.memory = request.POST.get('desktop_memory_form')
    desktop.drive = request.POST.get('desktop_drive_form')
    
    desktop.save()

    base_url = reverse('desktop_details_view', kwargs={'package_id': desktop.desktop_package.pk})
    return redirect(f'{base_url}#pills-desktop')

#update monitor details
@require_POST
def update_monitor(request, pk):
    monitor                     = get_object_or_404(MonitorDetails, pk=pk)
    monitor.monitor_sn_db       = request.POST.get('monitor_sn_db')

    brand_id = request.POST.get('monitor_brand_db')#check if the brand_id is valid
    monitor.monitor_brand_db = get_object_or_404(Brand, pk=brand_id)#update the brand_name

    monitor.monitor_model_db    = request.POST.get('monitor_model_db')
    monitor.monitor_size_db     = request.POST.get('monitor_size_db')
    
    monitor.save()

    base_url = reverse('desktop_details_view', kwargs={'package_id': monitor.desktop_package.pk})
    return redirect(f'{base_url}#pills-monitor')

#update keyboard details
@require_POST
def update_keyboard(request, pk):
    keyboard                    = get_object_or_404(KeyboardDetails, pk=pk)
    keyboard.keyboard_sn_db     = request.POST.get('keyboard_sn_db')

    brand_id = request.POST.get('keyboard_brand_db')#check if the brand_id is valid
    keyboard.keyboard_brand_db = get_object_or_404(Brand, pk=brand_id)#update the brand_name

    keyboard.keyboard_model_db  = request.POST.get('keyboard_model_db')
    
    keyboard.save()

    base_url = reverse('desktop_details_view', kwargs={'package_id': keyboard.desktop_package.pk})
    return redirect(f'{base_url}#pills-keyboard')

@require_POST
def update_mouse(request, pk):
    mouse = get_object_or_404(MouseDetails, pk=pk)
    mouse.mouse_sn_db       = request.POST.get('mouse_sn_db')

    brand_id = request.POST.get('mouse_brand_db')#check if the brand_id is valid
    mouse.mouse_brand_db = get_object_or_404(Brand, pk=brand_id)#update the brand_name

    mouse.mouse_model_db    = request.POST.get('mouse_model_db')

    mouse.save()
    base_url = reverse('desktop_details_view', kwargs={'package_id': mouse.desktop_package.pk})
    return redirect(f'{base_url}#pills-mouse')

@require_POST
def update_ups(request, pk):
    ups = get_object_or_404(UPSDetails, pk=pk)
    ups.ups_sn_db       = request.POST.get('ups_sn_db')

    brand_id = request.POST.get('ups_brand_db')#check if the brand_id is valid
    ups.ups_brand_db = get_object_or_404(Brand, pk=brand_id)#update the brand_name

    ups.ups_model_db    = request.POST.get('ups_model_db')
    ups.ups_capacity_db = request.POST.get('ups_capacity_db')

    ups.save()
    base_url = reverse('desktop_details_view', kwargs={'package_id': ups.desktop_package.pk})
    return redirect(f'{base_url}#pills-ups')

@require_POST
def update_documents(request, pk):
    documents = get_object_or_404(DocumentsDetails, pk=pk)
    documents.docs_PAR = request.POST.get('docs_PAR')
    documents.docs_Propertyno = request.POST.get('docs_Propertyno')
    documents.docs_Acquisition_Type = request.POST.get('docs_Acquisition_Type')
    documents.docs_Value = request.POST.get('docs_Value')
    documents.docs_Datereceived = request.POST.get('docs_Datereceived')
    documents.docs_Dateinspected = request.POST.get('docs_Dateinspected')
    documents.docs_Supplier = request.POST.get('docs_Supplier')
    documents.docs_Status = request.POST.get('docs_Status')

    documents.save()
    base_url = reverse('desktop_details_view', kwargs={'package_id': documents.desktop_package.pk})
    return redirect(f'{base_url}#pills-documents')

                                            ######## SINGLE DISPOSAL TAB ###########



# Keyboard disposal under Keyboard pill page
def keyboard_disposed(request, keyboard_id):
    if request.method == 'POST':
        keyboard = get_object_or_404(KeyboardDetails, id=keyboard_id)
        keyboard.is_disposed = True
        keyboard.save()

        # Create a DisposedKeyboard record
        DisposedKeyboard.objects.create(
            keyboard_dispose_db=keyboard,
            desktop_package=keyboard.desktop_package,
            disposed_under=None,  # optional if linked to a desktop disposal
            disposal_date=timezone.now()
        )

        # ➕ If salvaged before, tag as disposed
        SalvagedKeyboard.objects.filter(keyboard_sn=keyboard.keyboard_sn_db).update(
            is_disposed=True,
            disposed_date=timezone.now()
        )

        return redirect(f'/desktop_details_view/{keyboard.desktop_package.id}/#pills-keyboard')

    return redirect('desktop_details_view', package_id=keyboard.desktop_package.id)


# Mouse disposal under Mouse pill page
def mouse_disposed(request, mouse_id):
    if request.method == 'POST':
        mouse = get_object_or_404(MouseDetails, id=mouse_id)
        mouse.is_disposed = True
        mouse.save()

        # Create a DisposedMouse record
        DisposedMouse.objects.create(
            mouse_db=mouse,
            desktop_package=mouse.desktop_package,
            disposed_under=None,  # optional if tied to a full desktop disposal
            disposal_date=timezone.now()
        )

        # ➕ If salvaged before, tag as disposed
        SalvagedMouse.objects.filter(mouse_sn=mouse.mouse_sn_db).update(
            is_disposed=True,
            disposed_date=timezone.now()
        )

        return redirect(f'/desktop_details_view/{mouse.desktop_package.id}/#pills-mouse')

    return redirect('desktop_details_view', package_id=mouse.desktop_package.id)


# UPS disposal under UPS pill page
def ups_disposed(request, ups_id):
    if request.method == 'POST':
        ups = get_object_or_404(UPSDetails, id=ups_id)
        ups.is_disposed = True
        ups.save()

        # Create a DisposedUPS record
        DisposedUPS.objects.create(
            ups_db=ups,
            desktop_package=ups.desktop_package,
            disposed_under=None,  # optional if tied to a full desktop disposal
            disposal_date=timezone.now()
        )

        # ➕ If salvaged before, tag as disposed
        SalvagedUPS.objects.filter(ups_sn=ups.ups_sn_db).update(
            is_disposed=True,
            disposed_date=timezone.now()
        )

        return redirect(f'/desktop_details_view/{ups.desktop_package.id}/#pills-ups')

    return redirect('desktop_details_view', package_id=ups.desktop_package.id)

                                            ######## SINGLE END TAB ###########




#viewing of all keyboard disposed sa page ni sa keyboard na naay disposed pud.
def disposed_keyboards(request):
    # Get all disposed keyboards
    disposed_keyboards = DisposedKeyboard.objects.all()
    # Render the list of disposed keyboards to the template
    return render(request, 'disposed_keyboards.html', {'disposed_keyboards': disposed_keyboards})



# END ################ (KEYBOARD END)


# BEGIN ################ (MOUSE)

#This function retrieves all mouse records and renders them in a similar way as mouse_details.

def monitor_details(request):
    """
    Show only current state per monitor serial:
    - Active: MonitorDetails (is_disposed=False) whose serial is NOT in current salvaged-reassigned list
    - Reassigned: SalvagedMonitor (is_reassigned=True, is_disposed=False)
    Disposed units never appear here.
    """
    # 1) Current reassigned (salvaged) monitors
    reassigned_qs = (
        SalvagedMonitor.objects
        .filter(is_reassigned=True, is_disposed=False)
        .select_related("reassigned_to")
    )

    # Normalize serials to avoid duplicates from case/whitespace mismatches
    reassigned_serials = {
        (s.monitor_sn or "").strip().lower()
        for s in reassigned_qs
    }

    # 2) Active monitors EXCLUDING any serial that’s currently reassigned
    active_qs = (
        MonitorDetails.objects
        .filter(is_disposed=False)
        .select_related("desktop_package", "monitor_brand_db")
    )

    active_data = []
    for m in active_qs:
        sn_norm = (m.monitor_sn_db or "").strip().lower()
        if sn_norm in reassigned_serials:
            # Skip: there is a more up-to-date reassigned record for this serial
            continue

        active_data.append({
            "id": m.id,
            "monitor_sn_db": m.monitor_sn_db,
            "monitor_brand_db": m.monitor_brand_db,
            "monitor_model_db": m.monitor_model_db,
            "monitor_size_db": m.monitor_size_db,
            "desktop_package": m.desktop_package,
            "status": "active",
            "salvaged_id": None,
        })

    # 3) Format reassigned rows
    reassigned_data = []
    for s in reassigned_qs:
        reassigned_data.append({
            "id": s.id,
            "monitor_sn_db": s.monitor_sn,
            "monitor_brand_db": s.monitor_brand,
            "monitor_model_db": s.monitor_model,
            "monitor_size_db": s.monitor_size,
            "desktop_package": s.reassigned_to,   # last package assigned (can be None)
            "status": "reassigned",
            "salvaged_id": s.id,
        })

    monitors = active_data + reassigned_data
    return render(request, "monitor_details.html", {"monitors": monitors})

def monitor_timeline_detail(request, salvaged_id):
    salvaged_monitor = get_object_or_404(SalvagedMonitor, pk=salvaged_id)
    history = salvaged_monitor.history.order_by('-reassigned_at')
    return render(request, 'salvage/monitor_timeline_detail.html', {
        "monitor": salvaged_monitor,
        "history": history
    })


def keyboard_details(request):
    # 1) Current reassigned keyboards
    reassigned_qs = (
        SalvagedKeyboard.objects
        .filter(is_reassigned=True, is_disposed=False)
        .select_related("reassigned_to")
    )
    reassigned_serials = {(s.keyboard_sn or "").strip().lower() for s in reassigned_qs}

    # 2) Active keyboards excluding reassigned
    active_qs = KeyboardDetails.objects.filter(is_disposed=False).select_related("desktop_package")
    active_data = []
    for k in active_qs:
        sn_norm = (k.keyboard_sn_db or "").strip().lower()
        if sn_norm in reassigned_serials:
            continue
        active_data.append({
            "id": k.id,
            "keyboard_sn_db": k.keyboard_sn_db,
            "keyboard_brand_db": k.keyboard_brand_db,
            "keyboard_model_db": k.keyboard_model_db,
            "desktop_package": k.desktop_package,
            "status": "active",
            "salvaged_id": None,
        })

    # 3) Reassigned keyboards
    reassigned_data = []
    for s in reassigned_qs:
        reassigned_data.append({
            "id": s.id,
            "keyboard_sn_db": s.keyboard_sn,
            "keyboard_brand_db": s.keyboard_brand,
            "keyboard_model_db": s.keyboard_model,
            "desktop_package": s.reassigned_to,
            "status": "reassigned",
            "salvaged_id": s.id,
        })

    keyboards = active_data + reassigned_data
    return render(request, "keyboard_details.html", {"keyboards": keyboards})



def keyboard_timeline_detail(request, salvaged_id):
    salvaged_keyboard = get_object_or_404(SalvagedKeyboard, pk=salvaged_id)
    history = salvaged_keyboard.history.order_by('-reassigned_at')
    return render(request, 'salvage/keyboard_timeline_detail.html', {
        "keyboard": salvaged_keyboard,
        "history": history
    })

def mouse_details(request):
    reassigned_qs = (
        SalvagedMouse.objects
        .filter(is_reassigned=True, is_disposed=False)
        .select_related("reassigned_to")
    )
    reassigned_serials = {(s.mouse_sn or "").strip().lower() for s in reassigned_qs}

    active_qs = MouseDetails.objects.filter(is_disposed=False).select_related("desktop_package")
    active_data = []
    for m in active_qs:
        sn_norm = (m.mouse_sn_db or "").strip().lower()
        if sn_norm in reassigned_serials:
            continue
        active_data.append({
            "id": m.id,
            "mouse_sn_db": m.mouse_sn_db,
            "mouse_brand_db": m.mouse_brand_db,
            "mouse_model_db": m.mouse_model_db,
            "desktop_package": m.desktop_package,
            "status": "active",
            "salvaged_id": None,
        })

    reassigned_data = []
    for s in reassigned_qs:
        reassigned_data.append({
            "id": s.id,
            "mouse_sn_db": s.mouse_sn,
            "mouse_brand_db": s.mouse_brand,
            "mouse_model_db": s.mouse_model,
            "desktop_package": s.reassigned_to,
            "status": "reassigned",
            "salvaged_id": s.id,
        })

    mice = active_data + reassigned_data
    return render(request, "mouse_details.html", {"mice": mice})



def mouse_timeline_detail(request, salvaged_id):
    salvaged_mouse = get_object_or_404(SalvagedMouse, pk=salvaged_id)
    history = salvaged_mouse.history.order_by('-reassigned_at')
    return render(request, 'salvage/mouse_timeline_detail.html', {
        "mouse": salvaged_mouse,
        "history": history
    })



def ups_details(request):
    reassigned_qs = (
        SalvagedUPS.objects
        .filter(is_reassigned=True, is_disposed=False)
        .select_related("reassigned_to")
    )
    reassigned_serials = {(s.ups_sn or "").strip().lower() for s in reassigned_qs}

    active_qs = UPSDetails.objects.filter(is_disposed=False).select_related("desktop_package")
    active_data = []
    for u in active_qs:
        sn_norm = (u.ups_sn_db or "").strip().lower()
        if sn_norm in reassigned_serials:
            continue
        active_data.append({
            "id": u.id,
            "ups_sn_db": u.ups_sn_db,
            "ups_brand_db": u.ups_brand_db,
            "ups_model_db": u.ups_model_db,
            "desktop_package": u.desktop_package,
            "status": "active",
            "salvaged_id": None,
        })

    reassigned_data = []
    for s in reassigned_qs:
        reassigned_data.append({
            "id": s.id,
            "ups_sn_db": s.ups_sn,
            "ups_brand_db": s.ups_brand,
            "ups_model_db": s.ups_model,
            "desktop_package": s.reassigned_to,
            "status": "reassigned",
            "salvaged_id": s.id,
        })

    ups_list = active_data + reassigned_data
    return render(request, "ups_details.html", {"ups_list": ups_list})



def ups_timeline_detail(request, salvaged_id):
    salvaged_ups = get_object_or_404(SalvagedUPS, pk=salvaged_id)
    history = salvaged_ups.history.order_by('-reassigned_at')
    return render(request, 'salvage/ups_timeline_detail.html', {
        "ups": salvaged_ups,
        "history": history
    })


#This function retrieves the details of a specific mouse by its ID.
def mouse_detailed_view(request, mouse_id):
    # Get the specific mouse using its ID
    mouse = get_object_or_404(MouseDetails, id=mouse_id)
    # Render the detailed view of the mouse
    return render(request, 'mouse_detailed_view.html', {'mouse': mouse})




#monitor disposal under keyboard pill page
def monitor_disposed(request, monitor_id):
    if request.method == 'POST':
        monitor = get_object_or_404(MonitorDetails, id=monitor_id)
        monitor.is_disposed = True
        monitor.save()

        # Create a DisposedMonitor entry
        DisposedMonitor.objects.create(
            monitor_disposed_db=monitor,
            desktop_package=monitor.desktop_package,
            monitor_sn=monitor.monitor_sn_db,
            monitor_brand=str(monitor.monitor_brand_db) if monitor.monitor_brand_db else None,
            monitor_model=monitor.monitor_model_db,
            monitor_size=monitor.monitor_size_db,
            reason=request.POST.get("reason") or "Disposed individually",
        )

        # ➕ Tag SalvagedMonitor as disposed if exists
        from django.utils import timezone
        SalvagedMonitor.objects.filter(monitor_sn=monitor.monitor_sn_db).update(
            is_disposed=True,
            disposed_date=timezone.now()
        )


        return redirect(f'/desktop_details_view/{monitor.desktop_package.id}/#pills-monitor')


#MONITORS
def add_monitor_to_package(request, package_id):
    desktop_package = get_object_or_404(Desktop_Package, id=package_id)

    if request.method == "POST":
        salvaged_monitor_id = request.POST.get("salvaged_monitor_id")

        if salvaged_monitor_id:
            salvaged_monitor = get_object_or_404(SalvagedMonitor, id=salvaged_monitor_id)

            if salvaged_monitor.is_reassigned:
                messages.error(request, "❌ This salvaged monitor has already been reassigned.")
                return redirect("desktop_details_view", package_id=desktop_package.id)

            # ✅ Create active monitor record
            MonitorDetails.objects.create(
                desktop_package=desktop_package,
                monitor_sn_db=salvaged_monitor.monitor_sn,
                monitor_brand_db=Brand.objects.filter(name=salvaged_monitor.monitor_brand).first(),
                monitor_model_db=salvaged_monitor.monitor_model,
                monitor_size_db=salvaged_monitor.monitor_size,
                is_disposed=False,
            )

            # ✅ Update salvaged record
            salvaged_monitor.is_reassigned = True
            salvaged_monitor.reassigned_to = desktop_package
            salvaged_monitor.save()

            # ✅ Log history
            SalvagedMonitorHistory.objects.create(
                salvaged_monitor=salvaged_monitor,
                reassigned_to=desktop_package,
            )

            messages.success(request, "✅ Salvaged monitor reassigned and logged.")
            return redirect("desktop_details_view", package_id=desktop_package.id)


        else:
            # Case 2: Manual Input
            monitor_sn = request.POST.get("monitor_sn")
            monitor_brand_id = request.POST.get("monitor_brand_db")
            monitor_model = request.POST.get("monitor_model")
            monitor_size = request.POST.get("monitor_size")

            if not monitor_sn or not monitor_model:
                messages.error(request, "❌ Please fill in all required fields.")
                return redirect("desktop_details_view", package_id=desktop_package.id)

            # ✅ Convert brand ID into Brand instance
            brand_instance = Brand.objects.filter(id=monitor_brand_id).first() if monitor_brand_id else None

            MonitorDetails.objects.create(
                desktop_package=desktop_package,
                monitor_sn_db=monitor_sn,
                monitor_brand_db=brand_instance,
                monitor_model_db=monitor_model,
                monitor_size_db=monitor_size,
                is_disposed=False,
            )

            messages.success(request, "✅ New monitor added successfully.")
            return redirect("desktop_details_view", package_id=desktop_package.id)

    messages.error(request, "❌ Invalid request.")
    return redirect("desktop_details_view", package_id=desktop_package.id)



def add_keyboard_to_package(request, package_id):
    desktop_package = get_object_or_404(Desktop_Package, id=package_id)

    if request.method == "POST":
        salvaged_keyboard_id = request.POST.get("salvaged_keyboard_id")

        if salvaged_keyboard_id:
            # Case 1: Reassign salvaged keyboard
            salvaged_keyboard = get_object_or_404(SalvagedKeyboard, id=salvaged_keyboard_id)

            if salvaged_keyboard.is_reassigned:
                messages.error(request, "❌ This salvaged keyboard has already been reassigned.")
                return redirect("desktop_details_view", package_id=desktop_package.id)

            # ✅ Create active keyboard record
            KeyboardDetails.objects.create(
                desktop_package=desktop_package,
                keyboard_sn_db=salvaged_keyboard.keyboard_sn,
                keyboard_brand_db=Brand.objects.filter(name=salvaged_keyboard.keyboard_brand).first(),
                keyboard_model_db=salvaged_keyboard.keyboard_model,
                is_disposed=False,
            )

            # ✅ Update salvaged record
            salvaged_keyboard.is_reassigned = True
            salvaged_keyboard.reassigned_to = desktop_package
            salvaged_keyboard.save()

            # ✅ Log history
            SalvagedKeyboardHistory.objects.create(
                salvaged_keyboard=salvaged_keyboard,
                reassigned_to=desktop_package,
            )

            messages.success(request, "✅ Salvaged keyboard reassigned and logged.")
            return redirect("desktop_details_view", package_id=desktop_package.id)

        else:
            # Case 2: Manual Input
            keyboard_sn = request.POST.get("keyboard_sn")
            keyboard_brand_id = request.POST.get("keyboard_brand_db")
            keyboard_model = request.POST.get("keyboard_model")

            if not keyboard_sn or not keyboard_model:
                messages.error(request, "❌ Please fill in all required fields.")
                return redirect("desktop_details_view", package_id=desktop_package.id)

            # ✅ Convert brand ID into Brand instance
            brand_instance = Brand.objects.filter(id=keyboard_brand_id).first() if keyboard_brand_id else None

            KeyboardDetails.objects.create(
                desktop_package=desktop_package,
                keyboard_sn_db=keyboard_sn,
                keyboard_brand_db=brand_instance,
                keyboard_model_db=keyboard_model,
                is_disposed=False,
            )

            messages.success(request, "✅ New keyboard added successfully.")
            return redirect("desktop_details_view", package_id=desktop_package.id)

    messages.error(request, "❌ Invalid request.")
    return redirect("desktop_details_view", package_id=package_id)



#This function allows adding a new mouse to a specific desktop package, then redirects back to the "Mouse" tab of the desktop details view.
def add_mouse_to_package(request, package_id):
    desktop_package = get_object_or_404(Desktop_Package, id=package_id)

    if request.method == "POST":
        salvaged_mouse_id = request.POST.get("salvaged_mouse_id")

        # Case 1: Salvaged Mouse
        if salvaged_mouse_id:
            salvaged_mouse = get_object_or_404(SalvagedMouse, id=salvaged_mouse_id)

            if salvaged_mouse.is_reassigned:
                messages.error(request, "❌ This salvaged mouse has already been reassigned.")
                return redirect("desktop_details_view", package_id=desktop_package.id)

            MouseDetails.objects.create(
                desktop_package=desktop_package,
                mouse_sn_db=salvaged_mouse.mouse_sn,
                mouse_brand_db=Brand.objects.filter(name=salvaged_mouse.mouse_brand).first(),
                mouse_model_db=salvaged_mouse.mouse_model,
                is_disposed=False,
            )

            salvaged_mouse.is_reassigned = True
            salvaged_mouse.reassigned_to = desktop_package
            salvaged_mouse.save()

            SalvagedMouseHistory.objects.create(
                salvaged_mouse=salvaged_mouse,
                reassigned_to=desktop_package,
            )

            messages.success(request, "✅ Salvaged mouse reassigned and logged.")
            return redirect("desktop_details_view", package_id=desktop_package.id)

        # Case 2: Manual Input
        mouse_sn = request.POST.get("mouse_sn")
        mouse_brand_id = request.POST.get("mouse_brand_db")
        mouse_model = request.POST.get("mouse_model")

        if not mouse_sn or not mouse_model:
            messages.error(request, "❌ Please fill in all required fields.")
            return redirect("desktop_details_view", package_id=desktop_package.id)

        brand_instance = Brand.objects.filter(id=mouse_brand_id).first() if mouse_brand_id else None

        MouseDetails.objects.create(
            desktop_package=desktop_package,
            mouse_sn_db=mouse_sn,
            mouse_brand_db=brand_instance,
            mouse_model_db=mouse_model,
            is_disposed=False,
        )

        messages.success(request, "✅ New mouse added successfully.")
        return redirect("desktop_details_view", package_id=desktop_package.id)

    messages.error(request, "❌ Invalid request.")
    return redirect("desktop_details_view", package_id=package_id)


def add_ups_to_package(request, package_id):
    desktop_package = get_object_or_404(Desktop_Package, id=package_id)

    if request.method == "POST":
        salvaged_ups_id = request.POST.get("salvaged_ups_id")

        # Case 1: Salvaged UPS
        if salvaged_ups_id:
            salvaged_ups = get_object_or_404(SalvagedUPS, id=salvaged_ups_id)

            if salvaged_ups.is_reassigned:
                messages.error(request, "❌ This salvaged UPS has already been reassigned.")
                return redirect("desktop_details_view", package_id=desktop_package.id)

            UPSDetails.objects.create(
                desktop_package=desktop_package,
                ups_sn_db=salvaged_ups.ups_sn,
                ups_brand_db=Brand.objects.filter(name=salvaged_ups.ups_brand).first(),
                ups_model_db=salvaged_ups.ups_model,
                is_disposed=False,
            )

            salvaged_ups.is_reassigned = True
            salvaged_ups.reassigned_to = desktop_package
            salvaged_ups.save()

            SalvagedUPSHistory.objects.create(
                salvaged_ups=salvaged_ups,
                reassigned_to=desktop_package,
            )

            messages.success(request, "✅ Salvaged UPS reassigned and logged.")
            return redirect("desktop_details_view", package_id=desktop_package.id)

        # Case 2: Manual Input
        ups_sn = request.POST.get("ups_sn")
        ups_brand_id = request.POST.get("ups_brand_db")
        ups_model = request.POST.get("ups_model")

        if not ups_sn or not ups_model:
            messages.error(request, "❌ Please fill in all required fields.")
            return redirect("desktop_details_view", package_id=desktop_package.id)

        brand_instance = Brand.objects.filter(id=ups_brand_id).first() if ups_brand_id else None

        UPSDetails.objects.create(
            desktop_package=desktop_package,
            ups_sn_db=ups_sn,
            ups_brand_db=brand_instance,
            ups_model_db=ups_model,
            is_disposed=False,
        )

        messages.success(request, "✅ New UPS added successfully.")
        return redirect("desktop_details_view", package_id=desktop_package.id)

    messages.error(request, "❌ Invalid request.")
    return redirect("desktop_details_view", package_id=package_id)


#This function lists all disposed mice, assuming you have a DisposedMouse model similar to DisposedKeyboard.
def disposed_mice(request):
    # Get all disposed mice
    disposed_mice = DisposedMouse.objects.all()
    # Render the list of disposed mice to the template
    return render(request, 'disposed_mice.html', {'disposed_mice': disposed_mice})



def add_desktop_package_with_details(request):
    employees = Employee.objects.all()
    desktop_brands = Brand.objects.filter(is_desktop=True)
    keyboard_brands = Brand.objects.filter(is_keyboard=True)
    mouse_brands = Brand.objects.filter(is_mouse=True)
    monitor_brands = Brand.objects.filter(is_monitor=True)
    ups_brands = Brand.objects.filter(is_ups=True)

    context = {
        'desktop_brands': desktop_brands,
        'keyboard_brands': keyboard_brands,
        'mouse_brands': mouse_brands,
        'monitor_brands': monitor_brands,
        'ups_brands': ups_brands,
        'employees': employees
    }

    if request.method == 'POST':
        print("=== FORM DATA ===")
        for key, value in request.POST.items():
            print(f"{key}: {value}")

        context['post_data'] = request.POST
        try:
            with transaction.atomic():
                def safe_get_brand(field_name):
                    brand_id = request.POST.get(field_name)
                    if not brand_id or not brand_id.isdigit():
                        raise ValueError(f"Missing or invalid brand ID for {field_name}")
                    return get_object_or_404(Brand, id=brand_id)

                def safe_get_employee(field_name):
                    emp_id = request.POST.get(field_name)
                    if emp_id and emp_id.isdigit():
                        return get_object_or_404(Employee, id=emp_id)
                    return None

                desktop_package = Desktop_Package.objects.create(is_disposed=False)

                # Foreign Keys
                enduser = safe_get_employee('enduser_input')
                assetowner = safe_get_employee('assetowner_input')
                desktop_brand = safe_get_brand('desktop_brand_name')
                monitor_brand = safe_get_brand('monitor_brand')
                keyboard_brand = safe_get_brand('keyboard_brand')
                mouse_brand = safe_get_brand('mouse_brand')
                ups_brand = safe_get_brand('ups_brand')

                # Desktop
                desktop_details = DesktopDetails.objects.create(
                    desktop_package=desktop_package,
                    serial_no=request.POST.get('desktop_serial_no'),
                    computer_name=request.POST.get('computer_name_input'),
                    brand_name=desktop_brand,
                    model=request.POST.get('desktop_model'),
                    processor=request.POST.get('desktop_processor'),
                    memory=request.POST.get('desktop_memory'),
                    drive=request.POST.get('desktop_drive'),
                    desktop_Graphics=request.POST.get('desktop_Graphics'),
                    desktop_Graphics_Size=request.POST.get('desktop_Graphics_Size'),
                    desktop_OS=request.POST.get('desktop_OS'),
                    desktop_Office=request.POST.get('desktop_Office'),
                    desktop_OS_keys=request.POST.get('desktop_OS_keys'),
                    desktop_Office_keys=request.POST.get('desktop_Office_keys')
                )

                # Monitor
                MonitorDetails.objects.create(
                    desktop_package=desktop_package,
                    monitor_sn_db=request.POST.get('monitor_sn'),
                    monitor_brand_db=monitor_brand,
                    monitor_model_db=request.POST.get('monitor_model'),
                    monitor_size_db=request.POST.get('monitor_size')
                )

                # Keyboard
                KeyboardDetails.objects.create(
                    desktop_package=desktop_package,
                    keyboard_sn_db=request.POST.get('keyboard_sn'),
                    keyboard_brand_db=keyboard_brand,
                    keyboard_model_db=request.POST.get('keyboard_model')
                )

                # Mouse
                MouseDetails.objects.create(
                    desktop_package=desktop_package,
                    mouse_sn_db=request.POST.get('mouse_sn'),
                    mouse_brand_db=mouse_brand,
                    mouse_model_db=request.POST.get('mouse_model')
                )

                # UPS
                UPSDetails.objects.create(
                    desktop_package=desktop_package,
                    ups_sn_db=request.POST.get('ups_sn'),
                    ups_brand_db=ups_brand,
                    ups_model_db=request.POST.get('ups_model'),
                    ups_capacity_db=request.POST.get('ups_capacity')
                )

                # Documents
                DocumentsDetails.objects.create(
                    desktop_package=desktop_package,
                    docs_PAR=request.POST.get('par_number_input'),
                    docs_Propertyno=request.POST.get('property_number_input'),
                    docs_Acquisition_Type=request.POST.get('acquisition_type_input'),
                    docs_Value=request.POST.get('value_desktop_input'),
                    docs_Datereceived=request.POST.get('date_received_input'),
                    docs_Dateinspected=request.POST.get('date_inspected_input'),
                    docs_Supplier=request.POST.get('supplier_name_input'),
                    docs_Status=request.POST.get('status_desktop_input')
                )

                # User
                UserDetails.objects.create(
                    desktop_package=desktop_package,
                    user_Enduser=enduser,
                    user_Assetowner=assetowner
                )

                # PM Schedule
                if enduser and enduser.employee_office_section:
                    for schedule in PMSectionSchedule.objects.filter(section=enduser.employee_office_section):
                        PMScheduleAssignment.objects.get_or_create(
                            desktop_package=desktop_package,
                            pm_section_schedule=schedule
                        )

                print("✅ SUCCESS: Equipment saved successfully.")
                return redirect('success_add_page', desktop_id=desktop_package.id)
                # return redirect('desktop_details_view', package_id=desktop_package.id)
                
                

        except Exception as e:
            print("❌ Exception occurred:")
            traceback.print_exc()
            return render(request, 'add_desktop_package_with_details.html', {
                'error_message': str(e),
                'desktop_brands': desktop_brands,
                'keyboard_brands': keyboard_brands,
                'mouse_brands': mouse_brands,
                'monitor_brands': monitor_brands,
                'ups_brands': ups_brands,
                'employees': employees,
                'post_data': request.POST
            })

    return render(request, 'add_desktop_package_with_details.html', context)

#sa pag add ni sa desktop details, check if the computer name already exists in the database.
def check_computer_name(request):
    computer_name = request.GET.get('computer_name', '').strip()
    exists = DesktopDetails.objects.filter(computer_name=computer_name).exists()
    return JsonResponse({'exists': exists})






############### (RECENT at BASE)


def recent_it_equipment_and_count_base(request):
    recent_desktops = DesktopDetails.objects.select_related('desktop_package').order_by('-created_at')[:10]
    total_count = DesktopDetails.objects.count()
    disposed_count = DesktopDetails.objects.filter(is_disposed=True).count()
    disposal_trend = '100,90,95,110,120,130,125'  # static or computed

    return render(request, 'base.html', {
        'recent_desktops': recent_desktops,
        'total_count': total_count,
        'disposed_count': disposed_count,
        'disposal_trend': disposal_trend,
    })

#employees

def employee_list(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('firstName')
        middle_initial = request.POST.get('middleInitial', '')
        last_name = request.POST.get('lastName')
        position = request.POST.get('position', 'Unknown')
        office_section_id = request.POST.get('office_section')  # Now this is the foreign key
        status = request.POST.get('status')

        # Create new employee
        Employee.objects.create(
            employee_fname=first_name,
            employee_mname=middle_initial,
            employee_lname=last_name,
            employee_position=position,
            employee_office_section_id=office_section_id,
            employee_status=status
        )

        messages.success(request, f"✅ {first_name} {last_name} has been added successfully!")
        return redirect('employee_list')

    employees = Employee.objects.all()
    office_sections = OfficeSection.objects.all()
    return render(request, 'employees.html', {
        'employees': employees,
        'office_sections': office_sections
    })


def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        employee.employee_fname = request.POST.get('firstName')
        employee.employee_mname = request.POST.get('middleInitial')
        employee.employee_lname = request.POST.get('lastName')
        employee.employee_position = request.POST.get('position')
        employee.employee_office_section_id = request.POST.get('office_section')  # FK update
        employee.employee_status = request.POST.get('status')
        employee.save()

        messages.success(request, f"✅ {employee.employee_fname} {employee.employee_lname} has been updated!")
        return redirect('employee_list')

    office_sections = OfficeSection.objects.all()
    return render(request, 'edit_employee.html', {
        'employee': employee,
        'office_sections': office_sections
    })


def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        employee.delete()
        messages.success(request, f"✅ {employee.employee_fname} {employee.employee_lname} has been deleted!")
        return redirect('employee_list')

    the_messages = get_messages(request)
    
    return render(request, 'delete_employee.html', {
        'employee': employee,
        'the_messages': the_messages
    })

##update asset owner

def update_asset_owner(request, desktop_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                new_assetowner_id = request.POST.get('assetowner_input')
                if not new_assetowner_id:
                    return JsonResponse({'success': False, 'error': 'Please select an asset owner'})

                new_assetowner = get_object_or_404(Employee, id=new_assetowner_id)
                user_details = get_object_or_404(UserDetails, desktop_package__id=desktop_id)
                old_assetowner = user_details.user_Assetowner

                # Update asset owner
                user_details.user_Assetowner = new_assetowner
                user_details.save()

                # Save history record
                AssetOwnerChangeHistory.objects.create(
                    desktop_package=user_details.desktop_package,
                    old_assetowner=old_assetowner,
                    new_assetowner=new_assetowner,
                    changed_by=request.user,
                    changed_at=timezone.now()
                )

                return JsonResponse({'success': True})
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f"Error updating Asset Owner: {str(e)}"
            }, status=400)
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method.'
    }, status=405)
    
def update_end_user(request, desktop_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                new_enduser_id = request.POST.get('enduser_input')
                if not new_enduser_id:
                    return JsonResponse({'success': False, 'error': 'Please select an end user'})

                new_enduser = get_object_or_404(Employee, id=new_enduser_id)
                user_details = get_object_or_404(UserDetails, desktop_package__id=desktop_id)
                old_enduser = user_details.user_Enduser

                # Update end user
                user_details.user_Enduser = new_enduser
                user_details.save()

                # Save history record
                EndUserChangeHistory.objects.create(
                    desktop_package=user_details.desktop_package,
                    old_enduser=old_enduser,
                    new_enduser=new_enduser,
                    changed_by=request.user,
                    changed_at=timezone.now()
                )

                return JsonResponse({'success': True})
                
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f"Error updating End User: {str(e)}"
            }, status=400)
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method.'
    }, status=405)

# sa kadaghanan na dispose katung naay checkbox sa monitor, mouse, keyboard, ups, etc.
@require_POST
def dispose_desktop(request, desktop_id):
    desktop_details = get_object_or_404(DesktopDetails, id=desktop_id)
    desktop_package = desktop_details.desktop_package
    user_details = UserDetails.objects.filter(desktop_package=desktop_package).first()

    reason = request.POST.get("reason", "")

    # --- Create a DisposedDesktopDetail (main record) ---
    disposed_desktop = DisposedDesktopDetail.objects.create(
        desktop=desktop_details,
        serial_no=desktop_details.serial_no,
        brand_name=str(desktop_details.brand_name) if desktop_details.brand_name else None,
        model=desktop_details.model,
        asset_owner=user_details.user_Assetowner.full_name if user_details and user_details.user_Assetowner else None,
        reason=reason,
    )

    # --- Handle Monitors ---
    monitor_action = request.POST.get("monitor")
    if monitor_action == "dispose":
        for monitor in MonitorDetails.objects.filter(desktop_package=desktop_package, is_disposed=False):
            DisposedMonitor.objects.create(
                monitor_disposed_db=monitor,
                desktop_package=desktop_package,
                disposed_under=disposed_desktop,
                monitor_sn=monitor.monitor_sn_db,
                monitor_brand=str(monitor.monitor_brand_db) if monitor.monitor_brand_db else None,
                monitor_model=monitor.monitor_model_db,
                monitor_size=monitor.monitor_size_db,
                reason=reason,
            )
            monitor.is_disposed = True
            monitor.save()
        messages.success(request, "Monitor(s) disposed.")
    elif monitor_action == "salvage":
        for monitor in MonitorDetails.objects.filter(desktop_package=desktop_package, is_disposed=False):
            salvage_monitor_logic(monitor, notes="Salvaged instead of disposed")
            monitor.is_disposed = True
            monitor.save()
        messages.success(request, "Monitor(s) moved to Salvage Area.")

    # --- Handle Keyboards ---
    keyboard_action = request.POST.get("keyboard")
    if keyboard_action == "dispose":
        for kb in KeyboardDetails.objects.filter(desktop_package=desktop_package, is_disposed=False):
            DisposedKeyboard.objects.create(
                keyboard_dispose_db=kb,
                desktop_package=desktop_package,
                disposed_under=disposed_desktop,
            )
            kb.is_disposed = True
            kb.save()
        messages.success(request, "Keyboard(s) disposed.")
    elif keyboard_action == "salvage":
        for kb in KeyboardDetails.objects.filter(desktop_package=desktop_package, is_disposed=False):
            salvage_keyboard_logic(kb, notes="Salvaged instead of disposed")
            kb.is_disposed = True
            kb.save()
        messages.success(request, "Keyboard(s) moved to Salvage Area.")

    # --- Handle Mice ---
    mouse_action = request.POST.get("mouse")
    if mouse_action == "dispose":
        for mouse in MouseDetails.objects.filter(desktop_package=desktop_package, is_disposed=False):
            DisposedMouse.objects.create(
                mouse_db=mouse,
                desktop_package=desktop_package,
                disposed_under=disposed_desktop,
            )
            mouse.is_disposed = True
            mouse.save()
        messages.success(request, "Mouse(s) disposed.")
    elif mouse_action == "salvage":
        for mouse in MouseDetails.objects.filter(desktop_package=desktop_package, is_disposed=False):
            salvage_mouse_logic(mouse, notes="Salvaged instead of disposed")
            mouse.is_disposed = True
            mouse.save()
        messages.success(request, "Mouse(s) moved to Salvage Area.")

    # --- Handle UPS ---
    ups_action = request.POST.get("ups")
    if ups_action == "dispose":
        for ups in UPSDetails.objects.filter(desktop_package=desktop_package, is_disposed=False):
            DisposedUPS.objects.create(
                ups_db=ups,
                desktop_package=desktop_package,
                disposed_under=disposed_desktop,
            )
            ups.is_disposed = True
            ups.save()
        messages.success(request, "UPS disposed.")
    elif ups_action == "salvage":
        for ups in UPSDetails.objects.filter(desktop_package=desktop_package, is_disposed=False):
            salvage_ups_logic(ups, notes="Salvaged instead of disposed")
            ups.is_disposed = True
            ups.save()
        messages.success(request, "UPS moved to Salvage Area.")

    # --- Mark desktop itself disposed ---
    desktop_details.is_disposed = True
    desktop_details.save()
    desktop_package.is_disposed = True
    desktop_package.disposal_date = timezone.now()
    desktop_package.save()

    messages.success(request, "Desktop disposal process completed.")
    return redirect("desktop_details_view", package_id=desktop_package.id)



#salvaged area overview
def salvage_overview(request):
    # --- Monitors ---
    all_monitors = SalvagedMonitor.objects.select_related("reassigned_to").order_by("-salvage_date", "-id")
    seen_monitors = set()
    deduped_monitors = []
    for sm in all_monitors:
        if sm.monitor_sn in seen_monitors:
            continue
        seen_monitors.add(sm.monitor_sn)

        if sm.reassigned_to:
            dd = DesktopDetails.objects.filter(desktop_package=sm.reassigned_to).first()
            sm.reassigned_computer_name = dd.computer_name if dd else "Unknown"
        else:
            sm.reassigned_computer_name = None

        deduped_monitors.append(sm)

    # --- Keyboards ---
    all_keyboards = SalvagedKeyboard.objects.select_related("reassigned_to").order_by("-salvage_date", "-id")
    seen_keyboards = set()
    deduped_keyboards = []
    for kb in all_keyboards:
        if kb.keyboard_sn in seen_keyboards:
            continue
        seen_keyboards.add(kb.keyboard_sn)

        if kb.reassigned_to:
            dd = DesktopDetails.objects.filter(desktop_package=kb.reassigned_to).first()
            kb.reassigned_computer_name = dd.computer_name if dd else "Unknown"
        else:
            kb.reassigned_computer_name = None

        deduped_keyboards.append(kb)

    # --- Mice ---
    all_mice = SalvagedMouse.objects.select_related("reassigned_to").order_by("-salvage_date", "-id")
    seen_mice = set()
    deduped_mice = []
    for m in all_mice:
        if m.mouse_sn in seen_mice:
            continue
        seen_mice.add(m.mouse_sn)

        if m.reassigned_to:
            dd = DesktopDetails.objects.filter(desktop_package=m.reassigned_to).first()
            m.reassigned_computer_name = dd.computer_name if dd else "Unknown"
        else:
            m.reassigned_computer_name = None

        deduped_mice.append(m)

    # --- UPS ---
    all_ups = SalvagedUPS.objects.select_related("reassigned_to").order_by("-salvage_date", "-id")
    seen_ups = set()
    deduped_ups = []
    for u in all_ups:
        if u.ups_sn in seen_ups:
            continue
        seen_ups.add(u.ups_sn)

        if u.reassigned_to:
            dd = DesktopDetails.objects.filter(desktop_package=u.reassigned_to).first()
            u.reassigned_computer_name = dd.computer_name if dd else "Unknown"
        else:
            u.reassigned_computer_name = None

        deduped_ups.append(u)

    # --- Context ---
    context = {
        "salvaged_monitors": deduped_monitors,
        "salvaged_keyboards": deduped_keyboards,
        "salvaged_mice": deduped_mice,
        "salvaged_ups": deduped_ups,
    }
    return render(request, "salvage_overview.html", context)




def salvaged_monitor_detail(request, pk):
    monitor = get_object_or_404(SalvagedMonitor, pk=pk)

    # history of reassignments
    history = (
        SalvagedMonitorHistory.objects
        .filter(salvaged_monitor=monitor)
        .select_related("reassigned_to")
        .order_by("-reassigned_at")
    )
    for entry in history:
        dd = DesktopDetails.objects.filter(desktop_package=entry.reassigned_to).only("computer_name").first()
        entry.reassigned_computer_name = dd.computer_name if dd else "Unknown"

    # ✅ add status label + class
    if monitor.is_disposed:
        status_label = f"Disposed on {monitor.disposed_date.strftime('%Y-%m-%d %H:%M') if monitor.disposed_date else ''}"
        status_class = "danger"
    elif monitor.is_reassigned:
        status_label = f"Reassigned → {monitor.reassigned_to}"
        status_class = "secondary"
    else:
        status_label = "Available"
        status_class = "success"

    return render(request, "salvage/salvaged_monitor_detail.html", {
        "monitor": monitor,
        "history": history,
        "status_label": status_label,
        "status_class": status_class,
    })

def salvaged_keyboard_detail(request, pk):
    keyboard = get_object_or_404(SalvagedKeyboard, pk=pk)

    history = (
        SalvagedKeyboardHistory.objects
        .filter(salvaged_keyboard=keyboard)
        .select_related("reassigned_to")
        .order_by("-reassigned_at")
    )
    for entry in history:
        dd = DesktopDetails.objects.filter(desktop_package=entry.reassigned_to).only("computer_name").first()
        entry.reassigned_computer_name = dd.computer_name if dd else "Unknown"

    if keyboard.is_disposed:
        status_label = f"Disposed on {keyboard.disposed_date.strftime('%Y-%m-%d %H:%M') if keyboard.disposed_date else ''}"
        status_class = "danger"
    elif keyboard.is_reassigned:
        status_label = f"Reassigned → {keyboard.reassigned_to}"
        status_class = "secondary"
    else:
        status_label = "Available"
        status_class = "success"

    return render(request, "salvage/salvaged_keyboard_detail.html", {
        "keyboard": keyboard,
        "history": history,
        "status_label": status_label,
        "status_class": status_class,
    })


def salvaged_mouse_detail(request, pk):
    mouse = get_object_or_404(SalvagedMouse, pk=pk)

    history = (
        SalvagedMouseHistory.objects
        .filter(salvaged_mouse=mouse)
        .select_related("reassigned_to")
        .order_by("-reassigned_at")
    )
    for entry in history:
        dd = DesktopDetails.objects.filter(desktop_package=entry.reassigned_to).only("computer_name").first()
        entry.reassigned_computer_name = dd.computer_name if dd else "Unknown"

    if mouse.is_disposed:
        status_label = f"Disposed on {mouse.disposed_date.strftime('%Y-%m-%d %H:%M') if mouse.disposed_date else ''}"
        status_class = "danger"
    elif mouse.is_reassigned:
        status_label = f"Reassigned → {mouse.reassigned_to}"
        status_class = "secondary"
    else:
        status_label = "Available"
        status_class = "success"

    return render(request, "salvage/salvaged_mouse_detail.html", {
        "mouse": mouse,
        "history": history,
        "status_label": status_label,
        "status_class": status_class,
    })


def salvaged_ups_detail(request, pk):
    ups = get_object_or_404(SalvagedUPS, pk=pk)

    history = (
        SalvagedUPSHistory.objects
        .filter(salvaged_ups=ups)
        .select_related("reassigned_to")
        .order_by("-reassigned_at")
    )
    for entry in history:
        dd = DesktopDetails.objects.filter(desktop_package=entry.reassigned_to).only("computer_name").first()
        entry.reassigned_computer_name = dd.computer_name if dd else "Unknown"

    if ups.is_disposed:
        status_label = f"Disposed on {ups.disposed_date.strftime('%Y-%m-%d %H:%M') if ups.disposed_date else ''}"
        status_class = "danger"
    elif ups.is_reassigned:
        status_label = f"Reassigned → {ups.reassigned_to}"
        status_class = "secondary"
    else:
        status_label = "Available"
        status_class = "success"

    return render(request, "salvage/salvaged_ups_detail.html", {
        "ups": ups,
        "history": history,
        "status_label": status_label,
        "status_class": status_class,
    })


#brands
def add_brand(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        is_desktop = 'is_desktop' in request.POST
        is_keyboard = 'is_keyboard' in request.POST
        is_mouse = 'is_mouse' in request.POST
        is_monitor = 'is_monitor' in request.POST
        is_ups = 'is_ups' in request.POST

        if not Brand.objects.filter(name=name).exists():
            Brand.objects.create(
                name=name,
                is_desktop=is_desktop,
                is_keyboard=is_keyboard,
                is_mouse=is_mouse,
                is_monitor=is_monitor,
                is_ups=is_ups
            )
        return redirect('add_brand')

    brands = Brand.objects.all()
    return render(request, 'add_brand.html', {'brands': brands})

def edit_brand(request):
    if request.method == 'POST':
        brand_id = request.POST.get('id')
        brand = Brand.objects.get(pk=brand_id)
        brand.name = request.POST.get('name')
        brand.is_desktop = 'is_desktop' in request.POST
        brand.is_keyboard = 'is_keyboard' in request.POST
        brand.is_mouse = 'is_mouse' in request.POST
        brand.is_monitor = 'is_monitor' in request.POST
        brand.is_ups = 'is_ups' in request.POST
        brand.save()
    return redirect('add_brand')

#print
from django.templatetags.static import static

def generate_desktop_pdf(request, desktop_id):
    desktop_details = get_object_or_404(DesktopDetails, id=desktop_id)
    desktop_package = desktop_details.desktop_package

    # Current (non-disposed) components
    keyboard_details = KeyboardDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).first()
    mouse_details = MouseDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).first()
    monitor_details = MonitorDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).first()
    ups_details = UPSDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).first()

    # Documents
    documents_details = DocumentsDetails.objects.filter(desktop_package=desktop_package)

    # Current user assignment
    user_details = UserDetails.objects.filter(desktop_package=desktop_package).first()

    # ✅ History data
    asset_owner_history = AssetOwnerChangeHistory.objects.filter(desktop_package=desktop_package).order_by("-changed_at")
    enduser_history = EndUserChangeHistory.objects.filter(desktop_package=desktop_package).order_by("-changed_at")

    disposed_desktops = DisposedDesktopDetail.objects.filter(desktop__desktop_package=desktop_package).order_by("-date_disposed")
    disposed_monitors = DisposedMonitor.objects.filter(desktop_package=desktop_package).order_by("-disposal_date")
    disposed_keyboards = DisposedKeyboard.objects.filter(desktop_package=desktop_package).order_by("-disposal_date")
    disposed_mice = DisposedMouse.objects.filter(desktop_package=desktop_package).order_by("-disposal_date")
    disposed_ups = DisposedUPS.objects.filter(desktop_package=desktop_package).order_by("-disposal_date")

    # QR code
    qr_code_url = None
    if desktop_package.qr_code:
        qr_code_url = request.build_absolute_uri(desktop_package.qr_code.url)

    # ✅ Logo fix – build absolute URL
    logo_url = request.build_absolute_uri(static('img/logo.png'))

    # Render PDF template
    html_string = render_to_string('pdf_template.html', {
        'desktop_detailsx': desktop_details,
        'desktop_package': desktop_package,
        'keyboard_detailse': keyboard_details,
        'mouse_detailse': mouse_details,
        'monitor_detailse': monitor_details,
        'ups_detailse': ups_details,
        'user_details': user_details,
        'documents_detailse': documents_details,
        'qr_code_url': qr_code_url,
        'logo_url': logo_url,  # ✅ pass logo to template

        # ✅ Added history
        'asset_owner_history': asset_owner_history,
        'enduser_history': enduser_history,
        'disposed_desktops': disposed_desktops,
        'disposed_monitors': disposed_monitors,
        'disposed_keyboards': disposed_keyboards,
        'disposed_mice': disposed_mice,
        'disposed_ups': disposed_ups,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=desktop_{desktop_id}_details.pdf'
    HTML(string=html_string).write_pdf(response)
    return response


#export to excel
def export_desktop_packages_excel(request):
    template_path = 'static/excel_template/3f2e3faf-8c25-426f-b673-a2b5fb38e34a.xlsx'
    wb = load_workbook(template_path)
    ws = wb.active

    red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

    start_row = 9
    row = start_row

    desktops = DesktopDetails.objects.select_related('desktop_package', 'brand_name').all()

    for i, desktop in enumerate(desktops, start=1):
        dp = desktop.desktop_package
        doc = DocumentsDetails.objects.filter(desktop_package=dp).first()
        user = UserDetails.objects.filter(desktop_package=dp).first()

        status = "Active" if not desktop.is_disposed else "Disposed"

        ws[f'A{row}'] = f"{i}a"
        ws[f'B{row}'] = "Desktop"
        ws[f'C{row}'] = doc.docs_Acquisition_Type if doc else ''
        ws[f'D{row}'] = desktop.processor
        ws[f'E{row}'] = desktop.memory
        ws[f'F{row}'] = desktop.drive
        ws[f'G{row}'] = desktop.desktop_OS
        ws[f'H{row}'] = desktop.desktop_Office
        ws[f'I{row}'] = status
        ws[f'J{row}'] = doc.docs_PAR if doc else ''
        ws[f'K{row}'] = desktop.serial_no
        ws[f'L{row}'] = doc.docs_Propertyno if doc else ''
        ws[f'M{row}'] = desktop.model
        ws[f'N{row}'] = desktop.brand_name.name if desktop.brand_name else ''
        ws[f'O{row}'] = doc.docs_Value if doc else ''
        ws[f'P{row}'] = f"{user.user_Enduser.employee_fname} {user.user_Enduser.employee_lname}" if user and user.user_Enduser else ''
        ws[f'Q{row}'] = user.user_Enduser.employee_position if user and user.user_Enduser else ''
        ws[f'R{row}'] = user.user_Enduser.employee_office_section.name if user and user.user_Enduser and user.user_Enduser.employee_office_section else ''
        ws[f'S{row}'] = "Region VIII"
        ws[f'T{row}'] = "Leyte 4th DEO"
        ws[f'U{row}'] = f"{user.user_Assetowner.employee_fname} {user.user_Assetowner.employee_lname}" if user and user.user_Assetowner else ''
        ws[f'V{row}'] = doc.docs_Datereceived if doc else ''
        ws[f'W{row}'] = doc.docs_Supplier if doc else ''
        ws[f'X{row}'] = doc.docs_Dateinspected if doc else ''
        ws[f'Y{row}'] = desktop.computer_name
        ws[f'Z{row}'] = status

        if status == "Disposed":
            for col in range(1, 27):
                ws.cell(row=row, column=col).fill = red_fill

        row += 1

        # Components
        components = [
            ('Monitor', MonitorDetails.objects.filter(desktop_package=dp), 'b'),
            ('Keyboard', KeyboardDetails.objects.filter(desktop_package=dp), 'c'),
            ('Mouse', MouseDetails.objects.filter(desktop_package=dp), 'd'),
            ('UPS', UPSDetails.objects.filter(desktop_package=dp), 'e'),
        ]

        for label, items, suffix in components:
            for item in items:
                status = "Active" if not item.is_disposed else "Disposed"

                ws[f'A{row}'] = f"{i}{suffix}"
                ws[f'B{row}'] = label
                ws[f'C{row}'] = doc.docs_Acquisition_Type if doc else ''
                ws[f'D{row}'] = ws[f'E{row}'] = ws[f'F{row}'] = ws[f'G{row}'] = ws[f'H{row}'] = "N/A"
                ws[f'I{row}'] = status
                ws[f'J{row}'] = doc.docs_PAR if doc else ''
                ws[f'L{row}'] = doc.docs_Propertyno if doc else ''
                ws[f'O{row}'] = doc.docs_Value if doc else ''
                ws[f'P{row}'] = f"{user.user_Enduser.employee_fname} {user.user_Enduser.employee_lname}" if user and user.user_Enduser else ''
                ws[f'Q{row}'] = user.user_Enduser.employee_position if user and user.user_Enduser else ''
                ws[f'R{row}'] = user.user_Enduser.employee_office_section.name if user and user.user_Enduser and user.user_Enduser.employee_office_section else ''
                ws[f'S{row}'] = "Region VIII"
                ws[f'T{row}'] = "Leyte 4th DEO"
                ws[f'U{row}'] = f"{user.user_Assetowner.employee_fname} {user.user_Assetowner.employee_lname}" if user and user.user_Assetowner else ''
                ws[f'V{row}'] = doc.docs_Datereceived if doc else ''
                ws[f'W{row}'] = doc.docs_Supplier if doc else ''
                ws[f'X{row}'] = doc.docs_Dateinspected if doc else ''
                ws[f'Y{row}'] = "N/A"
                ws[f'Z{row}'] = status

                # Component-specific fields
                if label == "Monitor":
                    ws[f'K{row}'] = item.monitor_sn_db
                    ws[f'M{row}'] = item.monitor_model_db
                    ws[f'N{row}'] = item.monitor_brand_db.name if item.monitor_brand_db else ''
                elif label == "Keyboard":
                    ws[f'K{row}'] = item.keyboard_sn_db
                    ws[f'M{row}'] = item.keyboard_model_db
                    ws[f'N{row}'] = item.keyboard_brand_db.name if item.keyboard_brand_db else ''
                elif label == "Mouse":
                    ws[f'K{row}'] = item.mouse_sn_db
                    ws[f'M{row}'] = item.mouse_model_db
                    ws[f'N{row}'] = item.mouse_brand_db.name if item.mouse_brand_db else ''
                elif label == "UPS":
                    ws[f'K{row}'] = item.ups_sn_db
                    ws[f'M{row}'] = item.ups_model_db
                    ws[f'N{row}'] = item.ups_brand_db.name if item.ups_brand_db else ''

                if status == "Disposed":
                    for col in range(1, 27):
                        ws.cell(row=row, column=col).fill = red_fill

                row += 1

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=desktop_bundle_export_{datetime.today().date()}.xlsx'
    return response

def add_maintenance(request, desktop_id):
    desktop = get_object_or_404(Desktop_Package, id=desktop_id)

    if request.method == 'POST':
        maintenance_date = request.POST.get('maintenance_date')
        performed_by = request.POST.get('performed_by')
        notes = request.POST.get('notes')

        # Convert maintenance_date to a Python date object
        maintenance_date_obj = datetime.strptime(maintenance_date, '%Y-%m-%d').date()
        next_schedule = maintenance_date_obj + timedelta(days=30)

        PreventiveMaintenance.objects.create(
            desktop_package=desktop,
            maintenance_date=maintenance_date,
            next_schedule=next_schedule,
            performed_by=performed_by,
            notes=notes,
            is_completed=True
        )
        return redirect('maintenance_history', desktop_id=desktop.id)

    return render(request, 'maintenance/add_maintenance.html', {'desktop': desktop})


def maintenance_history_view(request, desktop_id):
    # Get the desktop package and related details
    desktop = get_object_or_404(Desktop_Package, pk=desktop_id)
    desktop_details = DesktopDetails.objects.filter(desktop_package=desktop).first()
    user_details = UserDetails.objects.filter(desktop_package=desktop).first()

    # Completed maintenance history
    maintenance_history = (
        PreventiveMaintenance.objects
        .filter(desktop_package=desktop)
        .select_related('pm_schedule_assignment__pm_section_schedule__quarter_schedule')
        .order_by('date_accomplished')
    )

    # Get the latest completed PM (if any)
    latest_pm = maintenance_history.last()

    # Current (pending) PM assignments
    current_pm_schedule = PMScheduleAssignment.objects.filter(
        desktop_package=desktop
    ).select_related(
        'pm_section_schedule__quarter_schedule',
        'pm_section_schedule__section'
    ).order_by(
        'pm_section_schedule__quarter_schedule__year',
        'pm_section_schedule__quarter_schedule__quarter'
    )

    return render(request, 'maintenance/history.html', {
        'desktop': desktop,
        'desktop_details': desktop_details,
        'user_details': user_details,
        'maintenance_history': maintenance_history,
        'maintenance_records': maintenance_history,
        'pm': latest_pm,
        'current_pm_schedule': current_pm_schedule,  # New table data
    })

# def get_schedule_date_range(request, quarter_id):
#     schedule = PMSectionSchedule.objects.filter(quarter_schedule_id=quarter_id).first()
#     if schedule:
#         return JsonResponse({
#             "start_date": schedule.start_date.strftime("%Y-%m-%d"),
#             "end_date": schedule.end_date.strftime("%Y-%m-%d")
#         })
#     return JsonResponse({}, status=404)

def get_schedule_date_range(request, quarter_id, section_id):
    try:
        schedule = PMSectionSchedule.objects.get(
            quarter_schedule_id=quarter_id,
            section_id=section_id
        )
        return JsonResponse({
            "start_date": schedule.start_date.strftime("%Y-%m-%d"),
            "end_date": schedule.end_date.strftime("%Y-%m-%d")
        })
    except PMSectionSchedule.DoesNotExist:
        return JsonResponse({"error": "Schedule not found"}, status=404)



# This function handles the checklist for preventive maintenance of a desktop package.


def checklist(request, desktop_id):
    desktop = get_object_or_404(Desktop_Package, pk=desktop_id)

    quarter_schedules = QuarterSchedule.objects.all().order_by('-year', 'quarter')
     # ❌ If desktop is disposed, block PM and show message
    is_disposed = not DesktopDetails.objects.filter(desktop_package=desktop, is_disposed=False).exists()

    if is_disposed:
        messages.error(request, "❌ Desktop was already disposed and cannot be PM anymore.")
        return redirect('desktop_details_view', package_id=desktop.id)  # Make sure this matches your URL name
    
     # ❌ Block if no schedule assigned
    has_schedule = PMScheduleAssignment.objects.filter(desktop_package=desktop).exists()
    if not has_schedule:
        messages.error(request, "⚠ Please add a PM schedule first before conducting Preventive Maintenance.")
        return redirect('desktop_details_view', package_id=desktop.id)


    checklist_labels = {
        1: "Check if configured and connected to the DPWH domain",
        2: "Check if able to access the intranet services",
        3: "Check if installed with anti-virus software authorized by IMS",
        4: "Check if anti-virus definition files are up-to-date",
        5: "Perform full virus scan using updated virus removal tool",
        6: "Remove all un-authorized software installations",
        7: "Remove all un-authorized files (e.g. movies)",
        8: "Check working condition of hardware devices/components",
        9: "Clean hardware and components, and organize cables",
    }

    user_details = UserDetails.objects.filter(desktop_package=desktop).first()
    office = user_details.user_Enduser.employee_office_section if user_details and user_details.user_Enduser else ''
    end_user = f"{user_details.user_Enduser.employee_fname} {user_details.user_Enduser.employee_lname}" if user_details and user_details.user_Enduser else ''
    desktop_details = DesktopDetails.objects.filter(desktop_package=desktop).first()
    
    # ✅ NEW: extract the section_id safely
    section_id = (
        user_details.user_Enduser.employee_office_section.id
        if user_details and user_details.user_Enduser and user_details.user_Enduser.employee_office_section
        else None
    )
    

    if request.method == "POST":
        quarter_id = request.POST.get("quarter_schedule_id")
        date_accomplished = request.POST.get("date_accomplished")
        quarter = QuarterSchedule.objects.get(id=quarter_id) if quarter_id else None

        # ✅ Check if PM was already conducted for this quarter and desktop
        already_done = PreventiveMaintenance.objects.filter(
            desktop_package=desktop,
            pm_schedule_assignment__pm_section_schedule__quarter_schedule=quarter
        ).exists()

        if already_done:
            messages.warning(request, f"❌ for {quarter.get_quarter_display()} {quarter.year} is already conducted.")
            return redirect('checklist', desktop_id=desktop.id)

        matched_schedule = PMScheduleAssignment.objects.filter(
            desktop_package=desktop,
            pm_section_schedule__quarter_schedule=quarter,
            pm_section_schedule__start_date__lte=date_accomplished,
            pm_section_schedule__end_date__gte=date_accomplished
        ).first()

        # Auto-create schedule assignment if not found
        if not matched_schedule and quarter:
            section = user_details.user_Enduser.employee_office_section if user_details and user_details.user_Enduser else None
            pm_section_schedule = PMSectionSchedule.objects.filter(
                quarter_schedule=quarter,
                section=section
            ).first()

            # Auto-create PMSectionSchedule if missing
            if not pm_section_schedule and section:
                pm_section_schedule = PMSectionSchedule.objects.create(
                    quarter_schedule=quarter,
                    section=section,
                    start_date=date_accomplished,
                    end_date=date_accomplished,
                    notes="Auto-created from checklist"
                )

            # Auto-create PMScheduleAssignment
            if pm_section_schedule:
                matched_schedule = PMScheduleAssignment.objects.create(
                    desktop_package=desktop,
                    pm_section_schedule=pm_section_schedule,
                    is_completed=True,
                    remarks="Auto-assigned via checklist"
                )

        # Create PreventiveMaintenance record
        pm = PreventiveMaintenance.objects.create(
            desktop_package=desktop,
            pm_schedule_assignment=matched_schedule,
            office=office,
            end_user=end_user,
            maintenance_date=timezone.now().date(),
            date_accomplished=date_accomplished,
            performed_by=request.user.get_full_name() if request.user.is_authenticated else "Technician",
            is_completed=True,
            **{f"task_{i}": request.POST.get(f"task_{i}") == "on" for i in range(1, 10)},
            **{f"note_{i}": request.POST.get(f"note_{i}", "") for i in range(1, 10)},
        )

        # Save checklist items
        for i in range(1, 10):
            MaintenanceChecklistItem.objects.create(
                maintenance=pm,
                item_text=checklist_labels[i],
                is_checked=request.POST.get(f"task_{i}") == "on"
            )

        if matched_schedule:
            matched_schedule.is_completed = True
            matched_schedule.remarks = "Checklist completed"
            matched_schedule.save()

        return redirect('maintenance_history', desktop_id=desktop.id)

    return render(request, 'maintenance/checklist.html', {
        'desktop': desktop,
        'desktop_details': desktop_details,
        'checklist_labels': checklist_labels,
        'office': office,
        'end_user': end_user,
        'range': range(1, 10),
        'quarter_schedules': quarter_schedules,
        'section_id': section_id,  # ✅ pass section_id to template
    })


def generate_pm_excel_report(request, pm_id):
    pythoncom.CoInitialize()

    # Get preventive maintenance and related desktop details
    pm = get_object_or_404(PreventiveMaintenance, pk=pm_id)
    desktop_details = DesktopDetails.objects.filter(desktop_package=pm.desktop_package).first()

    # Define paths
    template_path = os.path.join(settings.BASE_DIR, 'static', 'excel_template', 'PM checklist.xlsx')
    output_xlsx_path = os.path.join(settings.MEDIA_ROOT, f'PM_Report_{pm.id}.xlsx')
    output_pdf_path = os.path.join(settings.MEDIA_ROOT, f'PM_Report_{pm.id}.pdf')

    # Load Excel template
    wb = load_workbook(template_path)
    ws = wb.active

    # Fill basic info
    ws['C7'] = pm.office or ''
    ws['C8'] = desktop_details.computer_name if desktop_details else ''
    ws['C9'] = pm.end_user or ''
    ws['C10'] = str(pm.date_accomplished or '')

    # Fill checklist: checkmarks and notes
    for i in range(1, 10):
        # Checkmark (✓) in column D
        is_checked = getattr(pm, f"task_{i}", False)
        check_cell = f'D{13 + i}'  # D14 to D22
        ws[check_cell] = "✓" if is_checked else ""

        # Notes in column E
        note_value = getattr(pm, f'note_{i}', '')
        note_cell = f'E{13 + i}'  # E14 to E22
        ws[note_cell] = note_value

    # Save updated Excel file
    wb.save(output_xlsx_path)

    # Convert to PDF using Excel COM
    excel = Dispatch("Excel.Application")
    excel.Visible = False
    wb_com = excel.Workbooks.Open(output_xlsx_path)
    wb_com.ExportAsFixedFormat(0, output_pdf_path)  # 0 = PDF format
    wb_com.Close(False)
    excel.Quit()
    pythoncom.CoUninitialize()

    # Return the PDF file as download
    return FileResponse(open(output_pdf_path, 'rb'), as_attachment=True, filename=f'PM_Report_{pm.id}.pdf')



def pm_overview_view(request):
    pm_assignments = PMScheduleAssignment.objects.select_related(
        'desktop_package',
        'pm_section_schedule__quarter_schedule',
        'pm_section_schedule__section'
    ).all()

    # Attach computer_name for each assignment
    for assignment in pm_assignments:
        desktop_detail = DesktopDetails.objects.filter(desktop_package=assignment.desktop_package).first()
        assignment.computer_name = desktop_detail.computer_name if desktop_detail else "N/A"

    # Annotate computer_name for desktops (for dropdown)
    desktops = list(Desktop_Package.objects.prefetch_related(
        Prefetch('user_details', queryset=UserDetails.objects.select_related('user_Enduser__employee_office_section'))
    ))

    for desktop in desktops:
        desktop_detail = DesktopDetails.objects.filter(desktop_package=desktop).first()
        desktop.computer_name_display = desktop_detail.computer_name if desktop_detail else "N/A"

    schedules = PMSectionSchedule.objects.select_related('section', 'quarter_schedule')
    schedules_by_section = {}
    for s in schedules:
        section_name = s.section.name if s.section else 'Other'
        schedules_by_section.setdefault(section_name, []).append(s)

    quarters = QuarterSchedule.objects.all().order_by('-year', 'quarter')
    sections = OfficeSection.objects.all()

    return render(request, 'maintenance/overview.html', {
        'pm_assignments': pm_assignments,
        'desktops': desktops,
        'schedules': schedules,
        'schedules_by_section': schedules_by_section,
        'quarters': quarters,
        'sections': sections,
    })

  


def assign_pm_schedule(request):
    if request.method == 'POST':
        desktop_id = request.POST.get('desktop_package_id')
        schedule_id = request.POST.get('schedule_id')

        desktop = get_object_or_404(Desktop_Package, pk=desktop_id)
        schedule = get_object_or_404(PMSectionSchedule, pk=schedule_id)

        if PMScheduleAssignment.objects.filter(desktop_package=desktop, pm_section_schedule=schedule).exists():
            messages.warning(request, "This desktop is already assigned to this schedule.")
            return redirect('pm_overview')

        PMScheduleAssignment.objects.create(desktop_package=desktop, pm_section_schedule=schedule)
        messages.success(request, "Schedule successfully assigned.")
        return redirect('pm_overview')


def section_schedule_list_view(request):
    schedules = PMSectionSchedule.objects.select_related('quarter_schedule', 'section').order_by('-start_date')
    quarters = QuarterSchedule.objects.all().order_by('-year')
    sections = OfficeSection.objects.all().order_by('name')

    if request.method == 'POST':
        quarter_id = request.POST.get('quarter_schedule_id')
        section_id = request.POST.get('section_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        quarter = get_object_or_404(QuarterSchedule, pk=quarter_id)
        section = get_object_or_404(OfficeSection, pk=section_id)

        # Prevent duplicate schedule for same section and quarter
        if PMSectionSchedule.objects.filter(quarter_schedule=quarter, section=section).exists():
            messages.warning(request, f"A schedule already exists for {section.name} in {quarter.get_quarter_display()} {quarter.year}.")
            return redirect('section_schedule_list')

        # Create schedule if not existing
        PMSectionSchedule.objects.create(
            quarter_schedule=quarter,
            section=section,
            start_date=start_date,
            end_date=end_date,
        )

        messages.success(request, "Schedule added successfully.")
        return redirect('section_schedule_list')

    return render(request, 'maintenance/section_schedule_list.html', {
        'schedules': schedules,
        'quarters': quarters,
        'sections': sections,
    })

# # View to handle office section list and addition    
def office_section_list(request):
    if request.method == 'POST':
        section_name = request.POST.get('section_name')
        if section_name:
            if not OfficeSection.objects.filter(name__iexact=section_name).exists():
                OfficeSection.objects.create(name=section_name)
                messages.success(request, f'Office Section "{section_name}" added successfully.')
            else:
                messages.error(request, f'Office Section "{section_name}" already exists.')
        return redirect('office_section_list')  # replace with your URL name

    office_sections = OfficeSection.objects.all()
    return render(request, 'office_section_list.html', {'office_sections': office_sections})



#disposal overview page

def disposal_overview(request):
    # Desktops
    latest_desktops = (
        DisposedDesktopDetail.objects
        .values("serial_no")
        .annotate(latest_id=Max("id"))
    )
    desktops = DisposedDesktopDetail.objects.filter(id__in=[row["latest_id"] for row in latest_desktops])

    # Monitors
    latest_monitors = (
        DisposedMonitor.objects
        .values("monitor_sn")
        .annotate(latest_id=Max("id"))
    )
    monitors = DisposedMonitor.objects.filter(id__in=[row["latest_id"] for row in latest_monitors])

    # Keyboards
    latest_keyboards = (
        DisposedKeyboard.objects
        .values("keyboard_dispose_db__keyboard_sn_db")
        .annotate(latest_id=Max("id"))
    )
    keyboards = DisposedKeyboard.objects.filter(id__in=[row["latest_id"] for row in latest_keyboards])

    # Mice
    latest_mice = (
        DisposedMouse.objects
        .values("mouse_db__mouse_sn_db")
        .annotate(latest_id=Max("id"))
    )
    mice = DisposedMouse.objects.filter(id__in=[row["latest_id"] for row in latest_mice])

    # UPS
    latest_ups = (
        DisposedUPS.objects
        .values("ups_db__ups_sn_db")
        .annotate(latest_id=Max("id"))
    )
    ups_list = DisposedUPS.objects.filter(id__in=[row["latest_id"] for row in latest_ups])

    categories = [
        {"label": "Disposed Desktops", "items": desktops, "category": "desktop"},
        {"label": "Disposed Monitors", "items": monitors, "category": "monitor"},
        {"label": "Disposed Keyboards", "items": keyboards, "category": "keyboard"},
        {"label": "Disposed Mice", "items": mice, "category": "mouse"},
        {"label": "Disposed UPS", "items": ups_list, "category": "ups"},
    ]

    return render(request, "disposal/disposal_overview.html", {"categories": categories})

def disposal_history(request):
    desktops = DisposedDesktopDetail.objects.all().order_by("-date_disposed")
    monitors = DisposedMonitor.objects.all().order_by("-disposal_date")
    keyboards = DisposedKeyboard.objects.all().order_by("-disposal_date")
    mice = DisposedMouse.objects.all().order_by("-disposal_date")
    ups_list = DisposedUPS.objects.all().order_by("-disposal_date")

    categories = [
        {"label": "Desktop Disposal History", "items": desktops, "category": "desktop"},
        {"label": "Monitor Disposal History", "items": monitors, "category": "monitor"},
        {"label": "Keyboard Disposal History", "items": keyboards, "category": "keyboard"},
        {"label": "Mouse Disposal History", "items": mice, "category": "mouse"},
        {"label": "UPS Disposal History", "items": ups_list, "category": "ups"},
    ]

    return render(request, "disposal/disposal_history.html", {"categories": categories})





#Dashboard chart view for disposal overview
# Map each model to the correct disposal date field


def get_monthly_count(model, label_name, date_field):
    data = (
        model.objects
        .annotate(month=TruncMonth(date_field))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    result = {}
    for entry in data:
        month_label = entry['month'].strftime("%b %Y")
        result[month_label] = entry['count']

    return label_name, result

def get_daily_count(model, label_name, date_field):
    data = (
        model.objects
        .annotate(day=TruncDay(date_field))  # ← Group by day
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    result = {}
    for entry in data:
        day_label = entry['day'].strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
        result[day_label] = entry['count']

    return label_name, result



#http://127.0.0.1:8000/dashboard/chart/
def dashboard_view_chart(request):
    all_data = []

    models = [
        (DisposedDesktopDetail, 'Desktop', 'date_disposed'),
        (DisposedMonitor, 'Monitor', 'disposal_date'),
        (DisposedKeyboard, 'Keyboard', 'disposal_date'),
        (DisposedMouse, 'Mouse', 'disposal_date'),
        (DisposedUPS, 'UPS', 'disposal_date'),
    ]

    for model, label, date_field in models:
        category, data = get_daily_count(model, label, date_field)
        all_data.append({
            'label': category,
            'data': list(data.values()),
            'labels': list(data.keys()),
        })

    return render(request, 'dashboard_chart.html', {'chart_data': all_data})


#photo upload for monitor
@require_POST
def upload_monitor_photo(request, monitor_id):
    monitor = get_object_or_404(MonitorDetails, id=monitor_id)
    if 'photo' in request.FILES:
        monitor.monitor_photo = request.FILES['photo']
        monitor.save()
    return redirect(f'/desktop_details_view/{monitor.desktop_package.id}/#pills-monitor')


def export_salvage_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Salvaged Equipment"

    headers = [
        "Category", "SN", "Brand", "Model", "Size/Capacity",
        "Computer Name", "Asset Owner", "Date Salvaged", "Notes", "Status"
    ]
    ws.append(headers)

    def get_asset_owner(desktop_package):
        if not desktop_package:
            return ""
        user = UserDetails.objects.filter(desktop_package=desktop_package).first()
        if user and user.user_Assetowner:
            return user.user_Assetowner.full_name
        return ""

    def fmt_date(dt):
        if not dt:
            return ""
        try:
            return dt.strftime("%Y-%m-%d %H:%M")  # works if datetime
        except Exception:
            return dt.strftime("%Y-%m-%d")        # fallback for date

    # Monitors
    for m in DisposedMonitor.objects.all():
        computer_name = m.desktop_package.computer_name if m.desktop_package else ""
        asset_owner = get_asset_owner(m.desktop_package)
        ws.append([
            "Monitor", m.monitor_sn, m.monitor_brand, m.monitor_model, m.monitor_size,
            computer_name, asset_owner,
            fmt_date(m.disposal_date),
            m.reason or "", "Disposed"
        ])

    # Keyboards
    for k in DisposedKeyboard.objects.all():
        computer_name = k.desktop_package.computer_name if k.desktop_package else ""
        asset_owner = get_asset_owner(k.desktop_package)
        ws.append([
            "Keyboard",
            k.keyboard_dispose_db.keyboard_sn_db,
            str(k.keyboard_dispose_db.keyboard_brand_db),
            k.keyboard_dispose_db.keyboard_model_db,
            "",
            computer_name, asset_owner,
            fmt_date(k.disposal_date),
            "", "Disposed"
        ])

    # Mice
    for mo in DisposedMouse.objects.all():
        computer_name = mo.desktop_package.computer_name if mo.desktop_package else ""
        asset_owner = get_asset_owner(mo.desktop_package)
        ws.append([
            "Mouse",
            mo.mouse_db.mouse_sn_db,
            str(mo.mouse_db.mouse_brand_db),
            mo.mouse_db.mouse_model_db,
            "",
            computer_name, asset_owner,
            fmt_date(mo.disposal_date),
            "", "Disposed"
        ])

    # UPS
    for u in DisposedUPS.objects.all():
        computer_name = u.desktop_package.computer_name if u.desktop_package else ""
        asset_owner = get_asset_owner(u.desktop_package)
        ws.append([
            "UPS",
            u.ups_db.ups_sn_db,
            str(u.ups_db.ups_brand_db),
            u.ups_db.ups_model_db,
            u.ups_db.ups_capacity_db,
            computer_name, asset_owner,
            fmt_date(u.disposal_date),
            "", "Disposed"
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=salvaged_equipment.xlsx'
    return response



def print_salvage_overview(request):
    salvaged_monitors = DisposedMonitor.objects.all()
    salvaged_keyboards = DisposedKeyboard.objects.all()
    salvaged_mice = DisposedMouse.objects.all()
    salvaged_ups = DisposedUPS.objects.all()

    html_string = render_to_string("salvage/print_salvage.html", {
        "salvaged_monitors": salvaged_monitors,
        "salvaged_keyboards": salvaged_keyboards,
        "salvaged_mice": salvaged_mice,
        "salvaged_ups": salvaged_ups,
    })

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename=salvage_overview.pdf'
    HTML(string=html_string).write_pdf(response)
    return response



#the dashboard

# views_dashboard_snippet.py — paste this into your views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from calendar import month_abbr

# Import your models below — adjust names if your app uses different model class names
from .models import (
    Desktop_Package, DesktopDetails, MonitorDetails, KeyboardDetails, MouseDetails, UPSDetails,
    DisposedDesktopDetail, DisposedMonitor, DisposedKeyboard, DisposedMouse, DisposedUPS,
    PMSectionSchedule, PMScheduleAssignment, EndUserChangeHistory, AssetOwnerChangeHistory
)

def _months_back_labels(n=6):
    today = timezone.now().date()
    year = today.year
    month = today.month
    labels = []
    for _ in range(n):
        labels.append(f"{month_abbr[month]} {year}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    labels.reverse()
    return labels

def _monthly_counts_qs(qs, date_field, months=6):
    data = (qs.annotate(m=TruncMonth(date_field))
              .values('m')
              .annotate(c=Count('id'))
              .order_by('m'))
    # Map to 'Mon YYYY' -> count
    map_counts = {f"{month_abbr[row['m'].month]} {row['m'].year}": row['c'] for row in data if row['m']}
    labels = _months_back_labels(months)
    return labels, [map_counts.get(lbl, 0) for lbl in labels]

@login_required
def dashboard_pro(request):
    # KPIs
    total_packages = Desktop_Package.objects.count()
    active_packages = Desktop_Package.objects.filter(is_disposed=False).count()
    disposed_all = (
        DisposedDesktopDetail.objects.count() +
        DisposedMonitor.objects.count() +
        DisposedKeyboard.objects.count() +
        DisposedMouse.objects.count() +
        DisposedUPS.objects.count()
    )
    pm_pending = PMScheduleAssignment.objects.filter(is_completed=False).count()

    # Trend (last 3 months)
    months = 3
    lbls, desktop_series = _monthly_counts_qs(DisposedDesktopDetail.objects.all(), 'date_disposed', months)
    _, mouse_series = _monthly_counts_qs(DisposedMouse.objects.all(), 'disposal_date', months)
    _, keyboard_series = _monthly_counts_qs(DisposedKeyboard.objects.all(), 'disposal_date', months)
    _, ups_series = _monthly_counts_qs(DisposedUPS.objects.all(), 'disposal_date', months)  

    # Disposed by category (all-time)
    disposed_labels = ["Desktop", "Monitor", "Keyboard", "Mouse", "UPS"]
    disposed_data = [
        DisposedDesktopDetail.objects.count(),
        DisposedMonitor.objects.count(),
        DisposedKeyboard.objects.count(),
        DisposedMouse.objects.count(),
        DisposedUPS.objects.count(),
    ]

    # Active vs Disposed by category
    stack_labels = ["Desktop", "Monitor", "Keyboard", "Mouse", "UPS"]
    active_counts = [
        DesktopDetails.objects.filter(is_disposed=False).count(),
        MonitorDetails.objects.filter(is_disposed=False).count(),
        KeyboardDetails.objects.filter(is_disposed=False).count(),
        MouseDetails.objects.filter(is_disposed=False).count(),
        UPSDetails.objects.filter(is_disposed=False).count(),
    ]
    disposed_counts = [
        DesktopDetails.objects.filter(is_disposed=True).count(),
        MonitorDetails.objects.filter(is_disposed=True).count(),
        KeyboardDetails.objects.filter(is_disposed=True).count(),
        MouseDetails.objects.filter(is_disposed=True).count(),
        UPSDetails.objects.filter(is_disposed=True).count(),
    ]

    # Recent items
    recent = DesktopDetails.objects.filter(is_disposed=False).order_by('-created_at')[:10]

    # Upcoming PM (next 7 days)
    today = timezone.now().date()
    next_week = today + timedelta(days=7)
    upcoming = (PMSectionSchedule.objects
                .filter(start_date__lte=next_week, end_date__gte=today)
                .select_related('section'))
    pm_upcoming = []
    for s in upcoming:
        assignment = PMScheduleAssignment.objects.filter(pm_section_schedule=s).select_related('desktop_package').first()
        comp = "—"
        if assignment and assignment.desktop_package_id:
            dd = DesktopDetails.objects.filter(desktop_package=assignment.desktop_package).first()
            comp = dd.computer_name if dd else "—"
        pm_upcoming.append({
            "section": s.section.name if getattr(s, 'section', None) else "—",
            "range": f"{s.start_date} – {s.end_date}",
            "computer_name": comp,
        })

    # Audit trail (10 latest changes)
    enduser = EndUserChangeHistory.objects.select_related('desktop_package','new_enduser','old_enduser').order_by('-changed_at')[:5]
    assetown = AssetOwnerChangeHistory.objects.select_related('desktop_package','new_assetowner','old_assetowner').order_by('-changed_at')[:5]
    audit = []
    for e in enduser:
        audit.append({
            "type": "End User",
            "when": e.changed_at.strftime("%Y-%m-%d %H:%M"),
            "text": f"Desktop Package #{e.desktop_package_id}: <strong>{e.old_enduser or 'None'}</strong> → <strong>{e.new_enduser}</strong>",
        })
    for a in assetown:
        audit.append({
            "type": "Asset Owner",
            "when": a.changed_at.strftime("%Y-%m-%d %H:%M"),
            "text": f"Desktop Package #{a.desktop_package_id}: <strong>{a.old_assetowner or 'None'}</strong> → <strong>{a.new_assetowner}</strong>",
        })
    audit = sorted(audit, key=lambda x: x["when"], reverse=True)[:10]

    context = {
        "kpis": {
            "total_packages": total_packages,
            "active_packages": active_packages,
            "disposed_all": disposed_all,
            "pm_pending": pm_pending,
        },
        "charts": {
            "months": months,
            "labels": lbls,
            "desktop": desktop_series,
            "mouse": mouse_series,
            "keyboard": keyboard_series,
            "ups": ups_series,
            "disposed_by_cat_labels": disposed_labels,
            "disposed_by_cat_data": disposed_data,
            "stack_labels": stack_labels,
            "stack_active": active_counts,
            "stack_disposed": disposed_counts,
        },
        "recent": recent,
        "audit": audit,
        "pm_upcoming": pm_upcoming,
    }
    return render(request, "dashboard.html", context)