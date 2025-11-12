# Translation Keys Reference Guide

## 🎯 Quick Reference - All Translation Keys

This guide lists all 167 new translation keys added to support Reports, Attendance, Units pages and all modal forms across 10 languages.

---

## 📋 Reports Section (41 keys)

Used in: `templates/reports.html`

```
reports.aboutReportGeneration
reports.actions
reports.addCustomField
reports.attendanceDays
reports.attendanceRecordsFound
reports.chooseFormat
reports.configureTimeframe
reports.csvDescription
reports.csvFile
reports.currentFields
reports.customFields
reports.dailyRate
reports.dateRange
reports.downloadPerDay
reports.downloadPerUnit
reports.endDate
reports.excelDescription
reports.excelFile
reports.fieldName
reports.firstName
reports.formulaValue
reports.lastName
reports.noCustomFields
reports.noPerDayRecords
reports.noPerUnitRecords
reports.perDayReport
reports.perDaySubtitle
reports.perUnitRate
reports.perUnitReport
reports.perUnitSubtitle
reports.quickActions
reports.recordAttendance
reports.recordsSync
reports.reportInfo
reports.selectFileFormat
reports.startDate
reports.subtitle
reports.taskName
reports.title
reports.unitRecordsFound
reports.unitsCompleted
```

---

## 👥 Attendance Section (26 keys)

Used in: `templates/task_attendance.html`

```
attendance.absent
attendance.absentCount
attendance.addWorker
attendance.attendanceCannotRecordBefore
attendance.attendanceOnlyAvailable
attendance.backToTasks
attendance.backToToday
attendance.cannotRecordBefore
attendance.dateError
attendance.dateNavigation
attendance.enterUnits
attendance.name
attendance.nextDay
attendance.present
attendance.presentCount
attendance.previousDay
attendance.recordedAttendance
attendance.recordedUnits
attendance.save
attendance.searchByField
attendance.selectTaskDate
attendance.thisDataWillAppear
attendance.title
attendance.totalUnits
attendance.unitsCompleted
attendance.workers
```

---

## 📊 Units Section (17 keys)

Used in: `templates/task_units_completed.html`

```
units.addWorker
units.backToTasks
units.backToToday
units.cannotRecordBefore
units.dateError
units.dateNavigation
units.enterUnits
units.name
units.nextDay
units.payoutPerUnit
units.previousDay
units.save
units.searchByField
units.selectTaskDate
units.title
units.unitsCompleted
units.unitsOnlyAvailable
```

---

## 🔧 Modal Forms - 83 keys

### Add Worker Modal (11 keys)

Used in: `templates/modals/add_worker.html`

```
modals.addWorker.addCustomField
modals.addWorker.addField
modals.addWorker.addWorker
modals.addWorker.cancel
modals.addWorker.customFields
modals.addWorker.dateOfBirth
modals.addWorker.deleteConfirmation
modals.addWorker.fieldName
modals.addWorker.firstName
modals.addWorker.lastName
modals.addWorker.title
```

### Import Workers Modal (20 keys)

Used in: `templates/modals/import_workers.html`

```
modals.importWorkers.addField
modals.importWorkers.addNewField
modals.importWorkers.back
modals.importWorkers.cancel
modals.importWorkers.chooseExcelFile
modals.importWorkers.currentFields
modals.importWorkers.done
modals.importWorkers.excelColumn
modals.importWorkers.fieldNameCol
modals.importWorkers.fieldNamePlaceholder
modals.importWorkers.importComplete
modals.importWorkers.importWorkers
modals.importWorkers.manageFields
modals.importWorkers.mapColumns
modals.importWorkers.subtitle
modals.importWorkers.supportedFormats
modals.importWorkers.theseFieldsWillBeMapped
modals.importWorkers.title
modals.importWorkers.uploadAndMap
modals.importWorkers.workersImported
```

### Create Task Modal (28 keys)

Used in: `templates/modals/add_task.html`

```
modals.addTask.cancel
modals.addTask.chooseWhenTaskBegins
modals.addTask.clickToSelect
modals.addTask.confirm
modals.addTask.createTask
modals.addTask.dailyPayoutAmount
modals.addTask.dailyRate
modals.addTask.dailyTip
modals.addTask.description
modals.addTask.descriptionPlaceholder
modals.addTask.enterAmount
modals.addTask.enterAmountPerUnit
modals.addTask.fixedDailyAmount
modals.addTask.paymentPerItem
modals.addTask.paymentType
modals.addTask.perUnit
modals.addTask.perUnitPayoutAmount
modals.addTask.selectCurrency
modals.addTask.selectDate
modals.addTask.selectStartDate
modals.addTask.selected
modals.addTask.startDate
modals.addTask.subtitle
modals.addTask.taskName
modals.addTask.taskNamePlaceholder
modals.addTask.tip
modals.addTask.title
modals.addTask.unitsTip
```

