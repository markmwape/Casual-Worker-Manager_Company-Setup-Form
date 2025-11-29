// Use showToast from global scope (defined in script.js)
console.log('[worker.js] Script loading...');
console.log('[worker.js] window.addCustomField before definition:', typeof window.addCustomField);

// ============================================================================
// DUPLICATE DETECTION AND DATE VALIDATION FUNCTIONS
// ============================================================================

async function checkDuplicateValues(formData) {
    /**
     * Check for duplicate values in custom fields marked with duplicate detection
     * NOTE: This feature requires database migration 051 to be applied
     * Returns: { hasDuplicates: boolean, warnings: string[] }
     */
    // TODO: Re-enable once migration 051 runs successfully
    return { hasDuplicates: false, warnings: [] };
    
    /* Original implementation (disabled until migration is applied):
    try {
        const response = await fetch('/api/worker/check-duplicates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin',
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            console.error('Failed to check duplicates:', response.status);
            return { hasDuplicates: false, warnings: [] };
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error checking duplicates:', error);
        return { hasDuplicates: false, warnings: [] };
    }
    */
}

async function validateDateFormat(dateStr) {
    /**
     * Validate and normalize date format
     * Handles multiple formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, etc.
     */
    if (!dateStr) return { isValid: true, normalizedDate: null };
    
    const dateStr_trimmed = dateStr.trim();
    
    // Already in correct format
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr_trimmed)) {
        // Validate the date is real
        const date = new Date(dateStr_trimmed + 'T00:00:00Z');
        if (!isNaN(date.getTime())) {
            return { isValid: true, normalizedDate: dateStr_trimmed };
        }
        return { isValid: false, normalizedDate: null };
    }
    
    // Try to parse other formats
    let parsedDate = null;
    
    // DD/MM/YYYY or DD-MM-YYYY
    const slashMatch = dateStr_trimmed.match(/^(\d{1,2})[\/-](\d{1,2})[\/-](\d{4})$/);
    if (slashMatch) {
        const [_, part1, part2, year] = slashMatch;
        const p1 = parseInt(part1);
        const p2 = parseInt(part2);
        
        // Determine if DD/MM or MM/DD based on values
        let month, day;
        if (p1 > 12) {
            // Must be DD/MM
            day = p1;
            month = p2;
        } else if (p2 > 12) {
            // Must be MM/DD
            month = p1;
            day = p2;
        } else {
            // Ambiguous - assume DD/MM (European format is more common)
            day = p1;
            month = p2;
        }
        
        parsedDate = new Date(parseInt(year), month - 1, day);
    }
    
    // Validate the parsed date
    if (parsedDate && !isNaN(parsedDate.getTime())) {
        const normalized = `${parsedDate.getFullYear()}-${String(parsedDate.getMonth() + 1).padStart(2, '0')}-${String(parsedDate.getDate()).padStart(2, '0')}`;
        return { isValid: true, normalizedDate: normalized };
    }
    
    return { isValid: false, normalizedDate: null };
}

window.checkDuplicateValues = checkDuplicateValues;
window.validateDateFormat = validateDateFormat;

