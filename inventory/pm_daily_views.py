"""
Views for Daily PM Checklist System
Handles daily completions and weekly aggregation
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
from django.db import transaction

from .models import (
    PMChecklistTemplate, PMChecklistSchedule, PMChecklistCompletion,
    PMChecklistItem, PMChecklistItemCompletion
)
from .pm_daily_weekly_export import (
    generate_daily_pm_pdf, generate_weekly_pm_pdf,
    get_week_start_end, get_week_completions
)


def auto_create_week_schedules(template, reference_date):
    """
    Automatically create PM schedules for the entire week (Mon-Fri)
    This ensures schedules are always available without manual creation
    """
    monday, friday = get_week_start_end(reference_date)

    # Create schedules for Mon-Fri only (weekday 0-4)
    for day_offset in range(5):
        schedule_date = monday + timedelta(days=day_offset)

        # Only create if doesn't exist
        PMChecklistSchedule.objects.get_or_create(
            template=template,
            scheduled_date=schedule_date,
            defaults={
                'due_date': schedule_date,
                'status': 'PENDING',
                'assigned_to': None  # Can be assigned later
            }
        )


@login_required
def daily_pm_dashboard(request):
    """Dashboard showing daily PM tasks for today"""

    today = timezone.now().date()
    weekday = today.weekday()

    # Don't show on weekends
    if weekday >= 5:  # Saturday or Sunday
        context = {
            'is_weekend': True,
            'today': today
        }
        return render(request, 'pm/daily_dashboard.html', context)

    # Get Annex A template (Daily/Weekly datacenter checklist)
    try:
        template = PMChecklistTemplate.objects.get(annex_code='A')
    except PMChecklistTemplate.DoesNotExist:
        messages.error(request, 'PM Checklist template not found. Please run populate_pm_templates command.')
        return redirect('home')

    # Automatically ensure schedules exist for the entire current week (Mon-Fri)
    auto_create_week_schedules(template, today)

    # Get this week's completions for progress tracking
    monday, friday = get_week_start_end(today)
    week_completions = get_week_completions(template, today)

    # Build list of all 5 days with their schedules and completion status
    week_days = []
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    for day_offset in range(5):
        day_date = monday + timedelta(days=day_offset)

        # Get schedule for this day
        day_schedule = PMChecklistSchedule.objects.filter(
            template=template,
            scheduled_date=day_date
        ).first()

        # Check if completed
        day_completion = None
        is_day_completed = False
        if day_schedule:
            try:
                day_completion = PMChecklistCompletion.objects.get(schedule=day_schedule)
                is_day_completed = True
            except PMChecklistCompletion.DoesNotExist:
                pass

        week_days.append({
            'date': day_date,
            'day_name': day_names[day_offset],
            'is_today': day_date == today,
            'schedule': day_schedule,
            'completion': day_completion,
            'is_completed': is_day_completed,
            'is_past': day_date < today,
            'is_future': day_date > today,
        })

    context = {
        'is_weekend': False,
        'today': today,
        'today_name': today.strftime('%A'),
        'template': template,
        'week_days': week_days,
        'monday': monday,
        'friday': friday,
    }

    return render(request, 'pm/daily_dashboard.html', context)


@login_required
def complete_daily_pm(request, schedule_id):
    """Complete today's PM checklist"""

    schedule = get_object_or_404(PMChecklistSchedule, id=schedule_id)
    template = schedule.template

    # Check if already completed - allow editing to update readings throughout the day
    existing_completion = None
    if hasattr(schedule, 'completion'):
        existing_completion = schedule.completion

    # Get all items for this template
    items = PMChecklistItem.objects.filter(template=template, is_active=True).order_by('item_number')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update existing completion or create new one
                if existing_completion:
                    completion = existing_completion
                    completion.completed_by = request.user
                    completion.printed_name = request.POST.get('printed_name', '')
                    completion.save()
                    # Delete old item completions to replace with new ones
                    completion.item_completions.all().delete()
                else:
                    completion = PMChecklistCompletion.objects.create(
                        schedule=schedule,
                        completed_by=request.user,
                        completion_date=schedule.scheduled_date,
                        printed_name=request.POST.get('printed_name', '')
                    )

                # Determine which day this is (0=Monday, 4=Friday)
                weekday = schedule.scheduled_date.weekday()
                day_fields = {
                    0: 'monday',
                    1: 'tuesday',
                    2: 'wednesday',
                    3: 'thursday',
                    4: 'friday'
                }
                day_field = day_fields.get(weekday)

                # Create item completions
                for item in items:
                    # Check if item was completed (checkbox checked)
                    item_key = f'item_{item.id}'
                    is_completed = request.POST.get(item_key) == 'on'

                    # For items with scheduled times (3, 4, 5), collect readings
                    action = ''
                    if item.has_schedule_times and item.item_number in [3, 4, 5]:
                        readings = []
                        for idx, time in enumerate(item.schedule_times):
                            reading_key = f'reading_{item.id}_{idx}'
                            reading_value = request.POST.get(reading_key, '').strip()
                            if reading_value:
                                readings.append(f"{time}: {reading_value}")

                        if readings:
                            action = '\n'.join(readings)
                    else:
                        # Standard action field for other items
                        action = request.POST.get(f'action_{item.id}', '').strip()

                    # Problems field
                    problems = request.POST.get(f'problems_{item.id}', '').strip()

                    # Build item completion data
                    # AUTOMATICALLY set only TODAY's day field
                    item_completion_data = {
                        'completion': completion,
                        'item': item,
                        'problems_encountered': problems,
                        'action_taken': action,
                        # All days default to False
                        'monday': False,
                        'tuesday': False,
                        'wednesday': False,
                        'thursday': False,
                        'friday': False,
                    }

                    # Weekly tasks (items 6-8, 11) are ONLY done on Friday
                    # For Mon-Thu, skip marking these items even if checked
                    if item.item_number in [6, 7, 8, 11] and weekday != 4:
                        # Don't mark weekly items on Mon-Thu, but still save the record
                        is_completed = False

                    # Set ONLY today's day field if item was completed
                    if day_field and is_completed:
                        item_completion_data[day_field] = True

                    PMChecklistItemCompletion.objects.create(**item_completion_data)

                # Update schedule status
                schedule.status = 'COMPLETED'
                schedule.save()

                messages.success(request, f'Daily PM checklist for {schedule.scheduled_date.strftime("%A, %B %d")} completed successfully!')
                return redirect('pm_daily_dashboard')

        except Exception as e:
            messages.error(request, f'Error completing checklist: {str(e)}')
            return redirect('complete_daily_pm', schedule_id=schedule_id)

    # Get weekday (0=Monday, 4=Friday)
    weekday = schedule.scheduled_date.weekday()
    is_friday = weekday == 4

    # Pre-populate form with existing data if available
    # Attach existing data to each item object
    if existing_completion:
        item_completions_dict = {ic.item.id: ic for ic in existing_completion.item_completions.all()}
        for item in items:
            if item.id in item_completions_dict:
                item_comp = item_completions_dict[item.id]

                # Attach checkbox state
                item.is_checked = False
                if weekday == 0 and item_comp.monday:
                    item.is_checked = True
                elif weekday == 1 and item_comp.tuesday:
                    item.is_checked = True
                elif weekday == 2 and item_comp.wednesday:
                    item.is_checked = True
                elif weekday == 3 and item_comp.thursday:
                    item.is_checked = True
                elif weekday == 4 and item_comp.friday:
                    item.is_checked = True

                # Attach problems and action
                item.existing_problems = item_comp.problems_encountered or ''
                item.existing_action = item_comp.action_taken or ''

                # Extract readings for scheduled items
                item.existing_readings = []
                if item_comp.action_taken and item.has_schedule_times:
                    readings = item_comp.action_taken.split('\n')
                    for reading in readings:
                        if ': ' in reading:
                            item.existing_readings.append(reading.split(': ', 1)[1])
            else:
                item.is_checked = False
                item.existing_problems = ''
                item.existing_action = ''
                item.existing_readings = []
    else:
        for item in items:
            item.is_checked = False
            item.existing_problems = ''
            item.existing_action = ''
            item.existing_readings = []

    context = {
        'schedule': schedule,
        'template': template,
        'items': items,
        'today': schedule.scheduled_date,
        'today_name': schedule.scheduled_date.strftime('%A'),
        'weekday': weekday,
        'is_friday': is_friday,
        'existing_completion': existing_completion,
    }

    return render(request, 'pm/complete_daily_pm.html', context)


