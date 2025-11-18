# PM Daily Checklist System - How It Works

## 📋 Overview

The PM Daily Checklist System is a **DAILY** preventive maintenance system where:
- You complete a checklist **EVERY DAY** (Monday-Friday)
- Each day gets its own completion record
- At week's end, you can generate a **WEEKLY REPORT** showing all 5 days

---

## 🔗 Available Links & URLs

### 1. **Daily PM Dashboard**
- **URL**: `http://127.0.0.1:8000/pm/daily/`
- **Navigation**: Preventive Maintenance → Daily Datacenter PM → 📅 Today's Checklist
- **Purpose**: Shows today's PM tasks and week progress

### 2. **Weekly Report View**
- **URL**: `http://127.0.0.1:8000/pm/weekly/view/`
- **Navigation**: Preventive Maintenance → Daily Datacenter PM → 📊 Weekly Report
- **Purpose**: View all 5 days aggregated (Mon-Fri)

### 3. **Complete Today's Checklist**
- **URL**: `http://127.0.0.1:8000/pm/daily/complete/<schedule_id>/`
- **Accessed From**: Daily PM Dashboard → "Complete Checklist" button
- **Purpose**: Fill out today's PM checklist

### 4. **Export Daily PDF**
- **URL**: `http://127.0.0.1:8000/pm/daily/export/<completion_id>/`
- **Purpose**: Download PDF for a single day

### 5. **Export Weekly PDF**
- **URL**: `http://127.0.0.1:8000/pm/weekly/export/`
- **Purpose**: Download PDF showing entire week (Mon-Fri combined)

---

## 🚀 How The System Works

### **SETUP (One-time)**

#### Step 1: Populate Checklist Template
```bash
python manage.py populate_pm_templates
```

This creates the **Annex A template** with 12 checklist items:
- Items 1-6, 12: **Daily tasks** (check every day)
- Items 7-11: **Weekly tasks** (check once per week, dark gray)

---

## 📅 Daily Workflow (Monday - Friday)

### **Monday Morning (Example: November 18, 2025)**

#### 1. Access Dashboard
- Navigate to: `http://127.0.0.1:8000/pm/daily/`
- OR click: **Preventive Maintenance → Daily Datacenter PM → Today's Checklist**

**What Happens Automatically:**
- ✅ System detects it's Monday
- ✅ System auto-creates schedules for entire week (Mon-Fri)
- ✅ Shows: "Today's Checklist - Monday, November 18"

#### 2. Complete Today's Checklist
- Click **"Complete Today's Checklist"** button
- Goes to: `http://127.0.0.1:8000/pm/daily/complete/<schedule_id>/`

**On the Form:**
```
PREVENTIVE MAINTENANCE CHECKLIST
Monday, November 18, 2025

Item 1: Check if WAN connectivity is up
        [✓] Done  [ ] Problems: ___________

Item 2: Check if telephone system & servers are up
        [✓] Done  [ ] Problems: ___________

Item 3: Check servers' utilization below 80%
        Times: 9 AM, 2 PM
        [✓] Done  [ ] Problems: ___________

... (all 12 items)

Printed Name: ___________
[Submit]
```

**What You Do:**
- Check the box ✓ for items you completed
- Add any problems/actions in text fields
- Enter your name
- Click Submit

**What Happens Automatically:**
- ✅ System knows it's Monday
- ✅ For all checked items → Sets `monday=True`
- ✅ For unchecked items → Sets `monday=False`
- ✅ All other days (T, W, Th, F) → Set to `False`

#### 3. View Completion
- After submit, you're redirected to dashboard
- Message: "Daily PM checklist for Monday, November 18 completed successfully!"

#### 4. Export Monday's PDF
- Click **"Export Daily PDF"** button
- Downloads: `PM_Daily_Monday_20251118.pdf`

**PDF Shows:**
```
ANNEX "A"
Preventive Maintenance Checklist/Activities for the Datacenter (Daily/Weekly)

Schedule: Mondays - Fridays
Date accomplished: November 18, 2025 (Monday)

┌────┬─────────────────┬───────────────────────┬──────────┐
│Item│     Task        │ Status (put ✓ if done)│ Problems │
│No. │                 │ M │ T │ W │Th│ F      │          │
├────┼─────────────────┼───┼───┼───┼──┼───────┼──────────┤
│ 1  │ Check WAN...    │ ✓ │   │   │  │        │          │
│ 2  │ Check phone...  │ ✓ │   │   │  │        │          │
│ 3  │ Check servers.. │ ✓ │   │   │  │        │          │
...
```

**Notice:** Only the **M (Monday)** column has checkmarks! T, W, Th, F are empty.

---

### **Tuesday Morning (November 19, 2025)**

#### 1. Access Dashboard Again
- Go to: `http://127.0.0.1:8000/pm/daily/`
- Shows: "Today's Checklist - Tuesday, November 19"

**What You See:**
- Monday ✓ (completed)
- Tuesday ← (today - pending)
- Wednesday (pending)
- Thursday (pending)
- Friday (pending)

#### 2. Complete Tuesday's Checklist
- Click **"Complete Today's Checklist"**
- Fill out the form (same 12 items)
- Submit

**What Happens Automatically:**
- ✅ System knows it's Tuesday
- ✅ For all checked items → Sets `tuesday=True`
- ✅ Monday's data remains unchanged

#### 3. Export Tuesday's PDF
- Downloads: `PM_Daily_Tuesday_20251119.pdf`

**PDF Shows:**
```
┌────┬─────────────────┬───────────────────────┬──────────┐
│Item│     Task        │ M │ T │ W │Th│ F      │ Problems │
├────┼─────────────────┼───┼───┼───┼──┼───────┼──────────┤
│ 1  │ Check WAN...    │   │ ✓ │   │  │        │          │
│ 2  │ Check phone...  │   │ ✓ │   │  │        │          │
```

