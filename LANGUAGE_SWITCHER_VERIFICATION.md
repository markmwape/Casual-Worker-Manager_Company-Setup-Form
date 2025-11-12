# Language Switcher Verification Guide

## Changes Made

### 1. **JavaScript Improvements** (`static/js/language-switcher.js`)
✅ Added comprehensive console logging for debugging
✅ Improved error handling with detailed error messages
✅ Added proper cleanup of inline styles when closing dropdowns
✅ Added Escape key support to close dropdowns
✅ Enhanced menu population with validation checks
✅ Added aria-label for accessibility

### 2. **CSS Improvements** (`static/css/language-switcher-fixes.css`)
✅ Fixed visibility states with proper specificity
✅ Added smooth transitions for opening/closing
✅ Added multiple selector variations to ensure visibility
✅ Fixed z-index hierarchy
✅ Improved transform animations

### 3. **Backend Improvements** (`language_routes.py`)
✅ Enhanced error handling with detailed logging
✅ Added session.modified flag to ensure session saves
✅ Improved validation of language codes
✅ Added better fallback data
✅ Prioritized session over database for immediate language changes
✅ Added traceback logging for debugging

### 4. **HTML Improvements** (`templates/components/language_switcher.html`)
✅ Added aria-haspopup and aria-expanded attributes
✅ Ensured proper initial state (aria-expanded="false")

## How to Test

### Step 1: Start the Application
```bash
cd "/Users/markbonganimwape/Desktop/Casual Worker Manager_Company Setup Form"
python3 main.py
```

### Step 2: Open Browser Developer Tools
- **Chrome/Edge**: Press `F12` or `Cmd+Option+I` (Mac)
- **Firefox**: Press `F12` or `Cmd+Option+K` (Mac)
- **Safari**: Enable Developer Menu in Preferences, then `Cmd+Option+I`

### Step 3: Navigate to Console Tab
You should see initialization logs:
```
🌐 Initializing language switcher...
Found X language switcher container(s)
📡 Fetching languages from /api/languages...
✓ Response received with status: 200
✓ Languages data received: {...}
✓ Menu 1 populated with 10 languages
✓ Label 1 updated to: English
✅ Language switcher initialized successfully
Setting up dropdown behavior...
Found X language switcher button(s)
✓ Button 1 configured
Dropdown behavior setup complete
```

### Step 4: Test Dropdown Opening

1. **Click the language button** (🌐 icon with language name)
2. **Watch Console** - You should see:
   ```
   Button 1 clicked. Current state: closed
   Opening menu...
   Menu should now be visible. Classes: language-menu opacity-100 visible
   Menu inline styles: display: block; opacity: 1; visibility: visible; pointer-events: auto;
   ```

3. **Visual Check**: The dropdown menu should slide down showing all 10 languages

### Step 5: Test Language Selection

1. **Click a language** (e.g., "Français")
2. **Watch Console** - You should see:
   ```
   Changing to: fr
   Language changed to fr in session
   Updated database: language for user X set to fr
   ```

3. **Visual Check**: 
   - Loading spinner appears briefly
   - Page reloads
   - Language button now shows "Français"

### Step 6: Test on Different Pages

Test on these pages:
- ✅ Landing page (`/`)
- ✅ Sign-in page (`/signin`)
- ✅ Dashboard (after login)
- ✅ Mobile view (resize browser to < 768px width)

### Step 7: Test Edge Cases

1. **Outside Click**: Click anywhere outside the dropdown - it should close
2. **Escape Key**: Press `Esc` key - dropdown should close
3. **Multiple Instances**: If page has multiple language switchers, only one should be open at a time

## API Endpoint Testing

### Test `/api/languages` endpoint:
```bash
# Basic test
curl http://localhost:8080/api/languages

# Should return:
{
  "languages": {
    "en": "English",
    "fr": "Français",
    "sw": "Swahili",
    "pt": "Português",
    "es": "Español",
    "tr": "Türkçe",
    "hi": "हिंदी",
    "zh": "中文",
    "ar": "العربية",
    "vi": "Tiếng Việt"
  },
  "current_language": "en",
  "success": true
}
```

