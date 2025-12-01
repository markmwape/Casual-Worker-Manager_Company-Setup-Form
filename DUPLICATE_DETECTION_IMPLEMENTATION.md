# Duplicate Detection System - Implementation Guide

## Overview
The duplicate detection system allows users to enable/disable duplicate checking on custom fields. When enabled, the system prevents workers from being added with duplicate values in those fields.

## Backend Implementation

### 1. Database Schema
- **Table**: `import_field`
- **Column**: `enable_duplicate_detection` (Boolean, default=False)
- **Migration**: `051_add_duplicate_detection_column.py`

### 2. Core Helper Function
**Location**: `routes.py`

```python
def check_duplicate_custom_fields(company_id, custom_field_data, exclude_worker_id=None):
```

**Purpose**: Checks if any custom field values violate duplicate detection rules.

**Parameters**:
- `company_id`: The company to check within
- `custom_field_data`: Dictionary of `{field_id or field_name: value}` to check
- `exclude_worker_id`: Optional worker ID to exclude (for updates)

**Returns**: `(has_duplicates: bool, duplicate_fields: list)`

**Features**:
- Handles multiple field identifier formats (ID, name, custom_field_{id})
- Only checks fields where `enable_duplicate_detection=True`
- Excludes current worker when updating (prevents false positives)
- Returns list of fields with duplicates for detailed error messages

### 3. API Endpoints

#### Create Worker: `/api/worker` (POST)
**Before Worker Creation**:
1. Collects all custom field data from request
2. Calls `check_duplicate_custom_fields()`
3. If duplicates found → Returns 409 error with field names
4. If no duplicates → Proceeds with worker creation

**Response Codes**:
- `201`: Worker created successfully
- `409`: Duplicate values detected (with field list)
- `500`: Server error

#### Update Worker: `/api/worker/<id>` (PUT)
**Before Worker Update**:
1. Collects custom field data being updated
2. Calls `check_duplicate_custom_fields()` with `exclude_worker_id`
3. If duplicates found → Returns 409 error
4. If no duplicates → Proceeds with update

**Response Codes**:
- `200`: Worker updated successfully
- `409`: Duplicate values detected (with field list)
- `404`: Worker not found
- `500`: Server error

#### Import Workers: `/api/worker/import-mapped` (POST)
**For Each Row in Excel**:
1. Builds custom field data from mapped columns
2. Calls `check_duplicate_custom_fields()`
3. If duplicates found → Skips row, increments duplicate counter
4. If no duplicates → Creates worker

**Import Summary**:
```json
{
  "successful_imports": 10,
  "duplicate_records": 3,
  "error_records": 1,
  "error_details": ["Row 5: Duplicate values in Employee ID", ...]
}
```

#### Check Duplicates: `/api/worker/check-duplicates` (POST)
**Purpose**: Frontend validation before submission

**Request Body**:
```json
{
  "custom_field_1": "EMP001",
  "custom_field_2": "john@example.com"
}
```

**Response**:
```json
{
  "hasDuplicates": true,
  "warnings": ["Duplicate value 'EMP001' found in field 'Employee ID'"]
}
```

#### Toggle Duplicate Detection: `/api/import-field/<id>` (PUT)
**Request Body**:
```json
{
  "enable_duplicate_detection": true
}
```

**Response**:
```json
{
  "id": 1,
  "name": "Employee ID",
  "field_type": "text",
  "enable_duplicate_detection": true
}
```

## Frontend Implementation

### 1. UI Components

#### Add Worker Modal (`add_worker.html`)
**For Each Custom Field**:
- Field name label
- "Duplicate Check" badge (when enabled)
- Toggle switch with label "Check duplicates"
- Delete button

**Toggle Behavior**:
- When enabling → Direct API call
- When disabling → Shows warning modal first
- Updates badge visibility after toggle

#### Import Workers Modal (`import_workers.html`)
**Same UI as Add Worker Modal**:
- All fields show toggles
- Consistent badge display
- Same warning on disable

