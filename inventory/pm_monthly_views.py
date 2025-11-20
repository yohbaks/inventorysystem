"""
Views for Annex B - Monthly Datacenter PM Checklist
Schedule: 1st week of each month
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
def monthly_pm_dashboard(request):
    """Dashboard for Annex B Monthly PM Checklist"""

    # Get Annex B template
    template = get_object_or_404(PMChecklistTemplate, annex_code='B', is_active=True)

    # Get current date
    today = timezone.now().date()
    current_year = today.year
    current_month = today.month

    # Get or create schedule for current month (1st day of month)
    first_day = datetime(current_year, current_month, 1).date()
    last_day = datetime(current_year, current_month, monthrange(current_year, current_month)[1]).date()

    # Due date is end of 1st week (7th day of month)
    due_date = datetime(current_year, current_month, min(7, monthrange(current_year, current_month)[1])).date()

    schedule, created = PMChecklistSchedule.objects.get_or_create(
        template=template,
        scheduled_date=first_day,
        defaults={
            'due_date': due_date,
            'status': 'PENDING'
        }
    )

    # Check if completed
    try:
        completion = schedule.completion
        is_completed = True
    except PMChecklistCompletion.DoesNotExist:
        completion = None
        is_completed = False

    # Get smart suggestions from daily data (Item #1)
    smart_suggestions = get_monthly_smart_suggestions(current_year, current_month)

    context = {
        'template': template,
        'schedule': schedule,
        'completion': completion,
        'is_completed': is_completed,
        'current_month': today.strftime('%B %Y'),
        'first_day': first_day,
        'due_date': due_date,
        'is_overdue': schedule.is_overdue(),
        'smart_suggestions': smart_suggestions,
    }

    return render(request, 'pm/monthly_dashboard.html', context)


@login_required
def complete_monthly_pm(request, schedule_id):
    """Complete or update monthly PM checklist (Annex B)"""

    schedule = get_object_or_404(PMChecklistSchedule, id=schedule_id)
    template = schedule.template

    # Check if already completed - allow editing
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
                        completion_date=timezone.now().date(),
                        printed_name=request.POST.get('printed_name', '')
                    )

                # Create item completions
                for item in items:
                    # Check if item was completed (checkbox checked)
                    item_key = f'item_{item.id}'
                    is_completed = request.POST.get(item_key) == 'on'

                    # Problems and action
                    problems = request.POST.get(f'problems_{item.id}', '').strip()
                    action = request.POST.get(f'action_{item.id}', '').strip()

                    PMChecklistItemCompletion.objects.create(
                        completion=completion,
                        item=item,
                        is_completed=is_completed,
                        problems_encountered=problems,
                        action_taken=action
                    )

                # Update schedule status
                schedule.status = 'COMPLETED'
                schedule.save()

                messages.success(request, f'Monthly PM checklist for {schedule.scheduled_date.strftime("%B %Y")} completed successfully!')
                return redirect('monthly_pm_dashboard')

        except Exception as e:
            messages.error(request, f'Error completing checklist: {str(e)}')
            return redirect('complete_monthly_pm', schedule_id=schedule_id)

    # Pre-populate form with existing data if available
    if existing_completion:
        item_completions_dict = {ic.item.id: ic for ic in existing_completion.item_completions.all()}
        for item in items:
            if item.id in item_completions_dict:
                item_comp = item_completions_dict[item.id]
                item.is_checked = item_comp.is_completed
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

    # Get smart suggestions
    smart_suggestions = get_monthly_smart_suggestions(schedule.scheduled_date.year, schedule.scheduled_date.month)

    context = {
        'schedule': schedule,
        'template': template,
        'items': items,
        'existing_completion': existing_completion,
        'month_name': schedule.scheduled_date.strftime('%B %Y'),
        'smart_suggestions': smart_suggestions,
    }

    return render(request, 'pm/complete_monthly_pm.html', context)


def get_monthly_smart_suggestions(year, month):
    """Get smart suggestions from daily data for monthly Item #1"""

    suggestions = {
        'has_critical_alerts': False,
        'server_issues_count': 0,
        'event_log_errors_count': 0,
        'summary': ''
    }

    try:
        # Get Annex A (Daily) template
        daily_template = PMChecklistTemplate.objects.get(annex_code='A', is_active=True)

        # Get all daily completions for this month
        first_day = datetime(year, month, 1).date()
        last_day = datetime(year, month, monthrange(year, month)[1]).date()

        daily_schedules = PMChecklistSchedule.objects.filter(
            template=daily_template,
            scheduled_date__gte=first_day,
            scheduled_date__lte=last_day,
            status='COMPLETED'
        )

        # Check Item #2 (servers) and Item #7 (event logs) from daily checklists
        for schedule in daily_schedules:
            try:
                completion = schedule.completion
                item_completions = completion.item_completions.all()

                for item_comp in item_completions:
                    # Item #2: Check if servers are up
                    if item_comp.item.item_number == 2:
                        if item_comp.problems_encountered:
                            suggestions['server_issues_count'] += 1
                            suggestions['has_critical_alerts'] = True

                    # Item #7: Event logs for critical warnings/errors
                    if item_comp.item.item_number == 7:
                        if item_comp.problems_encountered or 'error' in (item_comp.action_taken or '').lower() or 'critical' in (item_comp.action_taken or '').lower():
                            suggestions['event_log_errors_count'] += 1
                            suggestions['has_critical_alerts'] = True
            except:
                pass

        # Build summary
        if suggestions['has_critical_alerts']:
            parts = []
            if suggestions['server_issues_count'] > 0:
                parts.append(f"{suggestions['server_issues_count']} server issue(s)")
            if suggestions['event_log_errors_count'] > 0:
                parts.append(f"{suggestions['event_log_errors_count']} event log error(s)")
            suggestions['summary'] = f"Found {', '.join(parts)} in daily checklists this month"
        else:
            suggestions['summary'] = "No critical alerts found in daily checklists this month"

    except Exception as e:
        suggestions['summary'] = "Unable to retrieve daily checklist data"

    return suggestions
