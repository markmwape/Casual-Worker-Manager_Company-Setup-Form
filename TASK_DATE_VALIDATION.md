# Task Date Validation and Status Management

## Overview

This feature implements business logic for task start dates and automatic status management based on the selected date.

## Business Rules

1. **Date Validation**: Task start dates should be less than or equal to the current date
2. **Status Assignment**: 
   - If a future date is selected, the task status is automatically set to 'Pending'
   - If current or past date is selected, the task status is set to 'Active'
3. **Status Restrictions**: Tasks with future start dates can only have 'Pending' status until their start date is reached
4. **Automatic Status Updates**: Pending tasks automatically change to 'Active' when their start date is reached

## Implementation Details

### Backend Changes

#### Task Creation (`routes.py`)
- Added date validation logic in `create_task()` function
- Compares selected start date with current date
- Sets appropriate status based on date comparison
- Logs status assignment for debugging

#### Status Update Validation (`routes.py`)
- Added validation in `update_task_status()` function
- Prevents setting 'In Progress' or 'Completed' status for tasks with future start dates
- Returns clear error messages for invalid status changes
- Only allows 'Pending' status for future tasks

#### Status Update Function (`routes.py`)
- Added `update_pending_tasks_status()` function
- Automatically checks for pending tasks where start date has been reached
- Updates status from 'Pending' to 'Active'
- Called when viewing tasks or task attendance pages

### Frontend Changes

#### Date Picker Enhancement (`static/js/date-picker.js`)
- Added maximum date restriction for task start dates (today only)
- Added warning message for future date selection
- Enhanced validation with visual feedback

#### Status Indicator (`templates/modals/add_task.html`)
- Added real-time status indicator in task creation modal
- Shows what status will be assigned based on selected date
- Color-coded feedback (green for Active, orange for Pending)

#### Status Dropdown Enhancement (`templates/tasks.html`)
- Added client-side validation for status changes
- Disables 'In Progress' and 'Completed' options for future tasks
- Visual indicators show which options are available
- Clear error messages for invalid status attempts

#### CSS Styling (`static/css/date-picker.css`)
- Added warning message styling
- Orange/yellow color scheme for future date warnings
- Responsive design for mobile devices

## User Experience

### Task Creation Flow
1. User opens "Create New Task" modal
2. Date picker shows today's date as default
3. User can only select today or past dates
4. Real-time status indicator shows what status will be assigned
5. Warning message appears if future date is somehow selected
6. Task is created with appropriate status

### Status Management
1. Pending tasks are automatically checked when viewing tasks
2. Tasks with reached start dates are updated to 'Active'
3. Users see updated status immediately
4. No manual intervention required
5. Future tasks are restricted to 'Pending' status only
6. Clear visual feedback shows which status options are available

## Technical Notes

- Date comparison is done at midnight (00:00:00) to avoid time-of-day issues
- Status updates happen on page load for efficiency
- All date operations use UTC to avoid timezone issues
- Comprehensive error handling and logging included
- Backward compatible with existing tasks

## Testing

To test the functionality:
1. Create a task with today's date → Should be 'Active'
2. Create a task with a past date → Should be 'Active'
3. Try to create a task with future date → Should show warning and set to 'Pending'
4. Wait for a pending task's date to arrive → Should automatically become 'Active'
5. Try to set a future task to 'In Progress' → Should be blocked with error message
6. Try to set a future task to 'Completed' → Should be blocked with error message
7. Future tasks should only allow 'Pending' status in the dropdown 