@login_required
def export_daily_pm_pdf(request, completion_id):
    """Export a single day's PM checklist as PDF"""

    completion = get_object_or_404(PMChecklistCompletion, id=completion_id)

    # Generate PDF
    pdf_buffer = generate_daily_pm_pdf(completion)

    # Create response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')

    day_name = completion.completion_date.strftime('%A')
    date_str = completion.completion_date.strftime('%Y%m%d')
    filename = f"PM_Daily_{day_name}_{date_str}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
def export_weekly_pm_pdf(request):
    """
    Export WEEKLY PM checklist combining all 5 days
    Accepts 'date' parameter to specify which week (defaults to current week)
    """

    # Get date parameter or use today
    date_str = request.GET.get('date')
    if date_str:
        try:
            reference_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            reference_date = timezone.now().date()
    else:
        reference_date = timezone.now().date()

    # Get Annex A template
    try:
        template = PMChecklistTemplate.objects.get(annex_code='A')
    except PMChecklistTemplate.DoesNotExist:
        messages.error(request, 'PM Checklist template not found.')
        return redirect('pm_daily_dashboard')

    # Generate weekly PDF
    pdf_buffer = generate_weekly_pm_pdf(template, reference_date, request.user)

    # Create response
    monday, friday = get_week_start_end(reference_date)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')

    filename = f"PM_Weekly_{monday.strftime('%Y%m%d')}_{friday.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
