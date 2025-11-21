"""
PM Daily/Weekly PDF Export - Redesigned for Daily Checklist Approach
Each day (Mon-Fri) has its own completion. Weekly report aggregates all 5 days.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.utils import timezone
from io import BytesIO
from datetime import timedelta
import calendar

from .models import PMChecklistCompletion, PMChecklistItem


def get_week_start_end(date):
    """Get Monday and Friday of the week containing the given date"""
    # Get the weekday (0=Monday, 6=Sunday)
    weekday = date.weekday()

    # Calculate Monday of this week
    monday = date - timedelta(days=weekday)

    # Calculate Friday of this week
    friday = monday + timedelta(days=4)

    return monday, friday


def get_week_completions(template, week_start_date):
    """
    Get all completions for a week (Mon-Fri) for a specific template
    Returns dict: {0: monday_completion, 1: tuesday_completion, ...}
    where keys are weekday numbers (0=Mon, 4=Fri)
    """
    monday, friday = get_week_start_end(week_start_date)

    completions = PMChecklistCompletion.objects.filter(
        schedule__template=template,
        completion_date__gte=monday,
        completion_date__lte=friday
    ).select_related('schedule', 'schedule__template', 'completed_by')

    # Organize by weekday
    week_completions = {}
    for comp in completions:
        weekday = comp.completion_date.weekday()
        if weekday < 5:  # Only Mon-Fri
            week_completions[weekday] = comp

    return week_completions


def generate_daily_pm_pdf(completion):
    """
    Generate PDF for a SINGLE day's PM checklist completion
    Shows the full form but only the relevant day column is filled
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

    # Title and header styling
    annex_style = ParagraphStyle(
        'AnnexStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        fontName='Helvetica-Bold'
    )

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )

    schedule_info_style = ParagraphStyle(
        'ScheduleInfo',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica'
    )

    template = completion.schedule.template

    # Annex code
    elements.append(Paragraph(f'ANNEX "{template.annex_code}"', annex_style))
    elements.append(Spacer(1, 10))

    # Title
    elements.append(Paragraph(template.title, title_style))
    elements.append(Spacer(1, 10))

    # Schedule info
    day_name = completion.completion_date.strftime('%A')
    date_str = completion.completion_date.strftime('%B %d, %Y')
    schedule_text = f"<b>Schedule:</b> {template.schedule_note}<br/>"
    schedule_text += f"<b>Date accomplished:</b> {date_str} ({day_name})"

    elements.append(Paragraph(schedule_text, schedule_info_style))
    elements.append(Spacer(1, 15))

    # Build table - only show the current day's data
    table_data = build_daily_table(completion)

    # Column widths
    col_widths = [12*mm, 75*mm, 9*mm, 9*mm, 9*mm, 9*mm, 9*mm, 45*mm]

    table = Table(table_data, colWidths=col_widths, repeatRows=2)

    # Apply table style
    table_style = create_annex_a_table_style(completion)
    table.setStyle(table_style)

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Signature section
    add_signature_section(elements, completion, styles)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_weekly_pm_pdf(template, week_start_date, user):
    """
    Generate WEEKLY PDF combining all 5 days (Mon-Fri)
    Shows the full form with all days filled from their respective completions
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

    # Title and header styling
    annex_style = ParagraphStyle(
        'AnnexStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        fontName='Helvetica-Bold'
    )

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )

    schedule_info_style = ParagraphStyle(
        'ScheduleInfo',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica'
    )

    # Annex code
    elements.append(Paragraph(f'ANNEX "{template.annex_code}"', annex_style))
    elements.append(Spacer(1, 10))

    # Title
    elements.append(Paragraph(template.title, title_style))
    elements.append(Spacer(1, 10))

    # Week info
    monday, friday = get_week_start_end(week_start_date)
    schedule_text = f"<b>Schedule:</b> {template.schedule_note}<br/>"
    schedule_text += f"<b>Week of:</b> {monday.strftime('%B %d')} - {friday.strftime('%B %d, %Y')}"

    elements.append(Paragraph(schedule_text, schedule_info_style))
    elements.append(Spacer(1, 15))

    # Get all week's completions
    week_completions = get_week_completions(template, week_start_date)

    # Build weekly aggregated table
    table_data = build_weekly_table(template, week_completions)

    # Column widths
    col_widths = [12*mm, 75*mm, 9*mm, 9*mm, 9*mm, 9*mm, 9*mm, 45*mm]

    table = Table(table_data, colWidths=col_widths, repeatRows=2)

    # Apply table style
    table_style = create_annex_a_table_style_for_weekly(template)
    table.setStyle(table_style)

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Signature section - show who generated the weekly report
    signature_style = ParagraphStyle(
        'SignatureStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica'
    )

    elements.append(Paragraph("<b>Weekly report generated by:</b>", signature_style))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("_" * 50, signature_style))
    elements.append(Paragraph(f"({user.get_full_name() or user.username})", signature_style))
    elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y')}", signature_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def build_daily_table(completion):
    """Build table for a SINGLE day's completion - only one column filled"""

    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    item_completions = completion.item_completions.all().select_related('item').order_by('item__item_number')

    # Determine which day this completion is for
    weekday = completion.completion_date.weekday()  # 0=Monday, 4=Friday

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

    # Header rows
    header_row1 = [
        Paragraph('<b>Item<br/>No.</b>', header_style),
        Paragraph('<b>Task</b>', header_style),
        Paragraph('<b>Status<br/>(put ✓ if done)</b>', header_style),
        '', '', '', '',
        Paragraph('<b>Problems<br/>Encountered/Action</b>', header_style)
    ]

    header_row2 = [
        '', '',
        Paragraph('<b>M</b>', center_style),
        Paragraph('<b>T</b>', center_style),
        Paragraph('<b>W</b>', center_style),
        Paragraph('<b>Th</b>', center_style),
        Paragraph('<b>F</b>', center_style),
        ''
    ]

    table_data = [header_row1, header_row2]

    # Add data rows
    for item_comp in item_completions:
        item = item_comp.item

        # Check if this is a weekly item (6-11) that's only done on Friday
        is_weekly_friday_only = item.item_number in [6, 7, 8, 9, 10, 11]
        is_disabled_today = is_weekly_friday_only and weekday != 4  # Not Friday

        # Task description
        task_text = item.task_description.replace('\n', '<br/>')
        if item.has_schedule_times and item.schedule_times:
            time_list = ", ".join(item.schedule_times)
            task_text = f"{task_text}<br/><br/><b>Times:</b> {time_list}"

        # Add note for weekly items on non-Friday days
        if is_disabled_today:
            task_text += "<br/><br/><i>(Completed on Friday)</i>"

        # Checkmarks - only fill the current day's column
        checks = ["", "", "", "", ""]  # M, T, W, Th, F

        # For weekly Friday-only items (6-8, 11), don't show checkmark on Mon-Thu
        if not is_disabled_today:
            # Determine if this item was completed today
            is_completed = False
            if weekday == 0:
                is_completed = item_comp.monday
            elif weekday == 1:
                is_completed = item_comp.tuesday
            elif weekday == 2:
                is_completed = item_comp.wednesday
            elif weekday == 3:
                is_completed = item_comp.thursday
            elif weekday == 4:
                is_completed = item_comp.friday

            if is_completed:
                checks[weekday] = "✓"

        # Problems/Actions - don't show for disabled items
        problems_text = ""
        if not is_disabled_today:
            if item_comp.problems_encountered:
                problems_text += item_comp.problems_encountered
            if item_comp.action_taken:
                if problems_text:
                    problems_text += "<br/><br/>Action: "
                problems_text += item_comp.action_taken

        table_data.append([
            Paragraph(str(item.item_number), center_style),
            Paragraph(task_text, task_style),
            Paragraph(checks[0], center_style),  # Monday
            Paragraph(checks[1], center_style),  # Tuesday
            Paragraph(checks[2], center_style),  # Wednesday
            Paragraph(checks[3], center_style),  # Thursday
            Paragraph(checks[4], center_style),  # Friday
            Paragraph(problems_text, task_style) if problems_text else ""
        ])

    return table_data


