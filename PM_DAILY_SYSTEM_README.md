# PM Daily Checklist System - Complete Guide

## Overview

The PM (Preventive Maintenance) Daily Checklist System is designed for **daily completion** of datacenter maintenance tasks, Monday through Friday, with **weekly aggregation** for reporting.

## How It Works

### Daily Workflow

1. **Each Day (Mon-Fri)**:
   - Technician logs in and sees today's PM checklist
   - Completes the checklist items for TODAY only
   - Marks which tasks were done
   - Notes any problems or actions taken
   - Submits the daily completion

2. **Daily PDF Export**:
   - Generates the Annex A form
   - Shows ONLY today's column filled (e.g., Monday column has checkmarks)
   - Other day columns (Tue, Wed, Thu, Fri) are BLANK
   - This is the daily record

3. **Weekly PDF Export**:
   - Combines ALL 5 daily completions
   - Shows the FULL week on ONE form
   - M column shows Monday's checks
   - T column shows Tuesday's checks
   - W column shows Wednesday's checks
   - Th column shows Thursday's checks
   - F column shows Friday's checks
   - Problems from each day are aggregated

## Checklist Items (Annex A)

### Daily Tasks (Items 1-6, 12):
- Completed EVERY day Monday-Friday
- Should have checkmarks in all 5 columns by week's end

**Items:**
1. Check if WAN connectivity is up
2. Check if the telephone system is up and running / Check if all servers are up and running
3. Check if servers' utilization is below 80% (Times: 9 AM, 2 PM)
5. Check temperature level 20°C-27°C (Times: 8 AM, 10 AM, 12 PM, 2 PM, 4 PM)
6. Check humidity level 30%-60% (Times: 8 AM, 10 AM, 12 PM, 2 PM, 4 PM)
12. Remove any fire hazards

### Weekly Tasks (Items 7-11):
- Completed ONCE during the week (dark gray shading)
- Typically done on a specific day

**Items:**
7. Check if servers' anti-virus definition files are up-to-date
8. Check if server's event logs for critical warnings or errors
9. Check for signs of water leaks
10. Check for signs of holes on the ceiling and walls
11. Check for signs of pest infestation

## Setup Instructions

### 1. Populate Templates

Run this command to create/update the checklist template:

```bash
python manage.py populate_pm_templates
```

This creates the Annex A template with all 12 items.

### 2. Daily Completion

**Schedules are created automatically!** When you access the dashboard on any weekday, the system automatically creates schedules for the entire week (Mon-Fri).

No manual schedule creation needed!

**Each day:**
1. Navigate to PM Daily Dashboard
2. Click "Complete Today's Checklist"
3. Check off completed items
4. Add problems/actions if needed
5. Sign and submit

### 3. Export Reports

**Daily Report:**
- View a completed day
- Click "Export Daily PDF"
- Gets PDF showing only that day's column filled

**Weekly Report:**
- Click "Export Weekly Report"
- Select the week (defaults to current week)
- Gets PDF showing all 5 days combined

## URL Structure

Add these to your `urls.py`:

```python
from inventory.pm_daily_views import (
    daily_pm_dashboard,
    complete_daily_pm,
    export_daily_pm_pdf,
    export_weekly_pm_pdf,
    view_daily_pm_completion,
    weekly_pm_report_view,
)

urlpatterns = [
    # Daily PM paths
    path('pm/daily/', daily_pm_dashboard, name='pm_daily_dashboard'),
    path('pm/daily/complete/<int:schedule_id>/', complete_daily_pm, name='complete_daily_pm'),
    path('pm/daily/export/<int:completion_id>/', export_daily_pm_pdf, name='export_daily_pm_pdf'),
    path('pm/daily/view/<int:completion_id>/', view_daily_pm_completion, name='view_daily_pm_completion'),

    # Weekly PM paths
    path('pm/weekly/export/', export_weekly_pm_pdf, name='export_weekly_pm_pdf'),
    path('pm/weekly/view/', weekly_pm_report_view, name='weekly_pm_report_view'),
]
```

## Data Model Usage

### PMChecklistSchedule
- **One record per day** (Mon-Fri only)
- `scheduled_date`: The specific day (e.g., 2025-11-18 Monday)
- `template`: Links to Annex A template
- `status`: PENDING → COMPLETED

### PMChecklistCompletion
- **One record per day**
- `schedule`: Links to that day's schedule (OneToOne)
- `completion_date`: Same as schedule.scheduled_date
- `completed_by`: Technician who completed it

### PMChecklistItemCompletion
- **One record per item per day**
- For a Monday completion: `monday=True`, all others False
- For a Tuesday completion: `tuesday=True`, all others False
- etc.

This allows the weekly report to aggregate by looking at which day field is True in each completion.

## PDF Format

The PDF matches the exact template format (`templates/pm/daily_weekly.webp`):

- **Header**: "ANNEX A" in top right
- **Title**: "Preventive Maintenance Checklist/Activities for the Datacenter (Daily/Weekly)"
- **Schedule**: "Mondays - Fridays"
- **Table**:
  - 8 columns: Item No | Task | M | T | W | Th | F | Problems
  - Items 7-11 have dark gray background (weekly tasks)
  - Grid lines separating each day column

## Example Workflow

**Week of November 18-22, 2025:**

**Monday 11/18:**
- Complete checklist for Monday
- Export daily PDF → shows ✓ in M column only

**Tuesday 11/19:**
- Complete NEW checklist for Tuesday
- Export daily PDF → shows ✓ in T column only

**Wednesday 11/20:**
- Complete NEW checklist for Wednesday
- Export daily PDF → shows ✓ in W column only

**Thursday 11/21:**
- Complete NEW checklist for Thursday
- Export daily PDF → shows ✓ in Th column only

**Friday 11/22:**
- Complete NEW checklist for Friday
- Export daily PDF → shows ✓ in F column only

**End of Week:**
- Export weekly PDF → shows ✓ in all 5 columns (M, T, W, Th, F)
- All daily tasks should have 5 checkmarks
- Weekly tasks (7-11) may have 1-5 checkmarks depending on when done

## Files Changed/Created

1. **`pm_daily_weekly_export.py`** - NEW: Handles daily and weekly PDF generation
2. **`pm_daily_views.py`** - NEW: All views for daily workflow
3. **`populate_pm_templates.py`** - UPDATED: Sets frequency to DAILY
4. **`pm_pdf_export.py`** - OLD: Can be deprecated or kept for other annexes

## Migration Notes

If you have existing weekly completions:
- They will still work with the old system
- New completions should use the daily approach
- Consider data migration if you want to convert old data

## Key Differences from Old System

| Old System | New System |
|------------|------------|
| One completion per WEEK | One completion per DAY |
| Fill all M-F at once | Fill only TODAY's column |
| No daily PDF | Daily PDF shows one column |
| Weekly PDF = same as completion | Weekly PDF aggregates 5 completions |

## Summary

**Remember:**
- ✅ Schedules are created AUTOMATICALLY (Mon-Fri)
- ✅ Complete checklist DAILY (Mon-Fri)
- ✅ Each day creates a NEW completion record
- ✅ Daily PDF shows ONLY that day
- ✅ Weekly PDF combines ALL 5 days
- ✅ Weekends are excluded automatically
- ✅ Daily tasks: Items 1-6, 12
- ✅ Weekly tasks: Items 7-11 (dark gray)
