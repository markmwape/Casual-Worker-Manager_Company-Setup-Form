# Fix Language Preference Column Error

## Problem
You're getting a 500 error when trying to access workspaces:
```
column user.language_preference does not exist
```

This happens because the production database doesn't have the `language_preference` column yet, even though the code expects it.

## Solution

### Option 1: Automatic Fix (Recommended)

Run this migration script on your server after pulling the latest code:

```bash
# 1. SSH into your production server or Cloud Run instance
# 2. Navigate to the app directory
cd /path/to/Casual-Worker-Manager_Company-Setup-Form

# 3. Run the migration script
python3 apply_language_migration.py
```

This script will:
- Check if the column exists
- Create it if needed
- Set the default value to 'en'
- Verify the migration was successful

### Option 2: Manual SQL Fix (If Script Doesn't Work)

Connect directly to your PostgreSQL database and run:

```sql
ALTER TABLE "user"
ADD COLUMN IF NOT EXISTS language_preference VARCHAR(10) DEFAULT 'en' NOT NULL;
```

### Option 3: Cloud SQL Console

If using Google Cloud SQL:

1. Open [Google Cloud Console](https://console.cloud.google.com)
2. Go to Cloud SQL instances
3. Click on your database instance
4. Click "Connect using Cloud Shell"
5. Run the SQL command above:
   ```sql
   ALTER TABLE "user"
   ADD COLUMN IF NOT EXISTS language_preference VARCHAR(10) DEFAULT 'en' NOT NULL;
   ```

### Option 4: Using Cloud SQL Proxy

```bash
# Start Cloud SQL proxy (replace with your connection name)
cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432

# In another terminal, connect to the database
psql -h 127.0.0.1 -U postgres

# Enter your password, then run:
ALTER TABLE "user"
ADD COLUMN IF NOT EXISTS language_preference VARCHAR(10) DEFAULT 'en' NOT NULL;
```

## What Was Changed

The multi-language support feature added a new column to the User table:
- **Column name**: `language_preference`
- **Type**: VARCHAR(10)
- **Default value**: 'en' (English)
- **Purpose**: Stores user's preferred language code

## After Fixing

Once the column is added:
1. Restart your Cloud Run service or application
2. Try accessing workspaces again - the error should be gone
3. Users can now switch languages using the 🌐 button
4. Their language preference will be saved to this column

## Verification

After applying the migration, you can verify it worked:

```sql
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name='user' AND column_name='language_preference';
```

This should return:
```
column_name          | data_type
language_preference  | character varying
```

## Need Help?

If the migration still doesn't work:
1. Check that Flask-Babel is installed: `pip list | grep Flask-Babel`
2. Check database connection is working
3. Verify you have the right database permissions
4. Check application logs for detailed error messages

