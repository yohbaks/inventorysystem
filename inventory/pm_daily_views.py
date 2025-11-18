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

    # Get or create today's schedule
    schedule, created = PMChecklistSchedule.objects.get_or_create(
        template=template,
        scheduled_date=today,
        defaults={
            'due_date': today,
            'status': 'PENDING',
            'assigned_to': request.user
        }
    )

    # Check if already completed today
    try:
        completion = PMChecklistCompletion.objects.get(schedule=schedule)
        is_completed = True
    except PMChecklistCompletion.DoesNotExist:
        completion = None
        is_completed = False

    # Get this week's completions for progress tracking
    monday, friday = get_week_start_end(today)
    week_completions = get_week_completions(template, today)

    # Days completed this week
    days_completed = {
        'monday': 0 in week_completions,
        'tuesday': 1 in week_completions,
        'wednesday': 2 in week_completions,
        'thursday': 3 in week_completions,
        'friday': 4 in week_completions,
    }

    context = {
        'is_weekend': False,
        'today': today,
        'today_name': today.strftime('%A'),
        'template': template,
        'schedule': schedule,
        'completion': completion,
        'is_completed': is_completed,
        'days_completed': days_completed,
        'monday': monday,
        'friday': friday,
    }

    return render(request, 'pm/daily_dashboard.html', context)


@login_required
def complete_daily_pm(request, schedule_id):
    """Complete today's PM checklist"""

    schedule = get_object_or_404(PMChecklistSchedule, id=schedule_id)
    template = schedule.template

    # Check if already completed
    if hasattr(schedule, 'completion'):
        messages.warning(request, 'This checklist has already been completed.')
        return redirect('pm_daily_dashboard')

    # Get all items for this template
    items = PMChecklistItem.objects.filter(template=template, is_active=True).order_by('item_number')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create completion
                completion = PMChecklistCompletion.objects.create(
                    schedule=schedule,
                    completed_by=request.user,
                    completion_date=schedule.scheduled_date,
                    printed_name=request.POST.get('printed_name', '')
                )

                # Determine which day field to use
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
                    item_key = f'item_{item.id}'
                    is_completed = request.POST.get(item_key) == 'on'

                    # Problems and actions
                    problems = request.POST.get(f'problems_{item.id}', '').strip()
                    action = request.POST.get(f'action_{item.id}', '').strip()

                    # Create item completion
                    item_completion_data = {
                        'completion': completion,
                        'item': item,
                        'problems_encountered': problems,
                        'action_taken': action,
                    }

                    # Set the appropriate day boolean
                    if day_field:
                        item_completion_data[day_field] = is_completed

                    PMChecklistItemCompletion.objects.create(**item_completion_data)

                # Update schedule status
                schedule.status = 'COMPLETED'
                schedule.save()

                messages.success(request, f'Daily PM checklist for {schedule.scheduled_date.strftime("%A, %B %d")} completed successfully!')
                return redirect('pm_daily_dashboard')

        except Exception as e:
            messages.error(request, f'Error completing checklist: {str(e)}')
            return redirect('complete_daily_pm', schedule_id=schedule_id)

    context = {
        'schedule': schedule,
        'template': template,
        'items': items,
        'today': schedule.scheduled_date,
        'today_name': schedule.scheduled_date.strftime('%A'),
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

    return render(request, 'pm/view_daily_completion.html', context)


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
    Admin function to create PM schedules for the current week (Mon-Fri only)
    This should be called at the start of each week
    """

    if not request.user.is_staff:
        messages.error(request, 'Only staff can create schedules.')
        return redirect('pm_daily_dashboard')

    # Get Annex A template
    try:
        template = PMChecklistTemplate.objects.get(annex_code='A')
    except PMChecklistTemplate.DoesNotExist:
        messages.error(request, 'PM Checklist template not found.')
        return redirect('pm_daily_dashboard')

    # Get current week's Monday
    today = timezone.now().date()
    monday, friday = get_week_start_end(today)

    created_count = 0

    # Create schedules for Mon-Fri only
    for day_offset in range(5):  # 0=Monday to 4=Friday
        schedule_date = monday + timedelta(days=day_offset)

        schedule, created = PMChecklistSchedule.objects.get_or_create(
            template=template,
            scheduled_date=schedule_date,
            defaults={
                'due_date': schedule_date,
                'status': 'PENDING',
                'assigned_to': request.user
            }
        )

        if created:
            created_count += 1

    messages.success(request, f'Created {created_count} schedules for week of {monday.strftime("%B %d")} - {friday.strftime("%B %d, %Y")}')
    return redirect('pm_daily_dashboard')
