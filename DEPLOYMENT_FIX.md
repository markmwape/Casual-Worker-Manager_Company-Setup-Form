# Deployment Fix - Flask Babel Error

## Error Description
```
ModuleNotFoundError: No module named 'flask_babel'
```

The app was failing to initialize in production because `flask_babel` was imported in `app_init.py` but was missing from `requirements.txt`.

## Fixes Applied

### 1. Added Flask-Babel to requirements.txt
**File**: `requirements.txt`

Added:
```
Flask-Babel
```

This package is required for internationalization (i18n) support in the application.

### 2. Made language_routes import optional
**File**: `app_init.py`

Changed:
```python
# Before
import routes
import language_routes
```

To:
```python
# After
import routes
try:
    import language_routes
except ImportError:
    logging.warning("language_routes module not found - language switching features may be limited")
```

This prevents the app from crashing if the `language_routes` module doesn't exist yet.

## Deployment Steps

1. **Commit the changes**:
   ```bash
   git add requirements.txt app_init.py
   git commit -m "fix: Add Flask-Babel dependency and handle missing language_routes"
   git push origin main
   ```

2. **Redeploy to Cloud Run**:
   The deployment should trigger automatically, or you can manually deploy:
   ```bash
   gcloud run deploy cw-manager-service \
     --source . \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Verify the deployment**:
   - Check that the app starts without errors
   - Test the `/tasks` endpoint
   - Verify worker deletion functionality still works

## What Flask-Babel Does

Flask-Babel provides:
- Translation support (gettext, ngettext)
- Locale selection
- Date/time formatting
- Number formatting

These functions are used in:
- `app_init.py` - Babel initialization
- `routes.py` - Translation functions
- Templates - Internationalized strings

## Additional Notes

If you want to fully implement language switching:
1. Create `language_routes.py` with language selection endpoints
2. Add translation files in `translations/` directory
3. Configure supported languages in `app_init.py`

For now, the app will work with the default language (English) without these additional components.
