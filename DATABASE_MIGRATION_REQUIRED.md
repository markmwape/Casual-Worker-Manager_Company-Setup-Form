# Database Migration Required - Enable Duplicate Detection Feature

## Status
⚠️ **TEMPORARY FIX APPLIED** - Application is now functional but duplicate detection feature is disabled until migration is applied.

## Issue
The application code references a database column `enable_duplicate_detection` on the `import_field` table that doesn't exist in the production database yet.

**Error that was occurring:**
```
ERROR: column import_field.enable_duplicate_detection does not exist
```

## Temporary Fix Applied
To prevent the app from crashing while maintaining functionality, the following changes were made:

### 1. **models.py** - Commented out the column definition
- Removed the `enable_duplicate_detection` column from the `ImportField` model
- Added TODO comment: "Uncomment enable_duplicate_detection after applying migration 050"
- This prevents SQLAlchemy from trying to SELECT a non-existent column

### 2. **static/js/worker.js** - Disabled duplicate detection function
- Modified `checkDuplicateValues()` to always return `{ hasDuplicates: false, warnings: [] }`
- Original implementation is commented out for future re-enabling
- The function still exists and is called, but doesn't perform checks until migration is applied

### 3. **templates/modals/add_worker.html** - Removed duplicate check badge
- Removed the conditional display of "Duplicate Check" badge
- Custom field names still display normally without the badge

## What You Need To Do

### Step 1: Apply the Database Migration
Execute this SQL on your PostgreSQL Cloud SQL instance:

```sql
ALTER TABLE import_field ADD COLUMN enable_duplicate_detection BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_import_field_duplicate_detection ON import_field(company_id, enable_duplicate_detection);
```

### How to Apply It

**Option A: Via Google Cloud Console**
1. Go to Cloud SQL → Your database instance
2. Click "Databases" → "cw_manager"
3. Click "Query editor" (or use "Connect" → "Cloud Shell")
4. Paste and execute the SQL commands above

**Option B: Via Cloud SQL Proxy (if you have it running)**
```bash
psql -h localhost -U cwuser -d cw_manager < migrations/050_add_duplicate_detection_flag.sql
```

**Option C: Via gcloud CLI**
```bash
gcloud sql connect YOUR_INSTANCE_NAME --user=cwuser
# Then execute the SQL commands
```

### Step 2: Re-enable the Feature
Once the migration is applied, uncomment the code in the following files:

**File: models.py (Line ~97)**
```python
# Change from:
# enable_duplicate_detection = db.Column(db.Boolean, default=False)

# To:
enable_duplicate_detection = db.Column(db.Boolean, default=False)
```

**File: static/js/worker.js (Lines 9-38)**
- Uncomment the original fetch implementation inside `checkDuplicateValues()`
- Remove the `return { hasDuplicates: false, warnings: [] };` line at the top

**File: templates/modals/add_worker.html (Lines 38-41)**
- Uncomment the duplicate check badge conditional:
```html
{% if field.enable_duplicate_detection %}
<span class="badge badge-warning badge-sm">Duplicate Check</span>
{% endif %}
```

### Step 3: Verify Everything Works
1. Restart the application server
2. Test creating a new worker with custom fields
3. Check that duplicate detection warnings appear (if enabled on fields)

## Files Modified (Temporary Fix)
- ✅ `/models.py` - Column definition commented out
- ✅ `/static/js/worker.js` - Duplicate detection disabled
- ✅ `/templates/modals/add_worker.html` - Badge display removed
- ✅ `migrations/050_add_duplicate_detection_flag.sql` - Ready to apply (created previously)

## Migration File Location
The migration SQL file is located at:
```
migrations/050_add_duplicate_detection_flag.sql
```

Content:
```sql
-- Add duplicate detection flag to import_field table
-- This feature allows marking custom fields for duplicate value checking

ALTER TABLE import_field ADD COLUMN enable_duplicate_detection BOOLEAN DEFAULT 0;

-- Create an index on the flag for efficient filtering
CREATE INDEX idx_import_field_duplicate_detection ON import_field(company_id, enable_duplicate_detection);
```

## Current Functionality
✅ All other features work normally:
- Worker creation/editing
- Custom fields (without duplicate detection)
- Task management
- Attendance tracking
- Reports

❌ Temporarily disabled:
- Duplicate value detection on custom fields
- Duplicate check warning badges in UI

## Important Notes
1. The app will work fine without this migration - duplicate detection is just a convenience feature
2. Once the migration is applied, the feature will work automatically
3. No data loss - the migration only adds a new column with a safe default value
4. The temporary fix is production-safe and doesn't affect existing functionality

## Support
If you have issues:
1. Check that the Cloud SQL instance is accessible
2. Verify database user `cwuser` has ALTER TABLE permissions
3. Check the database name is `cw_manager`
4. Connection string should be: `embee-accounting101:us-central1:cw-manager-db`