def view_daily_pm_completion(request, completion_id):
    """View a completed daily PM checklist"""

    completion = get_object_or_404(
        PMChecklistCompletion.objects.select_related(
            'schedule__template',
            'completed_by'
        ),
        id=completion_id
    )

    item_completions = completion.item_completions.all().select_related('item').order_by('item__item_number')

    # Determine which day this was
    weekday = completion.completion_date.weekday()
    day_name = completion.completion_date.strftime('%A')

    context = {
        'completion': completion,
        'item_completions': item_completions,
        'day_name': day_name,
        'weekday': weekday,
    }

    return render(request, 'pm/view_daily_pm_completion.html', context)


@login_required
def weekly_pm_report_view(request):
    """View weekly PM report (all 5 days aggregated)"""

    # Get date parameter or use current week
    date_str = request.GET.get('date')
    if date_str:
        try:
            reference_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            reference_date = timezone.now().date()
    else:
        reference_date = timezone.now().date()

    # Get Annex A template
    try:
        template = PMChecklistTemplate.objects.get(annex_code='A')
    except PMChecklistTemplate.DoesNotExist:
        messages.error(request, 'PM Checklist template not found.')
        return redirect('pm_daily_dashboard')

    # Get week boundaries
    monday, friday = get_week_start_end(reference_date)

    # Get all completions for this week
    week_completions = get_week_completions(template, reference_date)

    # Get all items
    items = PMChecklistItem.objects.filter(template=template, is_active=True).order_by('item_number')

    # Build aggregated data
    aggregated_data = []
    for item in items:
        item_data = {
            'item': item,
            'completions': {
                'monday': False,
                'tuesday': False,
                'wednesday': False,
                'thursday': False,
                'friday': False,
            },
            'problems': []
        }

        # Check each day
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        for weekday in range(5):
            if weekday in week_completions:
                completion = week_completions[weekday]
                item_comp = completion.item_completions.filter(item=item).first()

                if item_comp:
                    # Check completion status
                    day_field = day_names[weekday]
                    is_completed = getattr(item_comp, day_field, False)
                    item_data['completions'][day_field] = is_completed

                    # Collect problems
                    if item_comp.problems_encountered or item_comp.action_taken:
                        item_data['problems'].append({
                            'day': day_names[weekday].capitalize(),
                            'problems': item_comp.problems_encountered,
                            'action': item_comp.action_taken
                        })

        aggregated_data.append(item_data)

    context = {
        'template': template,
        'monday': monday,
        'friday': friday,
        'week_completions': week_completions,
        'aggregated_data': aggregated_data,
        'reference_date': reference_date,
    }

    return render(request, 'pm/weekly_report_view.html', context)


@login_required
def create_weekly_schedules(request):
    """
    DEPRECATED: Schedules are now created automatically.
    This view is kept for backwards compatibility but just redirects.
    """
    messages.info(request, 'Schedules are now created automatically when you access the dashboard.')
    return redirect('pm_daily_dashboard')