### Edit Task Modal (24 keys)

Used in: `templates/modals/edit_task.html`

```
modals.editTask.cancel
modals.editTask.chooseWhenTaskBegins
modals.editTask.clickToSelect
modals.editTask.dailyPayoutAmount
modals.editTask.dailyRate
modals.editTask.dailyTip
modals.editTask.description
modals.editTask.enterAmount
modals.editTask.enterAmountPerUnit
modals.editTask.fixedDailyAmount
modals.editTask.paymentPerItem
modals.editTask.paymentType
modals.editTask.perUnit
modals.editTask.perUnitPayoutAmount
modals.editTask.saveChanges
modals.editTask.selectCurrency
modals.editTask.selectStartDate
modals.editTask.selected
modals.editTask.startDate
modals.editTask.subtitle
modals.editTask.taskName
modals.editTask.tip
modals.editTask.title
modals.editTask.unitsTip
```

---

## 💻 How to Use in HTML

### Text Content
```html
<h1 data-i18n="reports.title">Reports</h1>
<p data-i18n="reports.subtitle">Detailed report display</p>
<button data-i18n="attendance.addWorker">Add Worker</button>
```

### Placeholders
```html
<input type="text" data-i18n-attr="modals.addTask.taskNamePlaceholder" 
       placeholder="e.g., Cleaning Service">
```

### Attributes
```html
<select data-i18n-attr="modals.addTask.selectCurrency">
    <option value="">Select Currency</option>
</select>
```

---

## 🌍 Language Codes

- **ar** - Arabic (العربية)
- **en** - English
- **es** - Spanish (Español)
- **fr** - French (Français)
- **hi** - Hindi (हिन्दी)
- **pt** - Portuguese (Português)
- **sw** - Swahili (Kiswahili)
- **tr** - Turkish (Türkçe)
- **vi** - Vietnamese (Tiếng Việt)
- **zh** - Chinese Simplified (简体中文)

---

## 📱 HTML Template Coverage

| Template | Location | Keys | Status |
|----------|----------|------|--------|
| Reports | `templates/reports.html` | 41 | ✅ Complete |
| Attendance | `templates/task_attendance.html` | 26 | ✅ Complete |
| Units | `templates/task_units_completed.html` | 17 | ✅ Complete |
| Add Worker | `templates/modals/add_worker.html` | 11 | ✅ Complete |
| Import Workers | `templates/modals/import_workers.html` | 20 | ✅ Complete |
| Create Task | `templates/modals/add_task.html` | 28 | ✅ Complete |
| Edit Task | `templates/modals/edit_task.html` | 24 | ✅ Complete |
| **TOTAL** | - | **167** | **✅ Complete** |

---

## 🔍 Finding Keys in JSON Files

Each language JSON file (`static/translations/{lang}.json`) contains the same key structure:

```json
{
  "reports": {
    "title": "Reports",
    "subtitle": "...",
    ...
  },
  "attendance": {
    "title": "Attendance",
    ...
  },
  "units": {
    "title": "Units",
    ...
  },
  "modals": {
    "addWorker": { ... },
    "importWorkers": { ... },
    "addTask": { ... },
    "editTask": { ... }
  }
}
```

---

## ✨ Example Usage

### JavaScript Translation
```javascript
// In i18n.js
i18n.t('reports.title')  // Returns "Reports" (or translation)
i18n.t('modals.addTask.dailyRate')  // Returns "Daily Rate"
```

### Dynamic Page Translation
```javascript
// Automatic via data-i18n attributes
translatePage()  // Updates all elements with data-i18n
```

### Language Switching
```javascript
// Call API to switch language
fetch('/api/language/set', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ language: 'fr' })
})
```

---

## 📊 Statistics

- **Total Keys**: 167
- **Languages**: 10
- **Total Translations**: 1,670+
- **Coverage**: 100% UI elements
- **Files Modified**: 7 HTML templates + 10 JSON files
- **Production Ready**: ✅ Yes

---

## 🚀 Maintenance

### Adding a New Language

1. Create `static/translations/{lang_code}.json`
2. Copy structure from `en.json`
3. Translate all 150+ keys
4. Save and restart application

### Updating Translations

1. Edit `static/translations/{lang_code}.json`
2. Update specific key values
3. Save and refresh page
4. Changes apply immediately (no restart needed)

### Adding New Translation Keys

1. Add key to all language JSON files
2. Add `data-i18n="section.key"` to HTML
3. JavaScript automatically picks up and translates
4. No code changes needed

---

## 🔗 Related Documentation

- `TRANSLATION_COMPLETION_SUMMARY.md` - Overall project summary
- `MULTI_LANGUAGE_COMPLETION_CHECKLIST.md` - Detailed checklist
- `static/js/i18n.js` - i18n JavaScript library
- `static/translations/*.json` - Translation files

---

**Last Updated**: 2024  
**Version**: 1.0  
**Status**: ✅ Production Ready

