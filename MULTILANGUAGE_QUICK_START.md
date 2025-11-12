# Multi-Language Setup - Quick Start Guide

## What Was Done ✅

Your Casual Worker Manager application now has **full multi-language support** with 10 languages:

- 🇬🇧 English
- 🇫🇷 French
- 🇹🇿 Swahili
- 🇵🇹 Portuguese
- 🇪🇸 Spanish
- 🇹🇷 Turkish
- 🇮🇳 Hindi
- 🇨🇳 Chinese
- 🇸🇦 Arabic

## Installation Steps

### Step 1: Install Flask-Babel
```bash
pip install -r requirements.txt
```

or specifically:
```bash
pip install Flask-Babel==2.0.0
```

### Step 2: Update Your Database
Run this command to add the language preference column to your User table:

```bash
/usr/local/bin/python3 -c "from app_init import app, db; app.app_context().push(); db.create_all()"
```

### Step 3: Restart Your Application
```bash
python main.py
```

or if using a specific Python version:
```bash
/usr/local/bin/python3 main.py
```

## What You Get

### 1. Language Switcher Button 🌐
- Appears in the sidebar (bottom, next to Sign Out)
- Appears in the header component
- Click the globe icon to select your language
- Works on all pages

### 2. Automatic Language Persistence
- User's language choice is saved to the database
- Loads automatically on next login
- No need to re-select language each time

### 3. Browser Language Detection
- If not logged in, detects your browser's preferred language
- Falls back to English if your language isn't supported

## How to Use

### For Users:
1. Look for the globe icon (🌐) in the sidebar or header
2. Click it to open the language menu
3. Select your preferred language
4. The page reloads with the selected language

### For Developers:
See `MULTILANGUAGE_SETUP.md` for detailed instructions on:
- Adding new translations
- Using translations in templates
- Using translations in JavaScript
- Extending to more content

## File Structure

```
├── app_init.py                           # Updated with Babel configuration
├── language_routes.py                    # NEW: Language switching API endpoints
├── translation_manager.py                # NEW: Translation management utility
├── models.py                             # Updated with language_preference field
├── babel.cfg                             # NEW: Babel configuration
├── requirements.txt                      # Updated with Flask-Babel
├── static/
│   ├── js/
│   │   └── i18n.js                      # NEW: Frontend translation utility
│   └── translations/                     # NEW: Translation JSON files
│       ├── en.json
│       ├── fr.json
│       ├── sw.json
│       ├── pt.json
│       ├── es.json
│       ├── tr.json
│       ├── hi.json
│       ├── zh.json
│       └── ar.json
├── templates/
│   ├── base.html                         # Updated with language switcher
│   ├── header_component.html             # Updated with language switcher
│   └── components/
│       └── language_switcher.html        # NEW: Language switcher component
├── migrations/
│   └── 040_add_user_language_preference.sql  # NEW: Database migration
├── MULTILANGUAGE_SETUP.md                # NEW: Detailed documentation
└── MULTILANGUAGE_QUICK_START.md          # NEW: This file
```

## API Endpoints

### Change User Language
```
POST /api/change-language
Content-Type: application/json

{
    "language": "fr"
}
```

### Get Available Languages
```
GET /api/languages
```

Returns:
```json
{
    "languages": {
        "en": "English",
        "fr": "Français",
        ...
    },
    "current_language": "en"
}
```

## Testing

1. **Login to your application**
2. **Click the globe icon (🌐)** in the sidebar
3. **Select a language** (e.g., French)
4. **Page should reload** with French translations
5. **Your preference is saved** - logout and login again, French should be the default

## Troubleshooting

### Issue: Language switcher doesn't appear
**Solution:**
- Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
- Check browser console for errors (F12)
- Verify `/api/languages` endpoint returns data

### Issue: Translations show as English
**Solution:**
- Check that `static/translations/` directory has JSON files
- Run `python translation_manager.py` again
- Verify Flask-Babel is installed: `pip list | grep Babel`

### Issue: Database errors about missing column
**Solution:**
- Run: `/usr/local/bin/python3 -c "from app_init import app, db; app.app_context().push(); db.create_all()"`
- Or run the SQL migration manually

### Issue: 404 errors for translation files
**Solution:**
- Ensure `static/` directory is properly configured in Flask
- Check that translation JSON files exist in `static/translations/`
- Verify Flask can serve static files (should work by default)

## Next Steps

### To Expand Translations:
1. Open `translation_manager.py`
2. Add your new English text to the `TRANSLATIONS` dictionary
3. Add translations for each language
4. Run `python translation_manager.py` to generate JSON files

### Example:
```python
"Welcome to the Dashboard": {
    "fr": "Bienvenue au tableau de bord",
    "sw": "Karibu kwenye dashibodi",
    "pt": "Bem-vindo ao painel de controle",
    # ... etc
}
```

### To Use Translations in Templates:
```html
<!-- Use data-i18n attribute -->
<h1 data-i18n="Welcome to the Dashboard">Welcome to the Dashboard</h1>
```

### To Use Translations in JavaScript:
```javascript
// After page loads
const message = window.i18n.t('Your text here');
```

## Performance

- ✅ Lightweight: Translation files are JSON (~2KB each)
- ✅ Cached: Language selection doesn't require API calls
- ✅ Fast: No external translation API needed
- ✅ Efficient: Browser caches translations locally

## Support for New Languages

To add more languages (e.g., German, Italian, Japanese):

1. Add to `app_init.py`:
```python
'de': 'Deutsch',
'it': 'Italiano',
'ja': '日本語',
```

2. Add translations to `translation_manager.py`
3. Run `python translation_manager.py`
4. Done!

---

**Status:** ✅ Ready to use
**Last Updated:** November 2025
**Support:** 10 languages