def build_weekly_table(template, week_completions):
    """Build table aggregating ALL 5 days of completions"""

    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    # Get all items for this template
    items = PMChecklistItem.objects.filter(template=template, is_active=True).order_by('item_number')

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

    # Header rows
    header_row1 = [
        Paragraph('<b>Item<br/>No.</b>', header_style),
        Paragraph('<b>Task</b>', header_style),
        Paragraph('<b>Status<br/>(put ✓ if done)</b>', header_style),
        '', '', '', '',
        Paragraph('<b>Problems<br/>Encountered/Action</b>', header_style)
    ]

    header_row2 = [
        '', '',
        Paragraph('<b>M</b>', center_style),
        Paragraph('<b>T</b>', center_style),
        Paragraph('<b>W</b>', center_style),
        Paragraph('<b>Th</b>', center_style),
        Paragraph('<b>F</b>', center_style),
        ''
    ]

    table_data = [header_row1, header_row2]

    # For each item, aggregate completion status across all 5 days
    for item in items:
        # Task description
        task_text = item.task_description.replace('\n', '<br/>')
        if item.has_schedule_times and item.schedule_times:
            time_list = ", ".join(item.schedule_times)
            task_text = f"{task_text}<br/><br/><b>Times:</b> {time_list}"

        # Checkmarks for each day
        checks = ["", "", "", "", ""]  # M, T, W, Th, F

        # Aggregate problems from all days
        all_problems = []

        # Check each day
        for weekday in range(5):  # 0=Mon to 4=Fri
            if weekday in week_completions:
                completion = week_completions[weekday]
                item_comp = completion.item_completions.filter(item=item).first()

                if item_comp:
                    # Check if completed on this day
                    is_completed = False
                    if weekday == 0:
                        is_completed = item_comp.monday
                    elif weekday == 1:
                        is_completed = item_comp.tuesday
                    elif weekday == 2:
                        is_completed = item_comp.wednesday
                    elif weekday == 3:
                        is_completed = item_comp.thursday
                    elif weekday == 4:
                        is_completed = item_comp.friday

                    if is_completed:
                        checks[weekday] = "✓"

                    # Collect problems
                    if item_comp.problems_encountered:
                        day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'][weekday]
                        all_problems.append(f"<b>{day_name}:</b> {item_comp.problems_encountered}")
                    if item_comp.action_taken:
                        day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'][weekday]
                        all_problems.append(f"<b>{day_name} Action:</b> {item_comp.action_taken}")

        # Combine all problems
        problems_text = "<br/>".join(all_problems)

        table_data.append([
            Paragraph(str(item.item_number), center_style),
            Paragraph(task_text, task_style),
            Paragraph(checks[0], center_style),  # Monday
            Paragraph(checks[1], center_style),  # Tuesday
            Paragraph(checks[2], center_style),  # Wednesday
            Paragraph(checks[3], center_style),  # Thursday
            Paragraph(checks[4], center_style),  # Friday
            Paragraph(problems_text, task_style) if problems_text else ""
        ])

    return table_data


