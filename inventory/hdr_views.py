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

    # Load the new template
    template_path = 'media/pm_reports/new_hdr.xlsx'
    wb = load_workbook(template_path, data_only=False, keep_vba=False)

    # Use the template's first sheet
    ws = wb.worksheets[0]
    wb.active = ws  # Make it the active sheet

    # Unmerge all cells to avoid "MergedCell is read-only" errors
    # Create a list of merged ranges to unmerge
    merged_ranges = list(ws.merged_cells.ranges)
    for merged_range in merged_ranges:
        ws.unmerge_cells(str(merged_range))

    # Fill in header information in the template
    ws['B2'] = report.period_display
    ws['B4'] = report.region
    ws['H4'] = report.network_admin_name
    ws['B5'] = report.office
    ws['H5'] = report.network_admin_contact
    ws['B6'] = report.address
    ws['H6'] = report.network_admin_email
    # Data starts at row 9 (assuming row 8 has headers in template)
    data_start_row = 9

    # Write each entry to the template
    for idx, entry in enumerate(entries):
        row_num = data_start_row + idx

        # Write data directly to template cells
        ws[f'A{row_num}'] = str(entry.ref_number)
        ws[f'B{row_num}'] = str(entry.incident_type)
        ws[f'C{row_num}'] = str(entry.main_category)
        ws[f'D{row_num}'] = str(entry.sub_category)
        ws[f'E{row_num}'] = str(entry.description)
        ws[f'F{row_num}'] = str(entry.status)
        ws[f'G{row_num}'] = entry.date_reported if entry.date_reported else ''
        ws[f'H{row_num}'] = str(entry.reported_by)
        ws[f'I{row_num}'] = str(entry.resolution) if entry.resolution else ''

        # Enable text wrapping for all data cells in this row
        for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
            ws[f'{col}{row_num}'].alignment = Alignment(wrap_text=True, vertical='top')

    # Apply formatting
    # Merge specific cells
    ws.merge_cells('G14:H14')
    ws.merge_cells('G15:H15')
    ws.merge_cells('A12:B12')
    ws.merge_cells('A14:B14')
    ws.merge_cells('A15:B15')

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
