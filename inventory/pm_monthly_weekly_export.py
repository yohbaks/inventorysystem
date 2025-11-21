"""
PDF Export for Annex B (Monthly) and Annex C (Weekly) PM Checklists
"""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

from .models import PMChecklistCompletion


def export_monthly_pm_pdf(request, completion_id):
    """Export Annex B Monthly PM checklist as PDF"""

    completion = get_object_or_404(PMChecklistCompletion, id=completion_id)
    schedule = completion.schedule
    template = schedule.template

    # Create response
    response = HttpResponse(content_type='application/pdf')
    filename = f'PM_Monthly_{schedule.scheduled_date.strftime("%Y_%m")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create PDF
    doc = SimpleDocTemplate(response, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.5*inch, rightMargin=0.5*inch)

    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.black,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    elements.append(Paragraph(f'ANNEX "B"', title_style))
    elements.append(Paragraph(template.title, title_style))

    # Schedule and Date
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica'
    )

    elements.append(Paragraph(f'<b>Schedule:</b> {template.schedule_note}', normal_style))
    elements.append(Paragraph(f'<b>Date accomplished:</b> {completion.completion_date.strftime("%B %d, %Y")}', normal_style))
    elements.append(Spacer(1, 12))

    # Create table data
    table_data = [
        ['Item\nNo.', 'Task', 'Status\n(put ✓ if done)', 'Problems\nEncountered/Action']
    ]

    # Get item completions
    item_completions = completion.item_completions.all().order_by('item__item_number')

    for item_comp in item_completions:
        item = item_comp.item

        # Task description
        task_text = Paragraph(item.task_description.replace('\n', '<br/>'), normal_style)

        # Status (checkmark if completed)
        status = '✓' if item_comp.is_completed else ''

        # Problems/Action
        problems_action = ''
        if item_comp.problems_encountered:
            problems_action += f"<b>Problems:</b> {item_comp.problems_encountered}<br/>"
        if item_comp.action_taken:
            problems_action += f"<b>Action:</b> {item_comp.action_taken}"
        problems_action_text = Paragraph(problems_action if problems_action else '', normal_style)

        table_data.append([
            str(item.item_number),
            task_text,
            status,
            problems_action_text
        ])

    # Create table
    table = Table(table_data, colWidths=[0.6*inch, 3.5*inch, 0.9*inch, 2.5*inch])

    # Table style
    table_style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # All cells
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item number center
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Status center
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
    ])

    table.setStyle(table_style)
    elements.append(table)

    # Signature section
    elements.append(Spacer(1, 30))
    elements.append(Paragraph('<b>Accomplished by:</b>', normal_style))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph('_' * 50, normal_style))
    elements.append(Paragraph(f'({completion.printed_name or completion.completed_by.get_full_name() or completion.completed_by.username})', normal_style))
    elements.append(Paragraph('(Signature over printed name)', normal_style))

    # Build PDF
    doc.build(elements)
    return response


def export_weekly_pm_pdf(request, completion_id):
    """Export Annex C Weekly PM checklist as PDF with 4 weeks"""

    completion = get_object_or_404(PMChecklistCompletion, id=completion_id)
    schedule = completion.schedule
    template = schedule.template

    # Create response
    response = HttpResponse(content_type='application/pdf')
    filename = f'PM_Weekly_{schedule.scheduled_date.strftime("%Y_%m")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create PDF
    doc = SimpleDocTemplate(response, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.5*inch, rightMargin=0.5*inch)

    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.black,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    elements.append(Paragraph(f'ANNEX "C"', title_style))
    elements.append(Paragraph(template.title, title_style))

    # Schedule, Location, and Date
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica'
    )

    elements.append(Paragraph(f'<b>Schedule:</b> {template.schedule_note}', normal_style))
    if schedule.location:
        elements.append(Paragraph(f'<b>Location of FD/BD:</b> {schedule.location}', normal_style))
    elements.append(Paragraph(f'<b>Date accomplished:</b> {completion.completion_date.strftime("%B %Y")}', normal_style))
    elements.append(Spacer(1, 12))

    # Create table data with 4 weeks
    table_data = [
        ['Item\nNo.', 'Task', 'Wk1', 'Wk2', 'Wk3', 'Wk4', 'Problems\nEncountered/Action']
    ]

    # Get item completions
    item_completions = completion.item_completions.all().order_by('item__item_number')

    for item_comp in item_completions:
        item = item_comp.item

        # Task description
        task_text = Paragraph(item.task_description.replace('\n', '<br/>'), normal_style)

        # Week checkmarks
        wk1 = '✓' if item_comp.week1 else ''
        wk2 = '✓' if item_comp.week2 else ''
        wk3 = '✓' if item_comp.week3 else ''
        wk4 = '✓' if item_comp.week4 else ''

        # Problems/Action
        problems_action = ''
        if item_comp.problems_encountered:
            problems_action += f"{item_comp.problems_encountered}<br/>"
        if item_comp.action_taken:
            problems_action += f"{item_comp.action_taken}"
        problems_action_text = Paragraph(problems_action if problems_action else '', normal_style)

        table_data.append([
            str(item.item_number),
            task_text,
            wk1,
            wk2,
            wk3,
            wk4,
            problems_action_text
        ])

    # Create table
    table = Table(table_data, colWidths=[0.5*inch, 2.8*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 2.2*inch])

    # Table style
    table_style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # All cells
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item number center
        ('ALIGN', (2, 1), (5, -1), 'CENTER'),  # Week columns center
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
    ])

    table.setStyle(table_style)
    elements.append(table)

    # Signature section
    elements.append(Spacer(1, 30))
    elements.append(Paragraph('<b>Accomplished by:</b>', normal_style))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph('_' * 50, normal_style))
    elements.append(Paragraph(f'({completion.printed_name or completion.completed_by.get_full_name() or completion.completed_by.username})', normal_style))
    elements.append(Paragraph('(Signature over printed name)', normal_style))

    # Build PDF
    doc.build(elements)
    return response