def create_annex_a_table_style(completion):
    """Create table style for Annex A with proper formatting"""

    item_completions = completion.item_completions.all().select_related('item').order_by('item__item_number')

    table_style_list = [
        # Header rows
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),

        # Merge cells
        ('SPAN', (0, 0), (0, 1)),  # Item No.
        ('SPAN', (1, 0), (1, 1)),  # Task
        ('SPAN', (2, 0), (6, 0)),  # Status spans M-F
        ('SPAN', (7, 0), (7, 1)),  # Problems

        # Alignment
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (6, -1), 'CENTER'),
        ('ALIGN', (7, 0), (7, -1), 'LEFT'),
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

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]

    # Dark gray for weekly tasks (items 6-10)
    # Only shade columns 0-6 (Item No, Task, M, T, W, Th, F)
    # Leave column 7 (Problems) unshaded
    weekly_task_color = colors.Color(0.45, 0.45, 0.45)

    for idx, item_comp in enumerate(item_completions):
        row_index = idx + 2
        if item_comp.item.item_number in [6, 7, 8, 9, 10, 11]:
            # Shade only columns 0-6, not column 7 (Problems)
            table_style_list.append(('BACKGROUND', (0, row_index), (6, row_index), weekly_task_color))
            table_style_list.append(('TEXTCOLOR', (0, row_index), (6, row_index), colors.white))

    return TableStyle(table_style_list)


def create_annex_a_table_style_for_weekly(template):
    """Create table style for weekly aggregated report"""

    items = PMChecklistItem.objects.filter(template=template, is_active=True).order_by('item_number')

    table_style_list = [
        # Header rows
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),

        # Merge cells
        ('SPAN', (0, 0), (0, 1)),  # Item No.
        ('SPAN', (1, 0), (1, 1)),  # Task
        ('SPAN', (2, 0), (6, 0)),  # Status spans M-F
        ('SPAN', (7, 0), (7, 1)),  # Problems

        # Alignment
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (6, -1), 'CENTER'),
        ('ALIGN', (7, 0), (7, -1), 'LEFT'),
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

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]

    # Dark gray for weekly tasks (items 6-10)
    # Only shade columns 0-6 (Item No, Task, M, T, W, Th, F)
    # Leave column 7 (Problems) unshaded
    weekly_task_color = colors.Color(0.45, 0.45, 0.45)

    for idx, item in enumerate(items):
        row_index = idx + 2
        if item.item_number in [6, 7, 8, 9, 10, 11]:
            # Shade only columns 0-6, not column 7 (Problems)
            table_style_list.append(('BACKGROUND', (0, row_index), (6, row_index), weekly_task_color))
            table_style_list.append(('TEXTCOLOR', (0, row_index), (6, row_index), colors.white))

    return TableStyle(table_style_list)


def add_signature_section(elements, completion, styles):
    """Add signature section to PDF"""
    signature_style = ParagraphStyle(
        'SignatureStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica'
    )

    elements.append(Paragraph("<b>Accomplished by:</b>", signature_style))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("_" * 50, signature_style))
    elements.append(Paragraph(f"({completion.printed_name or completion.completed_by.get_full_name() or completion.completed_by.username})", signature_style))
    elements.append(Paragraph("(Signature over printed name)", signature_style))