### Test `/api/change-language` endpoint:
```bash
# Change to French
curl -X POST http://localhost:8080/api/change-language \
  -H "Content-Type: application/json" \
  -d '{"language": "fr"}'

# Should return:
{
  "success": true,
  "language": "fr",
  "message": "Language changed to fr"
}
```

## Troubleshooting Guide

### Issue: Dropdown Doesn't Appear

**Check Browser Console for:**
1. Are initialization logs present?
   - ❌ No logs → JavaScript file not loading
   - ✅ Logs present → Continue to next check

2. Does clicking show "Opening menu..." log?
   - ❌ No log → Button event not attached
   - ✅ Log present → Check CSS

3. Check element in DevTools:
   - Inspect the `.language-menu` element
   - Check computed styles: `display`, `opacity`, `visibility`
   - Should be: `display: block`, `opacity: 1`, `visibility: visible`

**Solutions:**
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Clear browser cache
- Check if CSS file is loading: Network tab → look for `language-switcher-fixes.css`

### Issue: API Returns Error

**Check Console for:**
```
❌ Error loading languages: [error message]
```

**Solutions:**
1. Check if Flask app is running
2. Check API endpoint in browser: `http://localhost:8080/api/languages`
3. Check application logs for Python errors
4. Verify database connection is working

### Issue: Language Doesn't Change

**Check Console for:**
```
Changing to: [lang_code]
```

**If no log appears:**
- Menu items might not have click handlers
- Check browser console for JavaScript errors

**If log appears but language doesn't change:**
- Check network tab for `/api/change-language` request
- Check application logs for backend errors
- Verify session is working properly

### Issue: Wrong Language Displayed

**Priority order (from highest to lowest):**
1. Session language (`session['language']`)
2. User database preference (`user.language_preference`)
3. Browser language preference
4. Default (`en`)

**Check:**
- Browser console: "Using language from [source]"
- Network tab → `/api/languages` response → `current_language` field

## Expected Behavior Summary

### ✅ Desktop View
- Language button in top-right corner
- Click → Dropdown opens downward
- Shows all 10 languages
- Current language highlighted
- Click language → Loading → Reload

### ✅ Mobile View  
- Language button in mobile menu footer
- Click → Dropdown opens upward
- Full width on mobile
- Touch-friendly sizing (minimum 44px)

### ✅ Sidebar View (Logged In)
- Language button at bottom of sidebar
- Click → Dropdown opens upward
- Dark theme styling
- Works in collapsed/expanded sidebar

### ✅ Persistence
- Language selection persists across:
  - Page reloads
  - Navigation
  - Browser sessions (if logged in)
  - Different devices (if logged in)

## Debug Mode

To see maximum debugging info, open browser console before using the language switcher. You should see approximately:

- 10-15 logs during initialization
- 3-5 logs when clicking button
- 5-8 logs when changing language
- 2-3 logs when closing dropdown

If you see fewer logs, something isn't working correctly.

## Success Criteria

✅ **Dropdown Opens**: Menu slides down smoothly with animation
✅ **Items Clickable**: Can click any language in the list
✅ **Visual Feedback**: Loading spinner appears during change
✅ **Language Changes**: Page reloads with new language
✅ **Persistence**: Selected language persists after reload
✅ **Multiple Instances**: All instances show same current language
✅ **Keyboard Support**: Escape key closes dropdown
✅ **Mobile Friendly**: Works on small screens
✅ **Accessibility**: Proper ARIA attributes for screen readers

## Next Steps

If everything works:
1. ✅ Clear browser cache
2. ✅ Test on different browsers
3. ✅ Test on mobile devices
4. ✅ Test with different user accounts

If issues persist:
1. Share browser console logs
2. Share Network tab requests/responses
3. Share application logs
4. Share screenshots of the issue

---

**Last Updated**: November 12, 2025
**Status**: Ready for Testing 🚀
