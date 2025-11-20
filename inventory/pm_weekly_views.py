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
    """Get comprehensive smart suggestions from daily data for all weekly items"""

    suggestions = {
        # Item #1: Equipment Running
        'item1': {
            'has_issues': False,
            'equipment_checks': [],  # {date, status, details}
            'total_checks': 0,
            'issues_count': 0,
            'summary': '',
            'suggested_action': ''
        },

        # Item #2: Water Leaks
        'item2': {
            'has_water_leaks': False,
            'leak_incidents': [],  # {date, location, severity, action}
            'total_incidents': 0,
            'summary': '',
            'suggested_action': ''
        },

        # Item #3: FD/BD Security
        'item3': {
            'summary': '',
            'suggested_action': 'Verify all FD/BD doors are properly locked and secured'
        },

        # Item #4: Obstructions
        'item4': {
            'has_previous_notes': False,
            'previous_obstructions': [],  # From previous weeks
            'summary': '',
            'suggested_action': ''
        },

        # Overall
        'has_any_alerts': False,
        'overall_summary': '',
        'week_date_range': ''
    }

    try:
        # Get Annex A (Daily) template
        daily_template = PMChecklistTemplate.objects.get(annex_code='A', is_active=True)

        # Get the week range (Monday to Friday of this week)
        monday_date = friday_date - timedelta(days=4)
        suggestions['week_date_range'] = f"{monday_date.strftime('%b %d')} - {friday_date.strftime('%b %d')}"

        # Get daily completions for this week
        daily_schedules = PMChecklistSchedule.objects.filter(
            template=daily_template,
            scheduled_date__gte=monday_date,
            scheduled_date__lte=friday_date,
            status='COMPLETED'
        ).order_by('scheduled_date')

        total_days_checked = daily_schedules.count()

        # Analyze daily checklists for this week
        for schedule in daily_schedules:
            try:
                completion = schedule.completion
                item_completions = completion.item_completions.all()
                date_str = schedule.scheduled_date.strftime('%b %d (%a)')

                for item_comp in item_completions:
                    # Item #2: Check if servers/network equipment are up (for Item #1 suggestion)
                    if item_comp.item.item_number == 2:
                        status = 'Running' if item_comp.is_completed else 'Issue'
                        details = item_comp.problems_encountered or 'All equipment operational'

                        suggestions['item1']['equipment_checks'].append({
                            'date': date_str,
                            'status': status,
                            'details': details
                        })
                        suggestions['item1']['total_checks'] += 1

                        if item_comp.problems_encountered or not item_comp.is_completed:
                            suggestions['item1']['has_issues'] = True
                            suggestions['item1']['issues_count'] += 1

                    # Item #8: Check for water leaks (for Item #2 suggestion)
                    if item_comp.item.item_number == 8:
                        problems = item_comp.problems_encountered or ''
                        action = item_comp.action_taken or ''

                        # Check for leak-related keywords
                        leak_keywords = ['leak', 'water', 'moisture', 'wet', 'drip', 'flood']
                        has_leak = any(keyword in problems.lower() or keyword in action.lower()
                                      for keyword in leak_keywords)

                        if has_leak or problems:
                            # Determine severity
                            severity = 'Critical' if any(kw in problems.lower() for kw in ['flood', 'major']) else 'Minor'

                            suggestions['item2']['leak_incidents'].append({
                                'date': date_str,
                                'location': 'FD/BD area',  # Could be enhanced with location parsing
                                'severity': severity,
                                'details': problems or 'Leak detected',
                                'action': action or 'None recorded'
                            })
                            suggestions['item2']['has_water_leaks'] = True
                            suggestions['item2']['total_incidents'] += 1

            except Exception as e:
                continue

        # === Process Item #1 (Equipment Running) ===
        if suggestions['item1']['has_issues']:
            suggestions['item1']['summary'] = f"⚠️ Equipment issues on {suggestions['item1']['issues_count']} day(s) this week"
            suggestions['item1']['suggested_action'] = (
                "Verify all FD/BD equipment is powered on and running. "
                "Check for tripped breakers or disconnected cables. "
                "Review equipment status indicators."
            )
        else:
            if suggestions['item1']['total_checks'] > 0:
                suggestions['item1']['summary'] = f"✓ All equipment running normally ({suggestions['item1']['total_checks']} checks)"
            else:
                suggestions['item1']['summary'] = "No equipment data available for this week"
            suggestions['item1']['suggested_action'] = "Visual inspection: Verify all equipment power and status lights"

        # === Process Item #2 (Water Leaks) ===
        if suggestions['item2']['has_water_leaks']:
            critical_count = sum(1 for incident in suggestions['item2']['leak_incidents']
                               if incident['severity'] == 'Critical')

            if critical_count > 0:
                suggestions['item2']['summary'] = f"🚨 CRITICAL: {critical_count} major leak(s) detected this week!"
            else:
                suggestions['item2']['summary'] = f"⚠️ {suggestions['item2']['total_incidents']} leak incident(s) detected"

            suggestions['item2']['suggested_action'] = (
                "IMMEDIATE: Check all FD/BD areas for signs of water. "
                "Inspect ceiling, walls, and floor for moisture. "
                "Check AC units and plumbing for leaks. "
                "Report to facilities immediately if found."
            )
        else:
            suggestions['item2']['summary'] = f"✓ No water leaks reported ({total_days_checked} daily checks)"
            suggestions['item2']['suggested_action'] = "Routine inspection: Check for any signs of moisture or water damage"

        # === Process Item #3 (FD/BD Locked) ===
        suggestions['item3']['summary'] = "Verify all FD/BD enclosures are properly secured"

        # === Process Item #4 (Obstructions) ===
        # Get previous week's data from the same monthly schedule
        try:
            weekly_template = PMChecklistTemplate.objects.get(annex_code='C', is_active=True)
            year = friday_date.year
            month = friday_date.month
            first_day_of_month = datetime(year, month, 1).date()

            previous_schedule = PMChecklistSchedule.objects.filter(
                template=weekly_template,
                scheduled_date=first_day_of_month
            ).first()

            if previous_schedule and hasattr(previous_schedule, 'completion'):
                prev_completion = previous_schedule.completion
                # Look for item #4 completions from previous weeks
                for item_comp in prev_completion.item_completions.all():
                    if item_comp.item.item_number == 4:
                        # Check previous weeks for obstruction notes
                        for wk in range(1, 5):
                            week_field = f'week{wk}'
                            problems = item_comp.problems_encountered or ''
                            if getattr(item_comp, week_field, False) and 'obstruction' in problems.lower():
                                suggestions['item4']['has_previous_notes'] = True
                                suggestions['item4']['previous_obstructions'].append({
                                    'week': wk,
                                    'details': problems
                                })

            if suggestions['item4']['has_previous_notes']:
                suggestions['item4']['summary'] = f"⚠️ Previous obstruction(s) noted - verify cleared"
                suggestions['item4']['suggested_action'] = (
                    "Check previous obstruction locations are now clear. "
                    "Inspect top, sides, and back of all FD/BD units. "
                    "Remove any boxes, equipment, or debris blocking airflow."
                )
            else:
                suggestions['item4']['summary'] = "Routine check: Ensure clear access and airflow"
                suggestions['item4']['suggested_action'] = (
                    "Verify minimum 3-foot clearance around all equipment. "
                    "Remove any stored items or obstructions. "
                    "Check ventilation paths are clear."
                )

        except Exception as e:
            suggestions['item4']['summary'] = "Check for any obstructions around equipment"
            suggestions['item4']['suggested_action'] = "Clear all obstructions from FD/BD areas"

        # === Overall Summary ===
        suggestions['has_any_alerts'] = (
            suggestions['item1']['has_issues'] or
            suggestions['item2']['has_water_leaks'] or
            suggestions['item4']['has_previous_notes']
        )

        if suggestions['has_any_alerts']:
            alert_parts = []
            if suggestions['item1']['has_issues']:
                alert_parts.append(f"{suggestions['item1']['issues_count']} equipment issue(s)")
            if suggestions['item2']['has_water_leaks']:
                alert_parts.append(f"{suggestions['item2']['total_incidents']} water leak(s)")
            if suggestions['item4']['has_previous_notes']:
                alert_parts.append("previous obstructions")

            suggestions['overall_summary'] = f"⚠️ Alerts: {', '.join(alert_parts)}"
        else:
            suggestions['overall_summary'] = f"✓ All normal for week of {suggestions['week_date_range']}"

    except Exception as e:
        suggestions['overall_summary'] = f"Unable to retrieve checklist data: {str(e)}"

    return suggestions