**Notice:** Now only the **T (Tuesday)** column has checkmarks!

---

### **Continue for Wednesday, Thursday, Friday**

Same process each day:
1. Access dashboard
2. Complete today's checklist
3. System auto-marks today's column
4. Export daily PDF (optional)

---

### **Friday Evening - Generate Weekly Report**

#### 1. View Weekly Report
- Navigate to: `http://127.0.0.1:8000/pm/weekly/view/`
- OR click: **Preventive Maintenance → Daily Datacenter PM → Weekly Report**

**What You See:**
```
WEEKLY PM REPORT
Week of: November 18 - November 22, 2025

Item 1: Check WAN connectivity
        Mon [✓]  Tue [✓]  Wed [✓]  Thu [✓]  Fri [✓]

Item 2: Check telephone & servers
        Mon [✓]  Tue [✓]  Wed [✓]  Thu [✓]  Fri [✓]

Item 7: Check anti-virus (WEEKLY TASK)
        Mon [ ]  Tue [ ]  Wed [✓]  Thu [ ]  Fri [ ]
        (Completed once on Wednesday)
```

#### 2. Export Weekly PDF
- Click **"Export Weekly PDF"**
- Downloads: `PM_Weekly_20251118_20251122.pdf`

**PDF Shows:**
```
ANNEX "A"
Preventive Maintenance Checklist/Activities for the Datacenter (Daily/Weekly)

Schedule: Mondays - Fridays
Week of: November 18 - November 22, 2025

┌────┬─────────────────┬───────────────────────┬──────────┐
│Item│     Task        │ M │ T │ W │Th│ F      │ Problems │
├────┼─────────────────┼───┼───┼───┼──┼───────┼──────────┤
│ 1  │ Check WAN...    │ ✓ │ ✓ │ ✓ │✓ │ ✓      │          │
│ 2  │ Check phone...  │ ✓ │ ✓ │ ✓ │✓ │ ✓      │          │
│ 3  │ Check servers.. │ ✓ │ ✓ │ ✓ │✓ │ ✓      │          │
...
│ 7  │ Anti-virus...   │   │   │ ✓ │  │        │ (dark)   │
│ 8  │ Event logs...   │   │   │ ✓ │  │        │ (dark)   │
```

**Notice:**
- Daily tasks (1-6, 12) have ✓ in ALL 5 columns
- Weekly tasks (7-11) have ✓ only where completed

---

## 🎯 Key Points

### Automatic Features:
1. **Schedules** - Auto-created when you visit dashboard
2. **Day Detection** - System knows what day it is
3. **Column Selection** - Automatically marks today's column
4. **Weekends** - Automatically skipped (no PM on Sat/Sun)

### Manual Features:
1. **Completing Checklist** - You check off items
2. **Adding Problems** - You type any issues
3. **Exporting PDFs** - You click export buttons

---

## 📊 Daily Tasks vs Weekly Tasks

### Daily Tasks (Items 1-6, 12):
- **Should be done EVERY day** (Mon-Fri)
- By Friday, should have 5 checkmarks across the week
- Examples:
  - Check WAN connectivity
  - Check servers
  - Check temperature/humidity

### Weekly Tasks (Items 7-11):
- **Done ONCE per week**
- Dark gray shading in PDF
- Can be done any day (Mon-Fri)
- Examples:
  - Check anti-virus updates
  - Check event logs
  - Check for water leaks
  - Check for pest infestation

---

## 🔄 Weekly Cycle

```
Week 1:
Mon → Complete checklist → Export Mon PDF (M column filled)
Tue → Complete checklist → Export Tue PDF (T column filled)
Wed → Complete checklist → Export Wed PDF (W column filled)
Thu → Complete checklist → Export Thu PDF (Th column filled)
Fri → Complete checklist → Export Fri PDF (F column filled)
     → Export Weekly PDF (ALL columns filled)

Week 2:
(Repeat same process)
Mon → New week starts...
```

---

## ❓ Common Questions

### Q: Do I need to create schedules?
**A:** NO! Schedules are created automatically when you access the dashboard.

### Q: Do I select which day (M/T/W/Th/F)?
**A:** NO! The system automatically knows what day it is and marks the correct column.

### Q: Can I complete multiple days at once?
**A:** NO! You can only complete TODAY's checklist. This ensures data integrity.

### Q: What if I miss a day?
**A:** You can go back and complete previous days if needed. The system allows completing any pending schedule.

### Q: When should I export weekly PDF?
**A:** Friday evening after completing all 5 days. Or anytime you want to see the week's progress.

---

## 🛠️ Templates You Need

To make the system fully functional, you need these templates:

### 1. **templates/pm/daily_dashboard.html**
Shows:
- Today's date and day name
- Week progress (which days completed)
- Button to complete today's checklist
- Link to weekly report

### 2. **templates/pm/complete_daily_pm.html**
Shows:
- Today's date
- List of all 12 checklist items
- Checkbox for each item
- Problems/Actions text fields
- Submit button

### 3. **templates/pm/weekly_report_view.html**
Shows:
- Week date range
- All items with M/T/W/Th/F status
- Aggregated problems
- Export weekly PDF button

---

## 📝 Summary

**The system is FULLY AUTOMATIC:**
1. Visit dashboard → Schedules created
2. Complete checklist → Today's day auto-marked
3. Export PDF → Shows today or full week
4. Next day → Repeat!

**You only do:**
- ✓ Check off completed items
- ✓ Add problems/actions
- ✓ Submit
- ✓ Export PDFs when needed

**That's it!** The system handles all the complexity automatically.
