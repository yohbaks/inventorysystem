from .models import PMScheduleAssignment, DesktopDetails

def pending_pm_notifications(request):
    from .models import PMScheduleAssignment, DesktopDetails

    pending_pm = PMScheduleAssignment.objects.filter(is_completed=False).select_related('desktop_package')
    for assignment in pending_pm:
        desktop_detail = DesktopDetails.objects.filter(desktop_package=assignment.desktop_package).first()
        if desktop_detail:
            assignment.computer_name = desktop_detail.computer_name
        else:
            assignment.computer_name = f"Desktop #{assignment.desktop_package.id}"

    return {
        'pending_pm_count': pending_pm.count(),
        'pending_pm_list': pending_pm[:5],
    }
