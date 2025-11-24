# Downtime Logging Guide

## Quick Reference: How to Log Equipment Downtime

### Step 1: Access Daily PM Completion
1. Navigate to your Daily PM completion form
2. Look for checklist items related to critical equipment (usually items 1 & 2)

### Step 2: Use the "Log Downtime" Button
- **Do NOT** just type downtime info in the "Problems Encountered" field
- **DO** click the red **"Log Downtime"** button
- This button appears for critical equipment monitoring items

### Step 3: Fill in the Downtime Form

#### Required Fields:
- **Date of Downtime**: When did it occur?
- **Start Time**: When did the downtime start?
- **Equipment/System Name**: Use specific keywords for auto-categorization:
  - For WAN issues: "network", "router", "switch", "internet", "connectivity"
  - For phone systems: "pabx", "phone", "telephone", "voip"
  - For servers: "server", "mail server", "database", "admin server"
  - For trunkline: "trunkline", "trunk line", "connection"

- **Severity Level**:
  - **Minor**: No service impact
  - **Moderate**: Partial impact (default)
  - **Major**: Significant impact
  - **Critical**: Complete service loss

- **Cause/Description**: What caused the downtime?

#### Optional Fields:
- **End Time**: When service was restored (leave blank if ongoing)
- **Resolution/Action Taken**: How was it resolved?
- **Services Affected**: Which services were impacted?
- **Users Affected**: Approximate number of users

### Step 4: Submit
- Click **"Log Downtime Event"**
- The system will:
  - Create a downtime event record
  - Auto-populate the "Problems" field with a summary
  - Make the data available for SNMR smart suggestions
  - Include it in downtime analytics

## SNMR Smart Suggestions

Once downtime is properly logged:

1. Create or edit an SNMR report for the month
2. Smart suggestions will automatically:
   - Find all downtime events for that month
   - Categorize by equipment type (WAN, PABX, Server, Trunkline)
   - Suggest status, reasons, dates, and resolutions
   - Show equipment affected and event counts

### Equipment Name → SNMR Category Mapping:

| Keywords in Equipment Name | SNMR Category |
|---------------------------|---------------|
| wan, network, router, switch, internet | Wide Area Network |
| pabx, pbx, phone, telephone, voip | PABX |
| server, admin, mail, database | Admin Server |
| trunkline, trunk, line, connection | Trunkline |

## Viewing Downtime Analytics

Access: `/inventory/pm/downtime/analytics/`

See:
- Total downtime events
- Total downtime hours
- Events by severity
- Events by equipment
- Daily breakdown charts
- Recent critical events

## Migration Note

If you have existing downtime info in "Problems" fields, run:
```bash
python migrate_downtime_data.py --live
```

This will parse and create proper downtime records from your problem descriptions.

---

**Remember**: Use the dedicated "Log Downtime" button, not just the problems field!