#### Warning Modal (`disableDuplicateWarningModal`)
**Shown When**: User tries to disable duplicate detection

**Content**:
- Warning icon and title
- Explanation of implications
- Highlighted risks (manual + import duplicates possible)
- Cancel / Confirm buttons

### 2. JavaScript Functions

#### `toggleDuplicateDetection(fieldId, enabled)`
**Purpose**: Handle toggle state changes

**Flow**:
1. If disabling → Show warning modal
2. If confirmed or enabling → Call `performDuplicateToggle()`
3. Update badge visibility
4. Reload both modals to sync

#### `performDuplicateToggle(fieldId, enabled)`
**Purpose**: Execute the API call

**Flow**:
1. Send PUT request to `/api/import-field/<id>`
2. On success → Update badges, show toast, reload fields
3. On error → Revert toggle, show error toast

#### `updateDuplicateBadges(fieldId, enabled)`
**Purpose**: Update badge visibility across all modals

**Flow**:
1. Find all field elements with matching `data-field-id`
2. Add/remove "Duplicate Check" badge based on `enabled`

#### `check DuplicateValues(formData)`
**Purpose**: Frontend validation before form submission

**Flow**:
1. Send POST to `/api/worker/check-duplicates`
2. Parse response for warnings
3. Return `{hasDuplicates, warnings}`

### 3. Form Submission Flow

#### Manual Worker Addition
```javascript
1. User fills form
2. Frontend calls checkDuplicateValues() [soft check]
3. If duplicates → Show confirmation dialog
4. User submits form
5. Backend enforces check_duplicate_custom_fields() [hard check]
6. If 409 error → Show error toast with field names
7. If 201 success → Close modal, reload page
```

#### Excel Import
```javascript
1. User uploads file
2. Maps columns to fields
3. Clicks "Import Workers"
4. Backend processes each row:
   - Checks duplicates using check_duplicate_custom_fields()
   - Skips rows with duplicates
   - Creates valid workers
5. Returns summary with duplicate count
6. Frontend shows import results
```

## User Experience Flow

### Creating a New Custom Field
1. User enters field name
2. User checks "Check for duplicates" checkbox (optional)
3. Clicks "Add Field"
4. Field appears with toggle already set to their choice

### Enabling Duplicate Detection
1. User sees existing field with toggle OFF
2. User clicks toggle ON
3. System immediately saves setting
4. Badge appears next to field name
5. Toast notification confirms

### Disabling Duplicate Detection
1. User sees field with toggle ON and badge
2. User clicks toggle OFF
3. Warning modal appears explaining risks
4. User can Cancel (toggle stays ON) or Confirm
5. If confirmed → Setting saved, badge disappears
6. Toast notification confirms

### Adding Worker with Duplicate
1. User fills form with duplicate value
2. Clicks "Add Worker"
3. Backend detects duplicate
4. Error toast appears: "Duplicate values detected in: Employee ID"
5. Form stays open, user can correct value

### Importing with Duplicates
1. User uploads Excel with 100 rows
2. 5 rows have duplicate Employee IDs (detection enabled)
3. Import completes with summary:
   - 95 workers imported successfully
   - 5 duplicate records skipped
   - Error details show which rows/fields had duplicates

## Error Handling

### Backend Errors
- **409 Conflict**: Duplicate values detected (user-facing)
- **500 Server Error**: Database or processing error (generic message)
- **401 Unauthorized**: Session expired (redirect to login)
- **404 Not Found**: Worker or field not found

### Frontend Error Display
```javascript
// 409 Duplicate Error
"Duplicate values detected in: Employee ID, Email Address"

// Generic Error
"Failed to save worker. Please try again."

// Network Error
"Connection error. Please check your internet connection."
```

## Testing Checklist

### Manual Worker Addition
- [ ] Create field with duplicate detection ON
- [ ] Try adding worker with existing value → Blocked
- [ ] Toggle detection OFF → Can add duplicate
- [ ] Update worker with duplicate value → Blocked
- [ ] Update worker to unique value → Success

