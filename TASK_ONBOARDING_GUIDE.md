# Task Tracking Pages - Onboarding Tours

## Overview

The three task tracking pages now have **individual, specialized onboarding tours** that guide users through their specific functionality:

1. **Task Attendance** (`/task_attendance/<task_id>`) - Mark workers present/absent
2. **Hours Worked** (`/task_hours_worked/<task_id>`) - Record hours for hourly-rate tasks
3. **Units Completed** (`/task_units_completed/<task_id>`) - Track units for piece-rate tasks

---

## 🎯 Task Attendance Tour

**Page:** `/task_attendance/<task_id>`  
**Purpose:** Mark workers as Present or Absent (or enter units for piece-rate tasks)

### Tour Steps:
1. **Mark Daily Attendance** - Overview of the attendance tracking page
2. **Select Date** - How to pick the date for attendance
3. **Worker List** - View all assigned workers
4. **Mark Present or Absent** - How to mark attendance status
5. **Save Attendance** - Save data to reports and payroll

### Key Features Highlighted:
- ✅ Present/Absent buttons with visual feedback
- 📅 Date navigation (previous/next day arrows)
- 💾 Auto-save to reports
- 🔍 Worker search functionality

---

## ⏰ Hours Worked Tour

**Page:** `/task_hours_worked/<task_id>`  
**Purpose:** Record the exact hours each worker spent on hourly-rate tasks

### Tour Steps:
1. **Record Hours Worked** - Overview of hours tracking
2. **Select Date** - Navigate to the correct date
3. **Worker Hours List** - See all workers in the task
4. **Enter Hours** - How to input decimal hours (e.g., 8.5)
5. **Save Hours** - Calculate and save hourly payments

### Key Features Highlighted:
- ⏱️ Decimal hour input (8, 8.5, 4.5)
- 💰 Automatic payment calculation (hours × rate)
- 📊 Integration with reports
- 🔢 Support for partial hours

---

## 📦 Units Completed Tour

**Page:** `/task_units_completed/<task_id>`  
**Purpose:** Track units/pieces/items completed for piece-rate payment

### Tour Steps:
1. **Track Units Completed** - Overview of unit tracking
2. **Select Date** - Choose the production date
3. **Worker Production List** - View all workers
4. **Enter Units** - Input whole number of completed units
5. **Save Units** - Calculate piece-rate payments

### Key Features Highlighted:
- 📦 Whole number unit input
- 💵 Automatic calculation (units × per-unit rate)
- 📈 Production tracking
- 🎯 Perfect for piece-rate jobs

---

## How to Start the Tours

### Method 1: Help Button (Recommended)
- Look for the **blue floating button** with a **?** in the bottom-right corner
- Click it to start the page-specific tour
- Works on all three pages automatically

### Method 2: Browser Console
```javascript
// Test if tour is working for current page
testOnboardingSystem()

// Force start the tour
forceStartTour()

// Clear tour state (to see welcome message again)
clearOnboardingState()
```

### Method 3: URL Parameter
Add `?show_onboarding=true` to any of these URLs:
```
/task_attendance/<task_id>?show_onboarding=true
/task_hours_worked/<task_id>?show_onboarding=true
/task_units_completed/<task_id>?show_onboarding=true
```

---

## Technical Implementation

### Page Detection
The onboarding system now properly detects these three pages:

```javascript
getCurrentPage() {
    const path = window.location.pathname;
    if (path.includes('/task_attendance')) return 'task_attendance';
    if (path.includes('/task_hours_worked')) return 'task_hours_worked';
    if (path.includes('/task_units_completed')) return 'task_units_completed';
    // ... other pages
}
```

### Data-Onboarding Attributes Added

#### Task Attendance (`task_attendance.html`):
- `data-onboarding="attendance-container"` - Main container
- `data-onboarding="attendance-table"` - Worker table
- `data-onboarding="attendance-checkbox"` - Present/Absent buttons
- `data-onboarding="save-attendance"` - Save button

#### Hours Worked (`task_hours_worked.html`):
- `data-onboarding="hours-worked-container"` - Main container
- `data-onboarding="page-header"` - Page header
- `data-onboarding="hours-table"` - Worker hours table
- `data-onboarding="hours-input"` - Hour input fields
- `data-onboarding="save-hours-btn"` - Save button

#### Units Completed (`task_units_completed.html`):
- `data-onboarding="units-completed-container"` - Main container
- `data-onboarding="page-header"` - Page header
- `data-onboarding="units-table"` - Worker units table
- `data-onboarding="units-input"` - Unit input fields
- `data-onboarding="save-units-btn"` - Save button

---

## Troubleshooting

### Tour doesn't start on task pages:

1. **Check you're on the correct page:**
   - Task Attendance: URL should include `/task_attendance/`
   - Hours Worked: URL should include `/task_hours_worked/`
   - Units Completed: URL should include `/task_units_completed/`

2. **Run diagnostic:**
   ```javascript
   testOnboardingSystem()
   ```
   This will show:
   - Current page detection
   - Available flows
   - Which elements are found/missing

3. **Force start:**
   ```javascript
   forceStartTour()
   ```

### Elements not highlighted:

1. Make sure the page has fully loaded
2. Check that workers are assigned to the task
3. Scroll to top of page before starting tour
4. Look for the help button (?) in bottom-right corner

### Help button not visible:

1. Refresh the page
2. Check browser console for JavaScript errors
3. Ensure you're not on the signin page
4. Try clearing browser cache

---

## User Benefits

### For New Users:
- 🎓 **Learn quickly** - Step-by-step guidance for each page type
- 🧭 **No confusion** - Clear instructions specific to the task at hand
- ✅ **Build confidence** - See exactly what to do and why

### For Existing Users:
- 🔄 **Replay anytime** - Click the help button to refresh your memory
- 📚 **Reference guide** - Quick reminder of features
- 🚀 **Discover features** - Learn about features you might have missed

---

## Files Modified

1. ✅ `static/js/onboarding.js` - Added three new flows
2. ✅ `templates/task_attendance.html` - Added data-onboarding attributes
3. ✅ `templates/task_hours_worked.html` - Added data-onboarding attributes
4. ✅ `templates/task_units_completed.html` - Added data-onboarding attributes
5. ✅ `TASK_ONBOARDING_GUIDE.md` - This documentation

---

## Quick Reference

| Page | URL Pattern | Main Purpose | Payment Type |
|------|-------------|--------------|--------------|
| Task Attendance | `/task_attendance/<id>` | Mark Present/Absent | Daily wage |
| Hours Worked | `/task_hours_worked/<id>` | Record hours worked | Hourly rate |
| Units Completed | `/task_units_completed/<id>` | Track units done | Piece rate |

---

## Console Commands

```javascript
// Check current page detection
window.onboardingSystem.currentPage

// See all available flows
Object.keys(window.onboardingSystem.flows)

// Test the system
testOnboardingSystem()

// Force start tour
forceStartTour()

// Reset everything
clearOnboardingState()
```

---

## Support

If tours still don't work:

1. Open browser console (F12)
2. Run: `testOnboardingSystem()`
3. Copy console output
4. Share with your development team

The diagnostic will show exactly which elements are missing or which flow isn't loading.

---

**✨ All three task tracking pages now have individual, context-aware onboarding tours!**
