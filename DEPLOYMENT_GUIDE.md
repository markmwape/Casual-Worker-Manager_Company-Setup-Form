# 🚀 Deployment Guide - Foreign Key Fix

## Issue Fixed
The foreign key constraint violation when associating Google emails with workspaces has been fixed in the code. Now you need to deploy the changes to production.

## What Was Fixed
The `associate_workspace_email` function in `routes.py` now properly:
1. ✅ Updates `workspace.created_by` before deleting placeholder user
2. ✅ Updates all `company.created_by` references
3. ✅ Deletes `UserWorkspace` records for placeholder user
4. ✅ Nullifies `worker.user_id` references
5. ✅ Uses proper transaction management with rollback
6. ✅ Comprehensive error handling and logging

## Deployment Steps

### Option 1: Quick Deploy via Cloud Build (Recommended)

```bash
# Navigate to project directory
cd "/Users/markbonganimwape/Desktop/Casual Worker Manager_Company Setup Form"

# Deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml

# This will:
# - Build the Docker container
# - Push to Google Container Registry
# - Deploy to Cloud Run automatically
# - No downtime deployment
```

### Option 2: Deploy via Shell Script

```bash
# Navigate to project directory
cd "/Users/markbonganimwape/Desktop/Casual Worker Manager_Company Setup Form"

# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Option 3: Manual Deploy

```bash
# Set your Google Cloud project
gcloud config set project embee-accounting101

# Deploy from source
gcloud run deploy cw-manager-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --max-instances 10 \
  --port 8080 \
  --set-env-vars="INSTANCE_CONNECTION_NAME=embee-accounting101:us-central1:cw-manager-db,DB_USER=cwuser,DB_NAME=cw_manager,GOOGLE_CLOUD_PROJECT=embee-accounting101" \
  --update-secrets="DB_PASS=db-pass:latest" \
  --add-cloudsql-instances=embee-accounting101:us-central1:cw-manager-db
```

## Pre-Deployment Checklist

- [x] Code fix implemented in `routes.py`
- [x] Syntax errors checked (compiles successfully)
- [x] Error handling with rollback added
- [x] Comprehensive logging added
- [ ] **Commit changes to Git**
- [ ] **Deploy to production**

## Commit Changes First

```bash
# Stage the changes
git add routes.py

# Commit with descriptive message
git commit -m "Fix foreign key constraint violation in associate_workspace_email

- Update workspace.created_by before deleting placeholder user
- Update all company.created_by references
- Delete UserWorkspace records for placeholder user
- Nullify worker.user_id references
- Add proper transaction management with rollback
- Add comprehensive error handling and logging

Fixes: psycopg2.errors.ForeignKeyViolation on user deletion"

# Push to main branch
git push origin main
```

## Post-Deployment Verification

### 1. Check Deployment Status
```bash
gcloud run services describe cw-manager-service --region=us-central1
```

### 2. View Live Logs
```bash
gcloud logs tail --service=cw-manager-service --region=us-central1
```

### 3. Test the Fix
1. Go to https://embeeaccounting.com
2. Click "Create New Workspace"
3. Fill in the workspace details
4. Click "Sign in with Google"
5. Complete Google authentication
6. **Should now succeed without errors!**

### 4. Look for Success Messages in Logs
You should see:
```
✓ TRANSFERRING OWNERSHIP: workspace [name] from pending_* to [your-email]
✓ Updated workspace.created_by to [user_id]
✓ Updated [N] companies to be owned by user [user_id]
✓ Deleted placeholder user: [email]
✓ COMMITTED: All changes saved to database
✓ VERIFICATION: UserWorkspace exists: True, Role: Admin
✓ VERIFIED: Placeholder user was successfully deleted
✓ VERIFIED: Workspace ownership successfully transferred
✓✓✓ Successfully associated email [email] with workspace [name] as Admin ✓✓✓
```

## Rollback Plan (If Issues Occur)

```bash
# List recent revisions
gcloud run revisions list --service=cw-manager-service --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic cw-manager-service \
  --to-revisions=[PREVIOUS_REVISION]=100 \
  --region=us-central1
```

## Database Cleanup (If Needed)

If you have orphaned placeholder users from the old code, you can clean them up:

```sql
-- Connect to your Cloud SQL database
-- Find placeholder users that are still referenced
SELECT u.id, u.email, 
       COUNT(DISTINCT w.id) as workspace_count,
       COUNT(DISTINCT c.id) as company_count
FROM "user" u
LEFT JOIN workspace w ON w.created_by = u.id
LEFT JOIN company c ON c.created_by = u.id
WHERE u.email LIKE 'pending_%'
GROUP BY u.id, u.email;

-- Manual cleanup (if needed) - BE CAREFUL!
-- The new code will handle this automatically for new workspaces
```

## Expected Behavior After Fix

1. **Workspace Creation**: User creates workspace → Placeholder user created
2. **Google Sign-In**: User signs in → `associate_workspace_email` called
3. **Ownership Transfer**: 
   - ✅ All foreign keys updated first
   - ✅ Placeholder user deleted safely
   - ✅ No foreign key violations
4. **Success**: User gets Admin access to workspace

## Monitoring

Watch these metrics after deployment:
- Error rate on `/api/workspace/associate-email` endpoint
- Number of successful workspace associations
- Foreign key violation errors (should be zero)

## Support

If you encounter any issues:
1. Check logs: `gcloud logs tail --service=cw-manager-service --region=us-central1`
2. Look for the error handling messages
3. Check if transaction was rolled back
4. Verify database state hasn't been corrupted

## Estimated Deployment Time
- Build: ~5-10 minutes
- Deploy: ~2-3 minutes
- Total: ~10-15 minutes

## Zero Downtime
Google Cloud Run provides zero-downtime deployments:
- New version is deployed alongside old version
- Traffic gradually shifts to new version
- Old version kept running until new version is healthy
- Automatic rollback if health checks fail

---

**Status**: ⚠️ READY TO DEPLOY - Code fixed locally, waiting for production deployment
