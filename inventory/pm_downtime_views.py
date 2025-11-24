"""
Views for Equipment Downtime Logging and Analytics
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, Avg

from .models import (
    EquipmentDowntimeEvent, PMChecklistItemCompletion,
    PMChecklistItem, PMChecklistTemplate
)


@login_required
@require_POST
def log_downtime_event(request, item_completion_id):
    """Log a new downtime event for a checklist item"""

    item_completion = get_object_or_404(PMChecklistItemCompletion, id=item_completion_id)

    try:
        # Get form data
        occurrence_date = request.POST.get('occurrence_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time', None)
        equipment_name = request.POST.get('equipment_name')
        severity = request.POST.get('severity', 'MODERATE')
        cause_description = request.POST.get('cause_description')
        resolution_notes = request.POST.get('resolution_notes', '')
        services_affected = request.POST.get('services_affected', '')
        users_affected = request.POST.get('users_affected_count', None)

        # Create downtime event
        downtime_event = EquipmentDowntimeEvent.objects.create(
            item_completion=item_completion,
            occurrence_date=datetime.strptime(occurrence_date, '%Y-%m-%d').date(),
            start_time=datetime.strptime(start_time, '%H:%M').time(),
            end_time=datetime.strptime(end_time, '%H:%M').time() if end_time else None,
            equipment_name=equipment_name,
            severity=severity,
            cause_description=cause_description,
            resolution_notes=resolution_notes,
            services_affected=services_affected,
            users_affected_count=int(users_affected) if users_affected else None,
            reported_by=request.user
        )

        # Auto-populate the Problems field with downtime summary
        downtime_summary = f"DOWNTIME: {downtime_event.occurrence_date} {downtime_event.start_time.strftime('%H:%M')}"
        if downtime_event.end_time:
            downtime_summary += f" - {downtime_event.end_time.strftime('%H:%M')}"
        downtime_summary += f" | {equipment_name} | {severity} | {cause_description}"

        # Append to existing problems or create new
        if item_completion.problems_encountered:
            item_completion.problems_encountered += f"\n\n{downtime_summary}"
        else:
            item_completion.problems_encountered = downtime_summary

        item_completion.save()

        messages.success(request, f'Downtime event logged: {downtime_event.get_duration_display()} downtime for {equipment_name}')

        return JsonResponse({
            'success': True,
            'message': 'Downtime event logged successfully',
            'duration': downtime_event.get_duration_display(),
            'event_id': downtime_event.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def downtime_analytics_dashboard(request):
    """Analytics dashboard showing downtime trends and statistics"""

    # Date range (default: last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    date_from = request.GET.get('date_from', start_date.strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))

    start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
    end_date = datetime.strptime(date_to, '%Y-%m-%d').date()

    # Get all downtime events in range
    downtime_events = EquipmentDowntimeEvent.objects.filter(
        occurrence_date__gte=start_date,
        occurrence_date__lte=end_date
    ).select_related('item_completion__item', 'reported_by')

    # Calculate statistics
    total_events = downtime_events.count()
    total_downtime_minutes = downtime_events.aggregate(
        total=Sum('duration_minutes')
    )['total'] or 0

    # Convert to hours
    total_downtime_hours = total_downtime_minutes / 60

    # Events by severity
    severity_breakdown = downtime_events.values('severity').annotate(
        count=Count('id'),
        total_duration=Sum('duration_minutes')
    ).order_by('-count')

    # Events by equipment
    equipment_breakdown = downtime_events.values('equipment_name').annotate(
        count=Count('id'),
        total_duration=Sum('duration_minutes')
    ).order_by('-count')[:10]  # Top 10

    # Events by day (for chart)
    # Use occurrence_date directly instead of TruncDate for better SQLite compatibility
    daily_breakdown = downtime_events.values('occurrence_date').annotate(
        count=Count('id'),
        total_duration=Sum('duration_minutes')
    ).order_by('occurrence_date')

    # Recent critical events
    critical_events = downtime_events.filter(
        severity='CRITICAL'
    ).order_by('-occurrence_date', '-start_time')[:5]

    # Average resolution time
    avg_duration = downtime_events.filter(
        duration_minutes__isnull=False
    ).aggregate(avg=Avg('duration_minutes'))['avg'] or 0

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_events': total_events,
        'total_downtime_hours': round(total_downtime_hours, 2),
        'avg_duration_minutes': round(avg_duration, 2),
        'severity_breakdown': severity_breakdown,
        'equipment_breakdown': equipment_breakdown,
        'daily_breakdown': daily_breakdown,
        'critical_events': critical_events,
        'recent_events': downtime_events.order_by('-occurrence_date', '-start_time')[:20],
    }

    return render(request, 'pm/downtime_analytics.html', context)
