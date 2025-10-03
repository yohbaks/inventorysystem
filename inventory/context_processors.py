from .models import PMScheduleAssignment, DesktopDetails
from datetime import date, timedelta

def pending_pm_notifications(request):
    today = date.today()
    near_future = today + timedelta(days=3)

    # Include overdue and near-future PMs that are not yet completed
    pending_pm = PMScheduleAssignment.objects.filter(
        is_completed=False,
        pm_section_schedule__start_date__lte=near_future
    ).select_related('equipment_package', 'pm_section_schedule__quarter_schedule', 'pm_section_schedule__section')

    for assignment in pending_pm:
        # Guard against missing equipment_package (e.g., laptops)
        if assignment.equipment_package:
            desktop_detail = DesktopDetails.objects.filter(equipment_package=assignment.equipment_package).first()
            assignment.computer_name = (
                desktop_detail.computer_name if desktop_detail else f"Desktop #{assignment.equipment_package.id}"
            )
        else:
            assignment.computer_name = "N/A"

        # Tag overdue (you can access this in the template)
        assignment.is_overdue = assignment.pm_section_schedule.start_date < today

    return {
        'pending_pm_count': pending_pm.count(),
        'pending_pm_list': pending_pm[:5],  # Limit to top 5
    }
