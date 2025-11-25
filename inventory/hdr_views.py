"""
HDR (HelpDesk Report) Views
Monthly reporting system for helpdesk incidents and service requests
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db import models
from datetime import date
from .models import HDRReport, HDREntry


@login_required
def hdr_list(request):
    """List all HDR reports"""
    reports = HDRReport.objects.all().select_related('created_by')

    context = {
        'reports': reports,
    }
    return render(request, 'hdr/hdr_list.html', context)


@login_required
def hdr_create(request):
    """Create a new HDR report"""
    if request.method == 'POST':
        try:
            # Get form data
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))

            # Check if report already exists
            if HDRReport.objects.filter(month=month, year=year).exists():
                messages.error(request, f'A report for {date(year, month, 1).strftime("%B %Y")} already exists.')
                return redirect('hdr_list')

            # Create report (no default entries - user will add manually)
            report = HDRReport.objects.create(
                month=month,
                year=year,
                region=request.POST.get('region', 'VIII'),
                office=request.POST.get('office', 'DPWH Leyte 4th Engineering District'),
                address=request.POST.get('address', 'Ormoc City Leyte'),
                network_admin_name=request.POST.get('network_admin_name', 'BOBBY L. YU'),
                network_admin_contact=request.POST.get('network_admin_contact', '66800|09219290909'),
                network_admin_email=request.POST.get('network_admin_email', 'yu.bobby@dpwh.gov.ph'),
                created_by=request.user
            )

            messages.success(request, f'HDR report for {report.period_display} created successfully. You can now add incidents.')
            return redirect('hdr_edit', report_id=report.id)

        except Exception as e:
            messages.error(request, f'Error creating report: {str(e)}')
            return redirect('hdr_list')

    # GET request - show create form
    context = {
        'months': [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ],
        'years': range(2024, 2031),
        'current_month': timezone.now().month,
        'current_year': timezone.now().year,
    }
    return render(request, 'hdr/hdr_create.html', context)


@login_required
def hdr_view(request, report_id):
    """View HDR report details"""
    report = get_object_or_404(HDRReport, id=report_id)
    entries = report.entries.order_by('date_reported', 'ref_number')

    context = {
        'report': report,
        'entries': entries
    }
    return render(request, 'hdr/hdr_view.html', context)


@login_required
def hdr_edit(request, report_id):
    """Edit an existing HDR report"""
    report = get_object_or_404(HDRReport, id=report_id)

    # Prevent editing finalized reports
    if report.is_finalized:
        messages.warning(request, 'This report has been finalized and cannot be edited.')
        return redirect('hdr_view', report_id=report.id)

    if request.method == 'POST':
        try:
            # Check if adding new entry
            if 'add_entry' in request.POST:
                # Auto-generate reference number
                ref_number = report.get_next_ref_number()

                HDREntry.objects.create(
                    report=report,
                    ref_number=ref_number,
                    incident_type=request.POST.get('new_incident_type', 'Service Request'),
                    main_category=request.POST.get('new_main_category'),
                    sub_category=request.POST.get('new_sub_category'),
                    description=request.POST.get('new_description'),
                    status=request.POST.get('new_status', 'Pending'),
                    date_reported=request.POST.get('new_date_reported'),
                    reported_by=request.POST.get('new_reported_by'),
                    resolution=request.POST.get('new_resolution', '')
                )
                messages.success(request, f'New incident added successfully with reference number: {ref_number}')
                return redirect('hdr_edit', report_id=report.id)

            # Check if deleting entry
            if 'delete_entry' in request.POST:
                entry_id = int(request.POST.get('entry_id'))
                entry = get_object_or_404(HDREntry, id=entry_id, report=report)
                entry.delete()
                messages.success(request, 'Incident deleted successfully.')
                return redirect('hdr_edit', report_id=report.id)

            # Update report details
            report.region = request.POST.get('region')
            report.office = request.POST.get('office')
            report.address = request.POST.get('address')
            report.network_admin_name = request.POST.get('network_admin_name')
            report.network_admin_contact = request.POST.get('network_admin_contact')
            report.network_admin_email = request.POST.get('network_admin_email')
            report.save()

            # Update entries
            for entry in report.entries.all():
                entry_prefix = f'entry_{entry.id}_'
                entry.ref_number = request.POST.get(f'{entry_prefix}ref_number', entry.ref_number)
                entry.incident_type = request.POST.get(f'{entry_prefix}incident_type', entry.incident_type)
                entry.main_category = request.POST.get(f'{entry_prefix}main_category', entry.main_category)
                entry.sub_category = request.POST.get(f'{entry_prefix}sub_category', entry.sub_category)
                entry.description = request.POST.get(f'{entry_prefix}description', entry.description)
                entry.status = request.POST.get(f'{entry_prefix}status', entry.status)
                entry.date_reported = request.POST.get(f'{entry_prefix}date_reported', entry.date_reported)
                entry.reported_by = request.POST.get(f'{entry_prefix}reported_by', entry.reported_by)
                entry.resolution = request.POST.get(f'{entry_prefix}resolution', entry.resolution)
                entry.save()

            messages.success(request, 'Report updated successfully.')
            return redirect('hdr_view', report_id=report.id)

        except Exception as e:
            messages.error(request, f'Error updating report: {str(e)}')

    context = {
        'report': report,
        'entries': report.entries.order_by('date_reported', 'ref_number'),
        'type_choices': HDREntry.TYPE_CHOICES,
        'category_choices': HDREntry.CATEGORY_CHOICES,
        'status_choices': HDREntry.STATUS_CHOICES,
        'next_ref_number': report.get_next_ref_number(),
    }
    return render(request, 'hdr/hdr_edit.html', context)


@login_required
def hdr_delete(request, report_id):
    """Delete HDR report"""
    if request.method == 'POST':
        report = get_object_or_404(HDRReport, id=report_id)
        period = report.period_display
        report.delete()
        messages.success(request, f'HDR report for {period} deleted successfully.')
        return redirect('hdr_list')
    return redirect('hdr_list')


@login_required
def hdr_finalize(request, report_id):
    """Finalize HDR report (lock it from editing)"""
    if request.method == 'POST':
        report = get_object_or_404(HDRReport, id=report_id)
        report.is_finalized = True
        report.finalized_at = timezone.now()
        report.save()
        messages.success(request, f'HDR report for {report.period_display} has been finalized.')
        return redirect('hdr_view', report_id=report.id)
    return redirect('hdr_list')


@login_required
def hdr_export_excel(request, report_id):
    """Export HDR report to Excel using template - fills data into pre-formatted cells"""
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
    from copy import copy
    from datetime import datetime
    import io

    report = get_object_or_404(HDRReport, id=report_id)
    entries = report.entries.order_by('date_reported', 'ref_number')

    # Load template
    template_path = 'media/pm_reports/HDR 2025.xlsx'
    wb = load_workbook(template_path)

    # Find the correct worksheet - try common sheet names
    ws = None
    sheet_names_to_try = ['Do not delete', 'Sheet1', 'Sheet', 'HDR']

    for sheet_name in sheet_names_to_try:
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            break

    # If no matching sheet found, use the first sheet
    if ws is None:
        ws = wb.worksheets[0]

    # Fill in header information
    ws['A2'] = f'For the Month of {report.period_display}'
    ws['B4'] = report.region
    ws['B5'] = report.office
    ws['B6'] = report.address
    ws['H4'] = report.network_admin_name
    ws['H5'] = report.network_admin_contact
    ws['H6'] = report.network_admin_email

    # Data starts at row 10 (row 9 has headers)
    data_start_row = 10

    # Define styles for data cells
    thin_border = Border(
        left=Side(style='thin', color='000000'),
        right=Side(style='thin', color='000000'),
        top=Side(style='thin', color='000000'),
        bottom=Side(style='thin', color='000000')
    )

    default_font = Font(name='Calibri', size=11, color='000000')
    center_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left_alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # Fill in data entries
    for idx, entry in enumerate(entries):
        row_num = data_start_row + idx

        # Ensure row is visible
        ws.row_dimensions[row_num].hidden = False
        ws.row_dimensions[row_num].height = 30  # Set minimum height

        # Column A - Ref Number
        cell_a = ws.cell(row=row_num, column=1)
        cell_a.value = str(entry.ref_number)
        cell_a.font = copy(default_font)
        cell_a.border = copy(thin_border)
        cell_a.alignment = copy(center_alignment)

        # Column B - Incident Type
        cell_b = ws.cell(row=row_num, column=2)
        cell_b.value = str(entry.incident_type)
        cell_b.font = copy(default_font)
        cell_b.border = copy(thin_border)
        cell_b.alignment = copy(center_alignment)

        # Column C - Main Category
        cell_c = ws.cell(row=row_num, column=3)
        cell_c.value = str(entry.main_category)
        cell_c.font = copy(default_font)
        cell_c.border = copy(thin_border)
        cell_c.alignment = copy(center_alignment)

        # Column D - Sub Category
        cell_d = ws.cell(row=row_num, column=4)
        cell_d.value = str(entry.sub_category)
        cell_d.font = copy(default_font)
        cell_d.border = copy(thin_border)
        cell_d.alignment = copy(center_alignment)

        # Column E - Description
        cell_e = ws.cell(row=row_num, column=5)
        cell_e.value = str(entry.description)
        cell_e.font = copy(default_font)
        cell_e.border = copy(thin_border)
        cell_e.alignment = copy(left_alignment)

        # Column F - Status
        cell_f = ws.cell(row=row_num, column=6)
        cell_f.value = str(entry.status)
        cell_f.font = copy(default_font)
        cell_f.border = copy(thin_border)
        cell_f.alignment = copy(center_alignment)

        # Column G - Date Reported
        cell_g = ws.cell(row=row_num, column=7)
        if entry.date_reported:
            if isinstance(entry.date_reported, str):
                try:
                    date_obj = datetime.strptime(entry.date_reported, '%Y-%m-%d')
                    cell_g.value = date_obj
                except:
                    cell_g.value = str(entry.date_reported)
            else:
                cell_g.value = entry.date_reported
            cell_g.number_format = 'MM/DD/YYYY'
        else:
            cell_g.value = ''
        cell_g.font = copy(default_font)
        cell_g.border = copy(thin_border)
        cell_g.alignment = copy(center_alignment)

        # Column H - Reported By
        cell_h = ws.cell(row=row_num, column=8)
        cell_h.value = str(entry.reported_by)
        cell_h.font = copy(default_font)
        cell_h.border = copy(thin_border)
        cell_h.alignment = copy(center_alignment)

        # Column I - Resolution
        cell_i = ws.cell(row=row_num, column=9)
        cell_i.value = str(entry.resolution) if entry.resolution else ''
        cell_i.font = copy(default_font)
        cell_i.border = copy(thin_border)
        cell_i.alignment = copy(left_alignment)

    # Ensure all columns are visible and have appropriate width
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 35
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 15
    ws.column_dimensions['H'].width = 20
    ws.column_dimensions['I'].width = 35

    # Prepare response
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Create response
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'HDR_{report.period_display.replace(" ", "_")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
