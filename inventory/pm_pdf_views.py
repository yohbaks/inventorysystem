"""
PDF Export Views for PM Checklists
"""

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import PMChecklistCompletion, PMChecklistReport
from .pm_pdf_export import generate_pm_checklist_pdf, generate_monthly_report_pdf


@login_required
def export_checklist_pdf(request, completion_id):
    """Export a completed checklist as PDF"""
    
    completion = get_object_or_404(PMChecklistCompletion, id=completion_id)
    
    # Generate PDF
    pdf_buffer = generate_pm_checklist_pdf(completion)
    
    # Create response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    
    # Filename
    filename = f"PM_Checklist_{completion.schedule.template.annex_code}_{completion.completion_date.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def export_report_pdf(request, report_id):
    """Export monthly/period report as PDF"""
    
    report = get_object_or_404(PMChecklistReport, id=report_id)
    
    # Generate PDF
    pdf_buffer = generate_monthly_report_pdf(report)
    
    # Save PDF to report model
    filename = f"PM_Report_{report.report_type}_{report.period_start.strftime('%Y%m%d')}_to_{report.period_end.strftime('%Y%m%d')}.pdf"
    report.pdf_file.save(filename, pdf_buffer, save=True)
    
    # Create response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
