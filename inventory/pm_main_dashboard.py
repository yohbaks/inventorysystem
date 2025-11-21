"""
Main PM Dashboard - Shows all PM checklist forms
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import PMChecklistTemplate


@login_required
def pm_main_dashboard(request):
    """Main PM Dashboard showing all PM checklist templates"""

    # Get all active PM templates
    templates = PMChecklistTemplate.objects.filter(is_active=True).order_by('annex_code')

    # Organize templates by annex code
    pm_forms = []
    for template in templates:
        form_info = {
            'template': template,
            'annex_code': template.annex_code,
            'title': template.title,
            'description': template.description,
            'frequency': template.get_frequency_display(),
            'schedule_note': template.schedule_note,
        }

        # Set dashboard URL based on annex code
        if template.annex_code == 'A':
            form_info['dashboard_url'] = 'pm_daily_dashboard'
            form_info['icon'] = 'fa-calendar-day'
            form_info['color'] = 'primary'
        elif template.annex_code == 'B':
            form_info['dashboard_url'] = 'monthly_pm_dashboard'
            form_info['icon'] = 'fa-calendar-alt'
            form_info['color'] = 'success'
        elif template.annex_code == 'C':
            form_info['dashboard_url'] = 'weekly_fdbd_dashboard'
            form_info['icon'] = 'fa-calendar-week'
            form_info['color'] = 'info'
        elif template.annex_code == 'F':
            form_info['dashboard_url'] = '#'  # TODO: Semi-annual not implemented yet
            form_info['icon'] = 'fa-calendar'
            form_info['color'] = 'warning'
        else:
            form_info['dashboard_url'] = '#'
            form_info['icon'] = 'fa-clipboard-list'
            form_info['color'] = 'secondary'

        pm_forms.append(form_info)

    context = {
        'pm_forms': pm_forms,
        'today': timezone.now().date(),
    }

    return render(request, 'pm/main_dashboard.html', context)