// Custom Modal Functions
function showCustomModal(title, message, type = 'info') {
    return new Promise((resolve) => {
        const modal = document.createElement('dialog');
        modal.className = 'modal';
        
        let iconClass = 'fas fa-info-circle text-blue-500';
        if (type === 'success') {
            iconClass = 'fas fa-check-circle text-green-500';
        } else if (type === 'error') {
            iconClass = 'fas fa-exclamation-circle text-red-500';
        } else if (type === 'warning') {
            iconClass = 'fas fa-exclamation-triangle text-yellow-500';
        }
        
        modal.innerHTML = `
            <div class="modal-box">
                <h3 class="font-bold text-lg flex items-center gap-2">
                    <i class="${iconClass}"></i>
                    <span>${title}</span>
                </h3>
                <p class="py-4">${message}</p>
                <div class="modal-action">
                    <button type="button" class="btn btn-primary" onclick="this.closest('dialog').close(); this.closest('dialog').remove();">OK</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const okBtn = modal.querySelector('.btn-primary');
        okBtn.addEventListener('click', () => {
            modal.remove();
            resolve(true);
        });
        
        modal.showModal();
    });
}

function showCustomConfirm(title, message) {
    return new Promise((resolve) => {
        const modal = document.createElement('dialog');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-box">
                <h3 class="font-bold text-lg flex items-center gap-2">
                    <i class="fas fa-question-circle text-blue-500"></i>
                    <span>${title}</span>
                </h3>
                <p class="py-4">${message}</p>
                <div class="modal-action">
                    <button type="button" class="btn btn-ghost cancel-btn">Cancel</button>
                    <button type="button" class="btn btn-primary confirm-btn">Confirm</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const cancelBtn = modal.querySelector('.cancel-btn');
        const confirmBtn = modal.querySelector('.confirm-btn');
        
        cancelBtn.addEventListener('click', () => {
            modal.remove();
            resolve(false);
        });
        
        confirmBtn.addEventListener('click', () => {
            modal.remove();
            resolve(true);
        });
        
        modal.showModal();
    });
}

function openDeleteWorkerModal(workerId) {
    document.getElementById('delete-worker-id').value = workerId;
    document.getElementById('delete-worker-modal').showModal();
}

function closeDeleteWorkerModal() {
    document.getElementById('delete-worker-modal').close();
}

function deleteWorker() {
    const workerId = document.getElementById('delete-worker-id').value;
    
    if (!workerId) {
        console.error('No worker ID found');
        showCustomModal('Error', 'No worker ID found', 'error');
        closeDeleteWorkerModal();
        return;
    }
    
    console.log('Deleting worker with ID:', workerId);
    
    fetch(`/api/worker/${workerId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('Delete response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        console.log('Delete result:', result);
        closeDeleteWorkerModal();
        
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            // Reload the page to reflect changes
            showCustomModal('Success', 'Worker deleted successfully!', 'success').then(() => {
                window.location.reload();
            });
        }
    })
    .catch(error => {
        closeDeleteWorkerModal();
        console.error('Delete worker error:', error);
        showCustomModal('Error', 'Error deleting worker: ' + error.message, 'error');
    });
}

function openDeleteAllWorkersModal() {
    document.getElementById('delete-all-workers-modal').showModal();
}

function deleteAllWorkers() {
    const modal = document.getElementById('delete-all-workers-modal');
    
    fetch('/api/worker/delete-all', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (modal) modal.close();
        
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            showCustomModal('Success', result.message || 'All workers deleted successfully!', 'success').then(() => {
                window.location.reload();
            });
        }
    })
    .catch(error => {
        if (modal) modal.close();
        console.error('Delete all workers error:', error);
        showCustomModal('Error', 'Error deleting all workers: ' + error.message, 'error');
    });
}

async function deleteSelectedWorkers() {
    const checkboxes = document.querySelectorAll('.worker-checkbox');
    const selectedIds = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.getAttribute('data-worker-id'));
    
    console.log('Selected worker IDs for deletion:', selectedIds);
    
    if (selectedIds.length === 0) {
        showCustomModal('Selection Required', 'Please select workers to delete', 'warning');
        return;
    }
    
    const confirmed = await showCustomConfirm('Confirm Delete', `Are you sure you want to delete ${selectedIds.length} selected worker(s)?`);
    if (!confirmed) {
        console.log('User cancelled bulk deletion');
        return;
    }
    
    console.log('Proceeding with bulk deletion');
    
    fetch('/api/worker/bulk-delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ worker_ids: selectedIds })
    })
    .then(response => {
        console.log('Bulk delete response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        console.log('Bulk delete result:', result);
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            showCustomModal('Success', result.message || 'Selected workers deleted successfully!', 'success').then(() => {
                window.location.reload();
            });
        }
    })
    .catch(error => {
        console.error('Delete selected workers error:', error);
        showCustomModal('Error', 'Error deleting selected workers: ' + error.message, 'error');
    });
}

