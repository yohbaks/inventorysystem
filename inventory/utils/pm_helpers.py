# inventory/utils/pm_helpers.py
from inventory.models import PMScheduleAssignment, PMSectionSchedule

def transfer_pm_schedule_on_user_change(equipment_package, new_enduser):
    """
    When End User changes:
    - Keeps all completed PMs intact.
    - Reassigns pending PMs to the new section (same quarter/year).
    """
    try:
        if not new_enduser or not new_enduser.employee_office_section:
            return "End user has no assigned office section."

        new_section = new_enduser.employee_office_section

        # 1️⃣ Find incomplete PMs for this desktop/laptop
        assignments = PMScheduleAssignment.objects.filter(
            equipment_package=equipment_package,
            is_completed=False
        ).select_related('pm_section_schedule__quarter_schedule')

        relinked = 0
        for a in assignments:
            quarter = a.pm_section_schedule.quarter_schedule
            new_sched = PMSectionSchedule.objects.filter(
                quarter_schedule=quarter,
                section=new_section
            ).first()
            if new_sched:
                a.pm_section_schedule = new_sched
                a.save(update_fields=['pm_section_schedule'])
                relinked += 1

        return f"{relinked} pending PM schedules moved to {new_section.name}."

    except Exception as e:
        return f"Transfer failed: {e}"
