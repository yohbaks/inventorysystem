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
    """Get comprehensive smart suggestions from daily data for all monthly items"""

    suggestions = {
        # Item #1: Network Equipment Alerts
        'item1': {
            'has_alerts': False,
            'server_issues': [],  # {date, details, action}
            'event_log_errors': [],  # {date, details, action}
            'total_alerts': 0,
            'severity': 'low',  # low, medium, high
            'summary': '',
            'suggested_action': ''
        },

        # Item #3: UPS Health
        'item3': {
            'has_issues': False,
            'ups_readings': [],  # {date, status, notes}
            'trend': 'stable',  # improving, stable, degrading
            'average_health': 100,
            'summary': '',
            'suggested_action': ''
        },

        # Item #4: Generator Status
        'item4': {
            'has_issues': False,
            'generator_readings': [],  # {date, status, notes}
            'last_test_date': None,
            'tests_this_month': 0,
            'summary': '',
            'suggested_action': ''
        },

        # Overall
        'has_any_alerts': False,
        'overall_summary': ''
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
        ).order_by('scheduled_date')

        total_days_checked = daily_schedules.count()
        ups_health_values = []

        # Analyze daily checklists
        for schedule in daily_schedules:
            try:
                completion = schedule.completion
                item_completions = completion.item_completions.all()
                date_str = schedule.scheduled_date.strftime('%b %d')

                for item_comp in item_completions:
                    # Item #2: Servers/Network Equipment
                    if item_comp.item.item_number == 2:
                        if item_comp.problems_encountered or not item_comp.is_completed:
                            suggestions['item1']['server_issues'].append({
                                'date': date_str,
                                'details': item_comp.problems_encountered or 'Not completed',
                                'action': item_comp.action_taken or 'None recorded'
                            })
                            suggestions['item1']['has_alerts'] = True
                            suggestions['item1']['total_alerts'] += 1

                    # Item #7: Event Logs
                    if item_comp.item.item_number == 7:
                        problems = item_comp.problems_encountered or ''
                        action = item_comp.action_taken or ''

                        # Check for critical keywords
                        critical_keywords = ['error', 'critical', 'warning', 'failed', 'alert']
                        is_critical = any(keyword in problems.lower() or keyword in action.lower()
                                        for keyword in critical_keywords)

                        if is_critical or problems:
                            suggestions['item1']['event_log_errors'].append({
                                'date': date_str,
                                'details': problems or 'Critical event detected',
                                'action': action or 'None recorded'
                            })
                            suggestions['item1']['has_alerts'] = True
                            suggestions['item1']['total_alerts'] += 1

                    # Item #3: UPS Readings
                    if item_comp.item.item_number == 3:
                        status = 'Good' if item_comp.is_completed else 'Issue'
                        notes = item_comp.problems_encountered or 'Normal operation'

                        suggestions['item3']['ups_readings'].append({
                            'date': date_str,
                            'status': status,
                            'notes': notes
                        })

                        if item_comp.problems_encountered or not item_comp.is_completed:
                            suggestions['item3']['has_issues'] = True

                        # Track health (assume 100% if completed with no issues)
                        health = 100 if (item_comp.is_completed and not item_comp.problems_encountered) else 70
                        ups_health_values.append(health)

                    # Item #4: Generator Check
                    if item_comp.item.item_number == 4:
                        status = 'Operational' if item_comp.is_completed else 'Issue'
                        notes = item_comp.problems_encountered or 'Normal operation'

                        suggestions['item4']['generator_readings'].append({
                            'date': date_str,
                            'status': status,
                            'notes': notes
                        })

                        if item_comp.is_completed:
                            suggestions['item4']['tests_this_month'] += 1
                            suggestions['item4']['last_test_date'] = date_str

                        if item_comp.problems_encountered or not item_comp.is_completed:
                            suggestions['item4']['has_issues'] = True

            except Exception as e:
                continue

        # === Process Item #1 (Network Equipment) ===
        if suggestions['item1']['total_alerts'] > 0:
            suggestions['item1']['severity'] = 'high' if suggestions['item1']['total_alerts'] > 5 else 'medium'

            # Build detailed summary
            parts = []
            if suggestions['item1']['server_issues']:
                parts.append(f"{len(suggestions['item1']['server_issues'])} server/network issue(s)")
            if suggestions['item1']['event_log_errors']:
                parts.append(f"{len(suggestions['item1']['event_log_errors'])} event log alert(s)")

            suggestions['item1']['summary'] = f"⚠️ Found {', '.join(parts)} in {total_days_checked} daily checks"

            # Suggested action
            suggestions['item1']['suggested_action'] = (
                "Review all network equipment for hardware alarms. "
                "Check router, switches, and servers for critical warnings. "
                "Verify all critical systems are operational."
            )
        else:
            suggestions['item1']['summary'] = f"✓ No critical network alerts in {total_days_checked} daily checks"
            suggestions['item1']['suggested_action'] = "Routine check: Verify status lights and monitoring dashboard"

        # === Process Item #3 (UPS) ===
        if ups_health_values:
            suggestions['item3']['average_health'] = sum(ups_health_values) / len(ups_health_values)

            # Determine trend (compare first half vs second half)
            if len(ups_health_values) >= 4:
                mid = len(ups_health_values) // 2
                first_half_avg = sum(ups_health_values[:mid]) / mid
                second_half_avg = sum(ups_health_values[mid:]) / (len(ups_health_values) - mid)

                if second_half_avg > first_half_avg + 5:
                    suggestions['item3']['trend'] = 'improving'
                elif second_half_avg < first_half_avg - 5:
                    suggestions['item3']['trend'] = 'degrading'
                else:
                    suggestions['item3']['trend'] = 'stable'

        if suggestions['item3']['has_issues']:
            suggestions['item3']['summary'] = f"⚠️ UPS issues detected ({suggestions['item3']['trend']} trend)"
            suggestions['item3']['suggested_action'] = (
                "Test UPS battery backup for minimum 5 minutes runtime. "
                "Check battery levels and replace if needed. "
                "Verify UPS alarm indicators."
            )
        else:
            suggestions['item3']['summary'] = f"✓ UPS operating normally ({suggestions['item3']['trend']} trend, {suggestions['item3']['average_health']:.0f}% health)"
            suggestions['item3']['suggested_action'] = "Perform routine 5-minute backup power test"

        # === Process Item #4 (Generator) ===
        if suggestions['item4']['has_issues']:
            suggestions['item4']['summary'] = f"⚠️ Generator issues detected (tested {suggestions['item4']['tests_this_month']}x this month)"
            suggestions['item4']['suggested_action'] = (
                "Coordinate with General Services to test generator and ATS. "
                "Verify generator can supply adequate backup power. "
                "Check fuel levels and battery charge."
            )
        else:
            if suggestions['item4']['tests_this_month'] > 0:
                suggestions['item4']['summary'] = f"✓ Generator operational (last test: {suggestions['item4']['last_test_date']})"
            else:
                suggestions['item4']['summary'] = "⚠️ No generator tests recorded this month"

            suggestions['item4']['suggested_action'] = "Test generator set and ATS with Equipment Management/General Services"

        # === Overall Summary ===
        suggestions['has_any_alerts'] = (
            suggestions['item1']['has_alerts'] or
            suggestions['item3']['has_issues'] or
            suggestions['item4']['has_issues']
        )

        alert_count = (
            len(suggestions['item1']['server_issues']) +
            len(suggestions['item1']['event_log_errors'])
        )

        if suggestions['has_any_alerts']:
            suggestions['overall_summary'] = f"⚠️ {alert_count} alert(s) require attention this month"
        else:
            suggestions['overall_summary'] = f"✓ All systems normal across {total_days_checked} daily checks"

    except Exception as e:
        suggestions['overall_summary'] = f"Unable to retrieve daily checklist data: {str(e)}"

    return suggestions