### Excel Import
- [ ] Import file with duplicates in enabled field → Rows skipped
- [ ] Import file with duplicates in disabled field → All imported
- [ ] Check import summary shows correct duplicate count
- [ ] Error details list specific rows with duplicates

### Toggle Behavior
- [ ] Toggle ON → Badge appears
- [ ] Toggle OFF → Warning modal shows
- [ ] Cancel warning → Toggle reverts to ON
- [ ] Confirm warning → Toggle stays OFF, badge removed
- [ ] Changes sync between Add Worker and Import modals

### Edge Cases
- [ ] Empty values not checked for duplicates
- [ ] Whitespace trimmed before comparison
- [ ] Case-sensitive duplicate detection
- [ ] Multiple fields with detection enabled
- [ ] Updating worker's own value not flagged as duplicate
- [ ] Field ID vs field name in API requests

## Configuration

### Enable/Disable Globally
To temporarily disable duplicate detection system:
```python
# In routes.py, modify check_duplicate_custom_fields()
def check_duplicate_custom_fields(...):
    return False, []  # Always return no duplicates
```

### Default Behavior
New custom fields have `enable_duplicate_detection=False` by default.
Users must explicitly enable it per field.

## Performance Considerations

### Database Queries
- Duplicate checks use indexed JOIN queries
- Each check queries `worker_custom_field_value` + `worker` tables
- Import process: O(n) where n = number of rows × enabled fields

### Optimization Tips
1. Add database index on `custom_field_id` and `value` columns
2. Batch import checks if performance becomes an issue
3. Consider caching for frequently checked values

## Future Enhancements

### Potential Improvements
1. **Case-insensitive option**: Toggle for case-sensitive/insensitive matching
2. **Fuzzy matching**: Detect similar values (e.g., "john@email.com" vs "John@Email.com")
3. **Bulk toggle**: Enable/disable detection for all fields at once
4. **Duplicate merge**: UI to merge duplicate workers found during import
5. **Historical tracking**: Log when duplicates are detected/bypassed
6. **Field-specific rules**: Different validation rules per field type

### API Extensions
```python
# Proposed endpoint for batch operations
POST /api/import-field/bulk-update
{
  "field_ids": [1, 2, 3],
  "enable_duplicate_detection": true
}
```

## Troubleshooting

### "Duplicate values detected" but value is unique
**Cause**: Whitespace or case differences
**Solution**: Check actual stored values in database

### Toggle not syncing between modals
**Cause**: Fields not refreshing after toggle
**Solution**: Ensure `reloadCustomFields()` and `loadImportFields()` are called

### Import showing wrong duplicate count
**Cause**: Duplicate check happening before custom_field_data built
**Solution**: Verify check is after data mapping (around line 4095 in routes.py)

### 409 errors not showing proper message
**Cause**: Frontend not handling 409 status code
**Solution**: Check fetch().then() chain includes 409 handling

## Migration Guide

### From Previous Version
1. Run Alembic migration: `alembic upgrade head`
2. All existing fields default to `enable_duplicate_detection=False`
3. No behavior changes until users enable detection per field
4. Frontend changes backward compatible

### Rollback
```bash
# Downgrade database
alembic downgrade -1

# Or manually:
ALTER TABLE import_field DROP COLUMN enable_duplicate_detection;
```

## Support

### Common User Questions

**Q: Can I enable duplicate detection after workers are already added?**
A: Yes, it only affects new workers being added, not existing ones.

**Q: Will enabling detection remove existing duplicates?**
A: No, it only prevents new duplicates from being added.

**Q: Can I temporarily allow duplicates?**
A: Yes, toggle the detection OFF for that field temporarily.

**Q: What if two fields have the same value but only one has detection?**
A: Only the field with detection enabled will block duplicates.

---

**Last Updated**: December 1, 2025
**Version**: 1.0
**Author**: Development Team