// --- Multi-select and Bulk Delete ---
document.addEventListener('DOMContentLoaded', function() {
    const selectAll = document.getElementById('selectAllWorkers');
    const checkboxes = document.querySelectorAll('.worker-checkbox');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');

    function updateDeleteSelectedBtn() {
        const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
        if (deleteSelectedBtn) {
            if (anyChecked) {
                deleteSelectedBtn.classList.remove('hidden');
            } else {
                deleteSelectedBtn.classList.add('hidden');
            }
        }
    }

    if (selectAll) {
        selectAll.addEventListener('change', function() {
            checkboxes.forEach(cb => { cb.checked = selectAll.checked; });
            updateDeleteSelectedBtn();
        });
    }
    
    checkboxes.forEach(cb => {
        cb.addEventListener('change', function() {
            updateDeleteSelectedBtn();
            if (!cb.checked && selectAll && selectAll.checked) {
                selectAll.checked = false;
            }
        });
    });
    
    // Initialize the button state on page load
    updateDeleteSelectedBtn();
});

// --- Edit Worker Modal ---
window.openEditWorkerModal = function(workerId) {
    const modal = document.getElementById('add-worker-modal');
    const form = document.getElementById('workerForm');
    
    console.log('[openEditWorkerModal] Opening modal for worker:', workerId);
    
    // Fetch worker data from the API
    fetch(`/api/worker/${workerId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch worker data');
            }
            return response.json();
        })
        .then(worker => {
            console.log('[openEditWorkerModal] Loaded worker data:', worker);
            
            // Load custom fields first, then populate the form
            reloadCustomFields();
            
            // Wait for custom fields to load, then populate all form fields
            setTimeout(() => {
                // Do NOT reset form - preserve custom field data!
                // Only clear specific fields we're about to populate
                
                // Set standard fields
                const firstNameInput = form.querySelector('input[name="first_name"]');
                if (firstNameInput) {
                    firstNameInput.value = worker.first_name || '';
                }
                
                const lastNameInput = form.querySelector('input[name="last_name"]');
                if (lastNameInput) {
                    lastNameInput.value = worker.last_name || '';
                }
                
                const dobInput = form.querySelector('input[name="date_of_birth"]');
                if (dobInput) {
                    dobInput.value = worker.date_of_birth || '';
                }
                
                // Set custom fields using field ID mapping
                console.log('[openEditWorkerModal] Setting custom field values');
                if (worker.custom_fields) {
                    // Try both field name and field ID approaches
                    const customFieldInputs = form.querySelectorAll('input[name^="custom_field_"]');
                    customFieldInputs.forEach(input => {
                        const fieldId = input.getAttribute('name').replace('custom_field_', '');
                        console.log('[openEditWorkerModal] Processing field:', fieldId);
                        
                        // Find matching custom field value from worker data
                        for (const [fieldName, fieldValue] of Object.entries(worker.custom_fields)) {
                            if (fieldValue) {
                                const labelElement = input.closest('.form-control').querySelector('.label-text');
                                const labelText = labelElement ? labelElement.textContent.trim() : '';
                                
                                if (labelText === fieldName) {
                                    input.value = fieldValue || '';
                                    console.log('[openEditWorkerModal] Set field', fieldName, 'to:', fieldValue);
                                    break;
                                }
                            }
                        }
                    });
                }
                
                console.log('[openEditWorkerModal] Form populated successfully');
            }, 300); // Slightly longer delay for custom fields to fully load
            
            // Change modal title and button text
            const modalTitle = modal.querySelector('h3');
            if (modalTitle) {
                modalTitle.textContent = 'Edit Worker';
            }
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Update Worker';
            }
            
            // Store workerId for update
            form.setAttribute('data-edit-worker-id', workerId);
            
            // Show modal
            modal.showModal();
            
            if (window.feather) {
                feather.replace();
            }
        })
        .catch(error => {
            console.error('Error fetching worker data:', error);
            showCustomModal('Error', 'Failed to load worker data. Please try again.', 'error');
        });
};

// --- Add Worker Modal Custom Field Functions ---
function reloadCustomFields() {
    console.log('Reloading custom fields...');
    
    fetch('/api/import-field')
        .then(res => {
            if (res.status === 401) {
                throw new Error('Authentication required. Please refresh the page and log in again.');
            }
            if (res.status === 400) {
                throw new Error('No workspace selected. Please select a workspace.');
            }
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(fields => {
            console.log('Loaded custom fields:', fields);
            const container = document.getElementById('customFieldsContainer');
            if (!container) {
                console.warn('customFieldsContainer not found');
                return;
            }
            
            // Clear existing custom field items (but keep the static ones from template)
            const existingCustomFields = container.querySelectorAll('.custom-field-item[data-field-id]');
            existingCustomFields.forEach(item => item.remove());
            
            // Add new custom fields
            fields.forEach(field => {
                console.log('Adding custom field:', field);
                const div = document.createElement('div');
                div.className = 'form-control w-full custom-field-item';
                div.setAttribute('data-field-id', field.id);
                
                div.innerHTML = `
                    <label class="label">
                        <div class="flex items-center gap-2 flex-1">
                            <span class="label-text text-black">${field.name}</span>
                        </div>
                        <button type="button" class="btn btn-ghost btn-sm text-red-500 hover:text-red-700 px-2 py-1" onclick="deleteCustomField(${field.id}, '${field.name}')" title="Delete this field">
                            <i data-feather="trash-2" class="h-5 w-5"></i>
                        </button>
                    </label>
                    <input type="text" name="custom_field_${field.id}" class="input input-bordered w-full h-10" placeholder="Enter ${field.name}">
                `;
                container.appendChild(div);
            });
            
            console.log('Custom fields reloaded successfully');
            
            // Refresh feather icons
            if (window.feather) feather.replace();
        })
        .catch(error => {
            console.error('Error reloading custom fields:', error);
        });
}

function addCustomField(sourceModal = null) {
    console.log('[addCustomField] ========== FUNCTION CALLED ==========');
    console.log('[addCustomField] Called from:', sourceModal || 'unknown');
    
    // Determine which input field and checkbox to use based on the modal
    let fieldNameInput;
    let duplicateDetectionCheckbox;
    let modalId;

    if (sourceModal === 'import') {
        modalId = '#import-workers-modal';
        fieldNameInput = document.querySelector('#import-workers-modal #newFieldNameImport');
        duplicateDetectionCheckbox = document.querySelector('#import-workers-modal #enableDuplicateDetectionImport');
        console.log('[addCustomField] Using IMPORT modal input');
    } else if (sourceModal === 'add-worker') {
        modalId = '#add-worker-modal';
        fieldNameInput = document.querySelector('#add-worker-modal #newFieldNameAddWorker');
        duplicateDetectionCheckbox = document.querySelector('#add-worker-modal #enableDuplicateDetectionAddWorker');
        console.log('[addCustomField] Using ADD WORKER modal input');
    } else {
        // Fallback for when sourceModal is not provided
        const importModal = document.getElementById('import-workers-modal');
        if (importModal && importModal.open) {
            modalId = '#import-workers-modal';
            sourceModal = 'import';
            fieldNameInput = document.querySelector('#import-workers-modal #newFieldNameImport');
            duplicateDetectionCheckbox = document.querySelector('#import-workers-modal #enableDuplicateDetectionImport');
            console.log('[addCustomField] Fallback to IMPORT modal');
        } else {
            modalId = '#add-worker-modal';
            sourceModal = 'add-worker';
            fieldNameInput = document.querySelector('#add-worker-modal #newFieldNameAddWorker');
            duplicateDetectionCheckbox = document.querySelector('#add-worker-modal #enableDuplicateDetectionAddWorker');
            console.log('[addCustomField] Fallback to ADD WORKER modal');
        }
    }
    
    console.log('[addCustomField] fieldNameInput element:', fieldNameInput);
    
    const fieldName = fieldNameInput?.value.trim();
    
    console.log('[addCustomField] Field name:', fieldName, 'from modal:', sourceModal);
    
    if (!fieldName) {
        showToast('Please enter a field name', 'warning');
        if (fieldNameInput) fieldNameInput.focus();
        return;
    }
    
    // Check if field name already exists - check both modals if needed
    const existingFieldsAddWorker = Array.from(document.querySelectorAll('#customFieldsContainer .label-text')).map(el => el.textContent.trim());
    const existingFieldsImport = Array.from(document.querySelectorAll('#currentFields [data-field]')).map(el => el.textContent.trim());
    const allExistingFields = [...new Set([...existingFieldsAddWorker, ...existingFieldsImport])];
    
    console.log('[addCustomField] Existing fields:', allExistingFields);
    
    if (allExistingFields.includes(fieldName)) {
        showToast('A field with this name already exists', 'error');
        if (fieldNameInput) {
            fieldNameInput.value = '';
            fieldNameInput.focus();
        }
        return;
    }
    
    // Save current form data before reloading custom fields
    const formData = {};
    const form = document.getElementById('workerForm') || document.getElementById('importWorkersForm');
    if (form) {
        const inputs = form.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            if (input.name && input.value) {
                formData[input.name] = input.value;
            }
        });
        console.log('[addCustomField] Saved form data:', formData);
    }
    
    console.log('[addCustomField] Sending request to create field...');
    
    const enableDuplicateDetection = duplicateDetectionCheckbox ? duplicateDetectionCheckbox.checked : false;
    
    fetch('/api/import-field', {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin',
        body: JSON.stringify({ 
            name: fieldName, 
            type: 'text',
            enable_duplicate_detection: enableDuplicateDetection
        })
    })
    .then(res => {
        console.log('[addCustomField] Response status:', res.status);
        if (res.status === 401) {
            throw new Error('Authentication required. Please refresh the page and log in again.');
        }
        if (res.status === 400) {
            throw new Error('No workspace selected. Please select a workspace.');
        }
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
    })
    .then(result => {
        console.log('[addCustomField] Result:', result);
        if (result.error) {
            showToast(result.error, 'error');
        } else {
            // Clear the input field and checkbox
            if (fieldNameInput) {
                fieldNameInput.value = '';
                fieldNameInput.focus();
            }
            if (duplicateDetectionCheckbox) {
                duplicateDetectionCheckbox.checked = false;
            }
            showToast(`Custom field "${fieldName}" added successfully!`, 'success');
            
            // Reload fields and restore form data
            reloadCustomFields();
            if (sourceModal === 'import' || document.getElementById('import-workers-modal')?.open) {
                loadImportFields();
            }
            
            // Restore form data after a brief delay to allow custom fields to load
            setTimeout(() => {
                if (form && Object.keys(formData).length > 0) {
                    Object.keys(formData).forEach(fieldName => {
                        const input = form.querySelector(`input[name="${fieldName}"]`);
                        if (input) {
                            input.value = formData[fieldName];
                        }
                    });
                    console.log('[addCustomField] Form data restored');
                }
            }, 350);
        }
    })
    .catch(error => {
        console.error('[addCustomField] Error:', error);
        showToast('Failed to add custom field. Please try again.', 'error');
    });
}

// Expose addCustomField immediately to global scope
window.addCustomField = addCustomField;
console.log('[worker.js] addCustomField exposed to window:', typeof window.addCustomField);

function deleteCustomField(fieldId, fieldName) {
    window._pendingDelete = { fieldId, fieldName };
    document.getElementById('deleteFieldMessage').textContent =
        `Are you sure you want to delete the custom field "${fieldName}"?`;
    document.getElementById('deleteFieldModal')?.showModal();
}

function confirmDeleteCustomField() {
    // Close confirmation modal
    document.getElementById('deleteFieldModal')?.close();
    const data = window._pendingDelete;
    if (!data) return;
    
    fetch(`/api/import-field/${data.fieldId}`, { 
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
        .then(res => {
            if (res.status === 401) {
                throw new Error('Authentication required. Please refresh the page and log in again.');
            }
            if (res.status === 404) {
                throw new Error('Field not found or already deleted.');
            }
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(result => {
            if (result.error) {
                showToast(result.error,'error');
            } else {
                showToast(`Custom field "${data.fieldName}" deleted successfully!`,'success');
                // Reload fields in both modals
                reloadCustomFields();
                loadImportFields();
            }
            window._pendingDelete = null;
        })
        .catch(error => {
            console.error('Error deleting custom field:', error);
            showToast('Failed to delete custom field. Please try again.', 'error');
            window._pendingDelete = null;
        });
}

// Add and close worker modal functions (imported from script.js behavior)
function openAddWorkerModal() {
    const modal = document.getElementById('add-worker-modal');
    if (!modal) {
        console.error('[openAddWorkerModal] Modal element not found');
        if (typeof showToast === 'function') showToast('Internal error: cannot open Add Worker modal', 'error');
        return;
    }
    const form = document.getElementById('workerForm');
    
    // Reset form and ensure it's in "add" mode
    if (form) {
        form.reset();
        form.removeAttribute('data-edit-worker-id');
        
        // Reset modal title
        const modalTitle = modal.querySelector('h3');
        if (modalTitle) {
            modalTitle.textContent = 'Add New Worker';
        }
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.textContent = 'Add Worker';
    }
    
    // Load current custom fields to ensure they're displayed
    reloadCustomFields();
    
    modal.showModal();
    
    // Replace feather icons
    if (window.feather) {
        feather.replace();
    }
    
    // Ensure Add Custom Field button is set up after modal is shown
    setTimeout(() => {
        console.log('[openAddWorkerModal] Setting up Add Custom Field button and input listeners');
        
        const addFieldBtn = document.querySelector('#add-worker-modal #addCustomFieldBtn');
        const newFieldInput = document.querySelector('#add-worker-modal #newFieldNameAddWorker');

        if (addFieldBtn && newFieldInput) {
            console.log('[openAddWorkerModal] Found button and input, setting up listeners');
            
            addFieldBtn.onclick = function(e) {
                console.log('[Add Field Button Click] Button clicked');
                e.preventDefault();
                e.stopPropagation();
                addCustomField('add-worker');
            };

            newFieldInput.onkeypress = function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    console.log('[newFieldName] Enter key pressed, triggering addCustomField');
                    addCustomField('add-worker');
                }
            };
        } else {
            console.warn('[openAddWorkerModal] Add Custom Field button or input not found');
        }
    }, 100);
}

function closeAddWorkerModal() {
    const modal = document.getElementById('add-worker-modal');
    if (!modal) return;
    
    const form = document.getElementById('workerForm');
    
    // Reset form
    if (form) {
        form.reset();
        form.removeAttribute('data-edit-worker-id');
        
        // Reset modal title
        const modalTitle = modal.querySelector('h3');
        if (modalTitle) {
            modalTitle.textContent = 'Add New Worker';
        }
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.textContent = 'Add Worker';
    }
    
    modal.close();
    
    // Reload the page to reflect any changes
    window.location.reload();
}

// Import Workers Modal functions
function openImportWorkersModal() {
    const modal = document.getElementById('import-workers-modal');
    if (!modal) {
        console.error('[openImportWorkersModal] Modal element not found');
        return;
    }
    modal.showModal();
    loadImportFields();
    
    // Replace feather icons if available
    if (window.feather) {
        feather.replace();
    }
    
    // Setup event listeners after modal is shown
    setTimeout(() => {
        console.log('[openImportWorkersModal] Setting up Import Custom Field button and input listeners');
        
        const addFieldBtn = document.querySelector('#import-workers-modal #addCustomFieldBtnImport');
        const newFieldInput = document.querySelector('#import-workers-modal #newFieldNameImport');

        if (addFieldBtn && newFieldInput) {
            console.log('[openImportWorkersModal] Found button and input, setting up listeners');
            
            addFieldBtn.onclick = function(e) {
                console.log('[Import Add Field Button Click] Button clicked');
                e.preventDefault();
                e.stopPropagation();
                addCustomField('import');
            };

            newFieldInput.onkeypress = function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    console.log('[Import newFieldName] Enter key pressed, triggering addCustomField');
                    addCustomField('import');
                }
            };
        } else {
            console.warn('[openImportWorkersModal] Import Add Custom Field button or input not found');
        }
    }, 100);
}

function closeImportWorkersModal() {
    const modal = document.getElementById('import-workers-modal');
    if (modal) {
        modal.close();
        
        // Reload the page to reflect any changes
        window.location.reload();
    }
}

function loadImportFields() {
    console.log('Loading import fields...');
    // Load existing import fields
    fetch('/api/import-field', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        console.log('Load fields response status:', response.status);
        if (response.status === 401 || response.status === 403) {
            console.warn('User not authenticated, skipping import fields load');
            showToast('Authentication required. Please refresh the page and log in again.', 'error');
            throw new Error('Authentication required. Please log in again.');
        }
        if (response.status === 400) {
            console.warn('No workspace selected, skipping import fields load');
            showToast('No workspace selected. Please select a workspace.', 'error');
            throw new Error('No workspace selected');
        }
        if (!response.ok) {
            console.error(`Failed to load import fields: HTTP ${response.status}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(fields => {
        console.log('Loaded fields:', fields);
        const currentFields = document.getElementById('currentFields');
        
        if (!currentFields) {
            console.warn('currentFields container not found');
            return;
        }
        
        // Clear all fields first
        currentFields.innerHTML = '';
        
        // Add default fields back
        const firstNameDiv = document.createElement('div');
        firstNameDiv.className = 'bg-blue-100 p-2 rounded-lg text-blue-700 font-medium truncate';
        firstNameDiv.setAttribute('data-field', 'first_name');
        firstNameDiv.textContent = 'First Name';
        currentFields.appendChild(firstNameDiv);
        
        const lastNameDiv = document.createElement('div');
        lastNameDiv.className = 'bg-blue-100 p-2 rounded-lg text-blue-700 font-medium truncate';
        lastNameDiv.setAttribute('data-field', 'last_name');
        lastNameDiv.textContent = 'Last Name';
        currentFields.appendChild(lastNameDiv);
        
        const dobDiv = document.createElement('div');
        dobDiv.className = 'bg-blue-100 p-2 rounded-lg text-blue-700 font-medium truncate';
        dobDiv.setAttribute('data-field', 'date_of_birth');
        dobDiv.textContent = 'Date of Birth';
        currentFields.appendChild(dobDiv);
        
        // Add custom fields
        fields.forEach(field => {
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'bg-blue-100 p-2 rounded-lg text-blue-700 font-medium truncate flex justify-between items-center';
            fieldDiv.setAttribute('data-field', field.name.replace(/ /g, '_'));
            
            const fieldNameSpan = document.createElement('span');
            fieldNameSpan.textContent = field.name;
            
            // Add duplicate detection badge if enabled
            if (field.enable_duplicate_detection) {
                const badge = document.createElement('span');
                badge.className = 'badge badge-warning badge-xs ml-1';
                badge.textContent = 'Dup';
                badge.title = 'Duplicate detection enabled';
                fieldNameSpan.appendChild(badge);
            }
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-ghost btn-sm text-red-500 hover:text-red-700 ml-2 px-2 py-1';
            deleteBtn.title = 'Delete this field';
            deleteBtn.onclick = function() {
                deleteCustomField(field.id, field.name);
            };
            deleteBtn.innerHTML = '<i class="material-icons text-sm">delete</i>';
            
            fieldDiv.appendChild(fieldNameSpan);
            fieldDiv.appendChild(deleteBtn);
            currentFields.appendChild(fieldDiv);
        });
    })
    .catch(error => {
        console.error('Error loading import fields:', error);
    });
}

// Expose to global scope
window.reloadCustomFields = reloadCustomFields;
window.addCustomField = addCustomField;
window.deleteCustomField = deleteCustomField;
window.confirmDeleteCustomField = confirmDeleteCustomField;
window.openAddWorkerModal = openAddWorkerModal;
window.closeAddWorkerModal = closeAddWorkerModal;
window.openDeleteWorkerModal = openDeleteWorkerModal;
window.closeDeleteWorkerModal = closeDeleteWorkerModal;
window.deleteWorker = deleteWorker;
window.deleteSelectedWorkers = deleteSelectedWorkers;
window.deleteAllWorkers = deleteAllWorkers;
window.openDeleteAllWorkersModal = openDeleteAllWorkersModal;
window.openImportWorkersModal = openImportWorkersModal;
window.closeImportWorkersModal = closeImportWorkersModal;
window.loadImportFields = loadImportFields;

console.log('[worker.js] Script fully loaded.');
console.log('[worker.js] window.addCustomField type:', typeof window.addCustomField);
console.log('[worker.js] window.addCustomField is:', window.addCustomField);