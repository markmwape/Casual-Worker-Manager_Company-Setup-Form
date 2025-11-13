# Custom Report Field (Per Hour) - Debugging Guide

## Issue
Getting "Failed to manage report field" error when trying to add a custom field to Per Hour reports.

## What I've Fixed

### 1. Enhanced Backend Error Logging (`routes.py`)
The `/api/report-field` endpoint now provides:
- ✅ Detailed logging of incoming request data
- ✅ Full error traceback in server logs
- ✅ Actual error message returned to frontend (not just generic message)

### 2. Enhanced Frontend Logging (`templates/modals/add_report_field.html`)
The `addCustomFieldPerHour()` function now includes:
- ✅ Console logging of request data before sending
- ✅ Console logging of response status and data
- ✅ Better validation checks
- ✅ More detailed error messages

## How to Debug

### Step 1: Open Browser Developer Tools
1. Press **F12** or **Cmd+Option+I** (Mac)
2. Go to the **Console** tab
3. Keep it open while adding the field

### Step 2: Try Adding the Field Again
With the setup from your screenshot:
- Field Name: `bxnjuhgavbnjh` (or any valid name with letters/underscores)
- Formula: `hours_worked * per_hour_rate`
- Maximum Limit: ✅ Enabled, value: `90000`

### Step 3: Check Console Output
You should now see detailed logs:
```javascript
Sending request to: /api/report-field
Request data: {
  name: "bxnjuhgavbnjh",
  formula: "hours_worked * per_hour_rate",
  field_type: "numeric",
  max_limit: 90000,
  payout_type: "per_hour"
}
Response status: 500 (or other status)
Response data: { error: "actual error message here" }
```

### Step 4: Check Server Logs
In your terminal where the server is running, you'll see:
```
INFO: Creating new report field: name=bxnjuhgavbnjh, formula=hours_worked * per_hour_rate, payout_type=per_hour
ERROR: Error managing report field: [actual error]
ERROR: Request data: {...}
ERROR: Traceback: [full stack trace]
```

## Common Issues & Solutions

### Issue 1: No Company Found
**Error**: "Company not found"
**Solution**: Ensure your workspace has a company created
- Go to Dashboard
- Check if company exists
- If not, create a company first

### Issue 2: Duplicate Field Name
**Error**: "A custom field with this name already exists"
**Solution**: Try a different field name or delete the existing field

### Issue 3: Invalid Formula
**Error**: Related to formula parsing
**Solution**: 
- Use valid field names: `hours_worked`, `per_hour_rate`, `age`
- Use valid operators: `+`, `-`, `*`, `/`, `(`, `)`
- Example: `hours_worked * per_hour_rate`

### Issue 4: Max Limit NaN
**Error**: Related to max_limit being NaN
**Solution**:
- Ensure the checkbox is checked
- Ensure a valid number is entered in the field
- The code now uses `parseFloat()` to convert properly

### Issue 5: Session/Authentication Issue
**Error**: "Not authenticated" or "No active workspace"
**Solution**: 
- Refresh the page
- Sign in again
- Ensure you have an active workspace selected

## Testing Checklist

Before clicking "Add Custom Field":
- [ ] Field name contains only letters and underscores
- [ ] Field name is not empty
- [ ] Formula is not empty  
- [ ] Formula uses valid field names and operators
- [ ] If Maximum Limit is enabled, a valid number is entered
- [ ] You're signed in with an active workspace
- [ ] Your workspace has a company created

## What to Share for Further Help

If the issue persists, please share:
1. **Browser Console logs** - Copy the full console output
2. **Server logs** - Copy the relevant error messages from terminal
3. **Network tab** - 
   - Go to Network tab in DevTools
   - Find the `/api/report-field` request
   - Share the Request payload and Response

## Expected Successful Flow

1. Fill in form → Click "Add Custom Field"
2. Console logs the request data
3. Server receives and logs the request
4. Server creates the field in database
5. Server returns 201 status with field data
6. Frontend shows "Success" modal
7. Page reloads
8. New field appears in the custom fields table

## Files Modified

1. **routes.py** - Line ~4377-4415
   - Added detailed logging
   - Better error messages

2. **templates/modals/add_report_field.html** - Line ~590-650
   - Added console logging
   - Better validation
   - Improved error handling
