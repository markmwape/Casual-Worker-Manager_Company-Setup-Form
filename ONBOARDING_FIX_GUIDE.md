# Onboarding Tour Fix - Reports Page

## What Was Fixed

The onboarding tour system has been fixed and improved to work properly on the reports page. Here are the changes made:

### 1. **Improved Element Detection**
   - Updated the reports flow to use the correct `data-onboarding` attributes
   - Fixed selectors to match the actual elements on the reports page
   - Added better fallback selectors

### 2. **Modal Handling**
   - Fixed modal detection to exclude the date-picker and format-selection modals
   - These modals are part of the page functionality and shouldn't block the tour
   - Tour will now start even if these specific modals are present

### 3. **Better Flow Definition**
   - Updated the reports flow with 4 clear steps:
     1. Overview of the reports page
     2. Date range selection
     3. Report types (Per Day, Per Hour, Per Unit)
     4. Export and download options
   - Added proper positioning and padding for each step
   - Improved descriptions to be more helpful

### 4. **Enhanced Debugging**
   - Added console logging to help troubleshoot issues
   - Added element existence checks
   - Better error messages when elements aren't found

### 5. **Help Button**
   - The floating help button (question mark) in the bottom-right corner now works reliably
   - Added better click event handling
   - Added console logs for debugging

## How to Use the Onboarding Tour

### Method 1: Help Button (Recommended)
1. Look for the blue floating button with a question mark (?) in the bottom-right corner of the page
2. Click the button to start the tour
3. The tour will guide you through all features of the reports page

### Method 2: Browser Console
If you need to troubleshoot or force-start the tour:

1. Open browser console (F12 or right-click → Inspect → Console)
2. Run any of these commands:

```javascript
// Test if onboarding system is working
testOnboardingSystem()

// Force start the tour
forceStartTour()

// Clear onboarding state (if you want to see the welcome message again)
clearOnboardingState()
```

### Method 3: URL Parameter
Add `?show_onboarding=true` to the URL:
```
https://your-site.com/reports?show_onboarding=true
```

## Tour Steps

The reports page tour includes these steps:

1. **Generate Reports** - Overview of the reports dashboard
2. **Select Date Range** - How to pick reporting periods
3. **Report Types** - Understanding Per Day, Per Hour, and Per Unit reports
4. **Export & Download** - How to download reports as CSV or Excel

## Troubleshooting

### If the tour doesn't start:

1. **Check the console** - Open browser console and look for errors
2. **Run test command** - Type `testOnboardingSystem()` in console to see diagnostics
3. **Check for modals** - Make sure no other modals/dialogs are open (except date picker)
4. **Clear state** - Run `clearOnboardingState()` and then `forceStartTour()`

### If elements aren't highlighted:

1. Make sure you're on the reports page (`/reports`)
2. Check that the page has fully loaded
3. Scroll to the top of the page before starting the tour
4. Run `testOnboardingSystem()` to see which elements are missing

### If help button is not visible:

1. Check bottom-right corner of the screen
2. Make sure you're not on the sign-in page (button only shows on main pages)
3. Check browser console for any JavaScript errors
4. Try refreshing the page

## Testing File

A test utilities file has been created at:
`static/js/onboarding-test.js`

To use it, add this line to your page (for testing only):
```html
<script src="{{ url_for('static', filename='js/onboarding-test.js') }}"></script>
```

Then you can use the test functions in the browser console.

## Notes

- The tour automatically skips itself if you've completed it before
- To reset: use `clearOnboardingState()` in console
- The tour prevents page scrolling while active
- Press ESC to exit the tour at any time
- The help button is always available for replaying the tour

## Support

If you still experience issues:

1. Open browser console (F12)
2. Run `testOnboardingSystem()`
3. Copy the console output
4. Share the output with your development team

The console will show:
- Whether the system is loaded
- Current page detection
- Available flows
- Which elements are found/missing
