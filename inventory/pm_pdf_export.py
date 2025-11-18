"""
PDF Export for PM Checklists
Generates A4 format PDFs matching the original paper forms
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from django.conf import settings
from io import BytesIO
import os

from .models import PMChecklistCompletion, PMChecklistItemCompletion


def generate_pm_checklist_pdf(completion):
    """
    Generate PDF for a completed PM checklist
    Returns BytesIO buffer containing the PDF
    """
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    annex_style = ParagraphStyle(
        'AnnexStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        fontName='Helvetica-Bold'
    )
    
    schedule = completion.schedule
    template = schedule.template
    
    # Annex code (top right)
    annex_text = f'ANNEX "{template.annex_code}"'
    elements.append(Paragraph(annex_text, annex_style))
    elements.append(Spacer(1, 10))
    
    # Title
    title = Paragraph(template.title, title_style)
    elements.append(title)
    elements.append(Spacer(1, 10))
    
    # Schedule information
    schedule_info_style = ParagraphStyle(
        'ScheduleInfo',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica'
    )
    
    schedule_text = f"<b>Schedule:</b> {template.schedule_note}<br/>"
    schedule_text += f"<b>Date accomplished:</b> {completion.completion_date.strftime('%B %d, %Y')}"
    
    if schedule.location:
        schedule_text += f"<br/><b>Location of FD/BD:</b> {schedule.location}"
    
    elements.append(Paragraph(schedule_text, schedule_info_style))
    elements.append(Spacer(1, 15))
    
    # Build checklist table based on annex type
    if template.annex_code == 'A':
        table_data = build_annex_a_table(completion)
    elif template.annex_code == 'B':
        table_data = build_annex_b_table(completion)
    elif template.annex_code == 'C':
        table_data = build_annex_c_table(completion)
    elif template.annex_code == 'F':
        table_data = build_annex_f_table(completion)
    else:
        table_data = build_simple_table(completion)
    
    # Create table with different column widths based on annex type
    if template.annex_code == 'A':
        # 8 columns: Item No | Task | M | T | W | Th | F | Problems
        col_widths = [12*mm, 75*mm, 9*mm, 9*mm, 9*mm, 9*mm, 9*mm, 45*mm]
    elif template.annex_code == 'C':
        col_widths = [15*mm, 80*mm, 45*mm, 50*mm]
    else:
        col_widths = [15*mm, 100*mm, 35*mm, 40*mm]

    table = Table(table_data, colWidths=col_widths, repeatRows=2)

    # Table style
    if template.annex_code == 'A':
        table_style_list = [
            # Header row 1 - gray background
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            # Header row 2 - gray background
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),

            # Merge cells for header row 1
            ('SPAN', (0, 0), (0, 1)),  # Item No. spans 2 rows
            ('SPAN', (1, 0), (1, 1)),  # Task spans 2 rows
            ('SPAN', (2, 0), (6, 0)),  # Status spans 5 columns (M T W Th F)
            ('SPAN', (7, 0), (7, 1)),  # Problems spans 2 rows

            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Item No. centered
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # Task left-aligned
            ('ALIGN', (2, 0), (6, -1), 'CENTER'),  # Status columns centered
            ('ALIGN', (7, 0), (7, -1), 'LEFT'),    # Problems left-aligned
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),

            # Fonts
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 1), 8),
            ('FONTSIZE', (0, 2), (-1, -1), 8),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),

            # Grid lines
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]

        # Add VERY dark gray shading for weekly tasks (items 7-11)
        # Weekly tasks start at row index 2 (after 2 header rows) + position in filtered items
        weekly_task_color = colors.Color(0.45, 0.45, 0.45)  # Dark gray matching template

        # Find which rows contain items 7-11
        for idx, item_comp in enumerate(item_completions):
            row_index = idx + 2  # +2 for the 2 header rows
            if item_comp.item.item_number in [7, 8, 9, 10, 11]:
                table_style_list.append(('BACKGROUND', (0, row_index), (-1, row_index), weekly_task_color))
                # Make text white on dark background
                table_style_list.append(('TEXTCOLOR', (0, row_index), (-1, row_index), colors.white))
    else:
        table_style_list = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]

    table_style = TableStyle(table_style_list)
    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Signature section
    signature_style = ParagraphStyle(
        'SignatureStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica'
    )
    
    elements.append(Paragraph("<b>Accomplished by:</b>", signature_style))
    elements.append(Spacer(1, 30))
    
    # Add signature image if available
    if completion.signature_image:
        try:
            sig_path = os.path.join(settings.MEDIA_ROOT, completion.signature_image.name)
            if os.path.exists(sig_path):
                sig_img = Image(sig_path, width=60*mm, height=20*mm)
                elements.append(sig_img)
        except:
            pass
    
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("_" * 50, signature_style))
    elements.append(Paragraph(f"({completion.printed_name or completion.completed_by.get_full_name() or completion.completed_by.username})", signature_style))
    elements.append(Paragraph("(Signature over printed name)", signature_style))
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer


def build_annex_a_table(completion):
    """Build table for Annex A (Daily/Weekly) - matches exact template format"""

    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    item_completions = completion.item_completions.all().select_related('item').order_by('item__item_number')

    # Create styles
    header_style = ParagraphStyle(
        'HeaderStyle',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=9,
        alignment=TA_CENTER,
    )

    task_style = ParagraphStyle(
        'TaskStyle',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=TA_LEFT,
    )

    center_style = ParagraphStyle(
        'CenterStyle',
        fontName='Helvetica',
        fontSize=8,
        alignment=TA_CENTER,
    )

    # Header rows - Status column spans 5 sub-columns
    header_row1 = [
        Paragraph('<b>Item<br/>No.</b>', header_style),
        Paragraph('<b>Task</b>', header_style),
        Paragraph('<b>Status<br/>(put ✓ if done)</b>', header_style),  # This will span 5 columns
        '',  # Placeholder for colspan
        '',  # Placeholder for colspan
        '',  # Placeholder for colspan
        '',  # Placeholder for colspan
        Paragraph('<b>Problems<br/>Encountered/Action</b>', header_style)
    ]

    header_row2 = [
        '',  # Empty for Item No.
        '',  # Empty for Task
        Paragraph('<b>M</b>', center_style),
        Paragraph('<b>T</b>', center_style),
        Paragraph('<b>W</b>', center_style),
        Paragraph('<b>Th</b>', center_style),
        Paragraph('<b>F</b>', center_style),
        '',  # Empty for Problems
    ]

    table_data = [header_row1, header_row2]

    for item_comp in item_completions:
        item = item_comp.item

        # Task description with time schedule
        # Convert newlines to <br/> for proper PDF rendering
        task_text = item.task_description.replace('\n', '<br/>')
        if item.has_schedule_times and item.schedule_times:
            time_list = "<br/>".join(item.schedule_times)
            task_text = f"{task_text}<br/><br/>{time_list}"

        # Status checkmarks for each day
        mon = "✓" if item_comp.monday else ""
        tue = "✓" if item_comp.tuesday else ""
        wed = "✓" if item_comp.wednesday else ""
        thu = "✓" if item_comp.thursday else ""
        fri = "✓" if item_comp.friday else ""

        # Problems/Actions
        problems_text = ""
        if item_comp.problems_encountered:
            problems_text += item_comp.problems_encountered
        if item_comp.action_taken:
            if problems_text:
                problems_text += "<br/><br/>Action: "
            problems_text += item_comp.action_taken

        table_data.append([
            Paragraph(str(item.item_number), center_style),
            Paragraph(task_text, task_style),
            Paragraph(mon, center_style),
            Paragraph(tue, center_style),
            Paragraph(wed, center_style),
            Paragraph(thu, center_style),
            Paragraph(fri, center_style),
            Paragraph(problems_text, task_style) if problems_text else ""
        ])

    return table_data


def build_annex_b_table(completion):
    """Build table for Annex B (Monthly)"""
    
    item_completions = completion.item_completions.all().select_related('item').order_by('item__item_number')
    
    # Header row
    header = [
        'Item\nNo.',
        'Task',
        'Status\n(put ✓ if done)',
        'Problems Encountered/Action'
    ]
    
    table_data = [header]
    
    for item_comp in item_completions:
        item = item_comp.item
        
        status_text = "✓" if item_comp.is_completed else ""
        
        problems_text = ""
        if item_comp.problems_encountered:
            problems_text += item_comp.problems_encountered
        if item_comp.action_taken:
            if problems_text:
                problems_text += "\n\nAction: "
            problems_text += item_comp.action_taken
        
        table_data.append([
            str(item.item_number),
            item.task_description,
            status_text,
            problems_text
        ])
    
    return table_data


def build_annex_c_table(completion):
    """Build table for Annex C (Weekly Building)"""
    
    item_completions = completion.item_completions.all().select_related('item').order_by('item__item_number')
    
    # Header row
    header = [
        'Item\nNo.',
        'Task',
        'Status\n(put ✓ if done)\nWk1  Wk2  Wk3  Wk4',
        'Problems\nEncountered/Action'
    ]
    
    table_data = [header]
    
    for item_comp in item_completions:
        item = item_comp.item
        
        wk1 = "✓" if item_comp.week1 else ""
        wk2 = "✓" if item_comp.week2 else ""
        wk3 = "✓" if item_comp.week3 else ""
        wk4 = "✓" if item_comp.week4 else ""
        status_text = f"{wk1}      {wk2}      {wk3}      {wk4}"
        
        problems_text = ""
        if item_comp.problems_encountered:
            problems_text += item_comp.problems_encountered
        if item_comp.action_taken:
            if problems_text:
                problems_text += "\n\nAction: "
            problems_text += item_comp.action_taken
        
        table_data.append([
            str(item.item_number),
            item.task_description,
            status_text,
            problems_text
        ])
    
    return table_data


def build_annex_f_table(completion):
    """Build table for Annex F (Semi-Annual)"""
    
    return build_annex_b_table(completion)  # Same format as Annex B


def build_simple_table(completion):
    """Build simple table for other checklist types"""
    
    return build_annex_b_table(completion)  # Default to simple format


def generate_monthly_report_pdf(report):
    """
    Generate monthly compilation report PDF
    """
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    # Title
    title_text = f"Preventive Maintenance Report<br/>{report.get_report_type_display()}"
    elements.append(Paragraph(title_text, title_style))
    
    # Period
    period_text = f"Period: {report.period_start.strftime('%B %d, %Y')} to {report.period_end.strftime('%B %d, %Y')}"
    elements.append(Paragraph(period_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Summary statistics
    summary_data = [
        ['Summary Statistics', 'Count'],
        ['Total Checklists', str(report.total_checklists)],
        ['Completed', str(report.completed_checklists)],
        ['Pending', str(report.pending_checklists)],
        ['Overdue', str(report.overdue_checklists)],
        ['Issues Found', str(report.total_issues_found)],
    ]
    
    summary_table = Table(summary_data, colWidths=[120*mm, 50*mm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Get completions for this period
    from .models import PMChecklistCompletion
    
    completions = PMChecklistCompletion.objects.filter(
        completion_date__gte=report.period_start,
        completion_date__lte=report.period_end
    ).select_related('schedule__template', 'completed_by').order_by('completion_date')
    
    if report.annex_filter:
        completions = completions.filter(schedule__template__annex_code=report.annex_filter)
    
    # Completed checklists detail
    if completions.exists():
        elements.append(Paragraph("Completed Checklists Detail", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        detail_data = [['Date', 'Checklist Type', 'Completed By', 'Issues']]
        
        for comp in completions:
            issues_count = comp.item_completions.filter(problems_encountered__isnull=False).exclude(problems_encountered='').count()
            
            detail_data.append([
                comp.completion_date.strftime('%Y-%m-%d'),
                comp.schedule.template.get_annex_code_display(),
                comp.completed_by.get_full_name() or comp.completed_by.username,
                str(issues_count) if issues_count > 0 else '-'
            ])
        
        detail_table = Table(detail_data, colWidths=[30*mm, 70*mm, 50*mm, 20*mm])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(detail_table)
    
    # Generated by footer
    elements.append(Spacer(1, 30))
    footer_text = f"Generated by: {report.generated_by.get_full_name() or report.generated_by.username}<br/>"
    footer_text += f"Generated on: {report.generated_at.strftime('%B %d, %Y at %I:%M %p')}"
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
