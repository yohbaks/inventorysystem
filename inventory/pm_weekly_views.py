"""
Views for Annex C - Weekly Floor/Building Distributors PM Checklist
Schedule: Every Friday for 4 weeks per month (Wk1, Wk2, Wk3, Wk4)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange

from .models import (
    PMChecklistTemplate, PMChecklistItem, PMChecklistSchedule,
    PMChecklistCompletion, PMChecklistItemCompletion
)


@login_required
def weekly_pm_dashboard(request):
    """Dashboard for Annex C Weekly PM Checklist - shows all 4 weeks of current month"""

    # Get Annex C template
    template = get_object_or_404(PMChecklistTemplate, annex_code='C', is_active=True)

    # Get current date
    today = timezone.now().date()
    current_year = today.year
    current_month = today.month

    # Get or create monthly schedule/completion (one per month, tracks all 4 weeks)
    first_day = datetime(current_year, current_month, 1).date()
    last_day = datetime(current_year, current_month, monthrange(current_year, current_month)[1]).date()

    schedule, created = PMChecklistSchedule.objects.get_or_create(
        template=template,
        scheduled_date=first_day,  # Use 1st of month as reference
        defaults={
            'due_date': last_day,  # Due by end of month
            'status': 'PENDING',
            'location': ''  # Will be filled when completing
        }
    )

    # Get or create completion for this month
    try:
        completion = schedule.completion
    except PMChecklistCompletion.DoesNotExist:
        completion = None

    # Get all Fridays in this month
    fridays = get_fridays_in_month(current_year, current_month)

    # Build week status
    weeks = []
    for week_num, friday_date in enumerate(fridays, start=1):
        week_status = {
            'week_number': week_num,
            'friday_date': friday_date,
            'is_past': friday_date < today,
            'is_today': friday_date == today,
            'is_future': friday_date > today,
            'is_completed': False,
            'can_fill': friday_date <= today,  # Can fill current or past weeks
        }

        # Check if this week has been completed
        if completion:
            item_completions = completion.item_completions.all()
            if item_completions.exists():
                # Check if any item has this week marked
                week_field = f'week{week_num}'
                for item_comp in item_completions:
                    if getattr(item_comp, week_field, False):
                        week_status['is_completed'] = True
                        break

        weeks.append(week_status)

    # Calculate overall completion status
    completed_weeks = sum(1 for w in weeks if w['is_completed'])
    total_weeks = len(weeks)
    is_month_complete = completed_weeks == total_weeks and total_weeks > 0

    context = {
        'template': template,
        'schedule': schedule,
        'completion': completion,
        'weeks': weeks,
        'current_month': today.strftime('%B %Y'),
        'completed_weeks': completed_weeks,
        'total_weeks': total_weeks,
        'is_month_complete': is_month_complete,
    }

    return render(request, 'pm/weekly_dashboard.html', context)


@login_required
def complete_weekly_pm(request, schedule_id, week_number):
    """Complete or update a specific week of the monthly PM checklist (Annex C)"""

    schedule = get_object_or_404(PMChecklistSchedule, id=schedule_id)
    template = schedule.template

    # Validate week number
    if week_number < 1 or week_number > 4:
        messages.error(request, 'Invalid week number')
        return redirect('weekly_fdbd_dashboard')

    # Get or create completion for this month
    try:
        completion = schedule.completion
    except PMChecklistCompletion.DoesNotExist:
        completion = None

    # Get all items for this template
    items = PMChecklistItem.objects.filter(template=template, is_active=True).order_by('item_number')

    # Get Friday date for this week
    fridays = get_fridays_in_month(schedule.scheduled_date.year, schedule.scheduled_date.month)
    try:
        friday_date = fridays[week_number - 1]
    except IndexError:
        messages.error(request, f'Week {week_number} does not exist in this month')
        return redirect('weekly_fdbd_dashboard')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create completion if it doesn't exist
                if not completion:
                    completion = PMChecklistCompletion.objects.create(
                        schedule=schedule,
                        completed_by=request.user,
                        completion_date=friday_date,
                        printed_name=request.POST.get('printed_name', '')
                    )
                    schedule.status = 'IN_PROGRESS'
                else:
                    # Update completion
                    completion.completed_by = request.user
                    completion.printed_name = request.POST.get('printed_name', '')
                    completion.save()

                # Update location if provided
                location = request.POST.get('location', '').strip()
                if location:
                    schedule.location = location
                    schedule.save()

                # Week field name (week1, week2, week3, week4)
                week_field = f'week{week_number}'

                # Update or create item completions
                for item in items:
                    # Check if item was completed (checkbox checked)
                    item_key = f'item_{item.id}'
                    is_completed = request.POST.get(item_key) == 'on'

                    # Problems and action (shared across all weeks)
                    problems = request.POST.get(f'problems_{item.id}', '').strip()
                    action = request.POST.get(f'action_{item.id}', '').strip()

                    # Get or create item completion
                    item_comp, created = PMChecklistItemCompletion.objects.get_or_create(
                        completion=completion,
                        item=item,
                        defaults={
                            'problems_encountered': problems,
                            'action_taken': action,
                        }
                    )

                    # Set the week field
                    setattr(item_comp, week_field, is_completed)

                    # Update problems/action if provided (append if already exists)
                    if problems:
                        if item_comp.problems_encountered:
                            item_comp.problems_encountered += f"\n[Week {week_number}] {problems}"
                        else:
                            item_comp.problems_encountered = f"[Week {week_number}] {problems}"

                    if action:
                        if item_comp.action_taken:
                            item_comp.action_taken += f"\n[Week {week_number}] {action}"
                        else:
                            item_comp.action_taken = f"[Week {week_number}] {action}"

                    item_comp.save()

                # Check if all weeks are complete
                all_weeks_complete = True
                total_fridays = len(fridays)
                for wk in range(1, total_fridays + 1):
                    week_check = f'week{wk}'
                    week_has_data = False
                    for item_comp in completion.item_completions.all():
                        if getattr(item_comp, week_check, False):
                            week_has_data = True
                            break
                    if not week_has_data:
                        all_weeks_complete = False
                        break

                if all_weeks_complete:
                    schedule.status = 'COMPLETED'
                else:
                    schedule.status = 'IN_PROGRESS'
                schedule.save()

                messages.success(request, f'Week {week_number} of {schedule.scheduled_date.strftime("%B %Y")} completed successfully!')
                return redirect('weekly_fdbd_dashboard')

        except Exception as e:
            messages.error(request, f'Error completing checklist: {str(e)}')
            return redirect('complete_weekly_pm', schedule_id=schedule_id, week_number=week_number)

    # Pre-populate form with existing data if available
    week_field = f'week{week_number}'
    if completion:
        item_completions_dict = {ic.item.id: ic for ic in completion.item_completions.all()}
        for item in items:
            if item.id in item_completions_dict:
                item_comp = item_completions_dict[item.id]
                item.is_checked = getattr(item_comp, week_field, False)
                item.existing_problems = item_comp.problems_encountered or ''
                item.existing_action = item_comp.action_taken or ''
            else:
                item.is_checked = False
                item.existing_problems = ''
                item.existing_action = ''
    else:
        for item in items:
            item.is_checked = False
            item.existing_problems = ''
            item.existing_action = ''

    # Get smart suggestions (water leaks from daily checklist)
    smart_suggestions = get_weekly_smart_suggestions(friday_date)

    context = {
        'schedule': schedule,
        'template': template,
        'items': items,
        'completion': completion,
        'week_number': week_number,
        'friday_date': friday_date,
        'month_name': schedule.scheduled_date.strftime('%B %Y'),
        'existing_location': schedule.location,
        'smart_suggestions': smart_suggestions,
    }

    return render(request, 'pm/complete_weekly_pm.html', context)


def get_fridays_in_month(year, month):
    """Get all Friday dates in a given month"""
    fridays = []
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, monthrange(year, month)[1]).date()

    # Start from first day and find all Fridays
    current = first_day
    while current <= last_day:
        if current.weekday() == 4:  # 4 = Friday
            fridays.append(current)
        current += timedelta(days=1)

    return fridays


def get_weekly_smart_suggestions(friday_date):
    """Get smart suggestions from daily data for weekly checklist"""

    suggestions = {
        'has_water_leaks': False,
        'water_leak_dates': [],
        'summary': ''
    }

    try:
        # Get Annex A (Daily) template
        daily_template = PMChecklistTemplate.objects.get(annex_code='A', is_active=True)

        # Get the week range (Monday to Friday of this week)
        # friday_date is the Friday, so go back 4 days to get Monday
        monday_date = friday_date - timedelta(days=4)

        # Get daily completions for this week
        daily_schedules = PMChecklistSchedule.objects.filter(
            template=daily_template,
            scheduled_date__gte=monday_date,
            scheduled_date__lte=friday_date,
            status='COMPLETED'
        )

        # Check Item #8 (water leaks) from daily checklists
        for schedule in daily_schedules:
            try:
                completion = schedule.completion
                item_completions = completion.item_completions.all()

                for item_comp in item_completions:
                    # Item #8: Check for signs of water leaks
                    if item_comp.item.item_number == 8:
                        if item_comp.problems_encountered or 'leak' in (item_comp.action_taken or '').lower():
                            suggestions['has_water_leaks'] = True
                            suggestions['water_leak_dates'].append(schedule.scheduled_date.strftime('%b %d'))
            except:
                pass

        # Build summary
        if suggestions['has_water_leaks']:
            dates_str = ', '.join(suggestions['water_leak_dates'])
            suggestions['summary'] = f"Water leaks reported on: {dates_str} (from daily checklists)"
        else:
            suggestions['summary'] = "No water leaks reported in datacenter this week"

    except Exception as e:
        suggestions['summary'] = "Unable to retrieve daily checklist data"

    return suggestions
