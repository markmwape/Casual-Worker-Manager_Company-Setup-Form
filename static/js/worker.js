// Import showToast from global scope if available, or provide fallback
const showToast = window.showToast || function(message, type = 'success') {
    console.log(`[Toast ${type}]:`, message);
    
    // Create a simple toast notification if no toast system is available
    const toast = document.createElement('div');
    const bgColor = type === 'error' ? 'bg-red-500' : type === 'warning' ? 'bg-yellow-500' : 'bg-green-500';
    toast.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
};

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
    
    // Setup Add Custom Field button with proper event handling
    console.log('[DOMContentLoaded] Setting up Add Custom Field button');
    setupAddCustomFieldButton();
    
    // Add Enter key support for custom field input
    const newFieldInput = document.getElementById('newFieldName');
    if (newFieldInput) {
        console.log('[DOMContentLoaded] Adding Enter key listener to newFieldName input');
        newFieldInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                console.log('[newFieldName] Enter key pressed, triggering addCustomField');
                addCustomField();
            }
        });
    }
});

// Function to setup Add Custom Field button
function setupAddCustomFieldButton() {
    const addFieldBtn = document.getElementById('addCustomFieldBtn');
    if (addFieldBtn) {
        console.log('[setupAddCustomFieldButton] Found Add Custom Field button');
        
        // Remove any existing click handlers by cloning the button
        const newBtn = addFieldBtn.cloneNode(true);
        addFieldBtn.parentNode.replaceChild(newBtn, addFieldBtn);
        
        // Add fresh click handler
        newBtn.addEventListener('click', function(e) {
            console.log('[Add Field Button] Button clicked');
            e.preventDefault();
            e.stopPropagation();
            addCustomField();
        });
        
        console.log('[setupAddCustomFieldButton] Event listener attached');
    } else {
        console.warn('[setupAddCustomFieldButton] Add Custom Field button not found yet');
    }
}

// --- Edit Worker Modal ---
window.openEditWorkerModal = function(workerId) {
    const modal = document.getElementById('add-worker-modal');
    const form = document.getElementById('workerForm');
    
    // Fetch worker data from the API
    fetch(`/api/worker/${workerId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch worker data');
            }
            return response.json();
        })
        .then(worker => {
            // Load custom fields first, then populate the form
            reloadCustomFields();
            
            // Wait a brief moment for custom fields to load, then populate the form
            setTimeout(() => {
                // Reset form first
                form.reset();
                
                // Set standard fields
                if (form.querySelector('input[name="first_name"]')) {
                    form.querySelector('input[name="first_name"]').value = worker.first_name || '';
                }
                if (form.querySelector('input[name="last_name"]')) {
                    form.querySelector('input[name="last_name"]').value = worker.last_name || '';
                }
                if (form.querySelector('input[name="date_of_birth"]')) {
                    form.querySelector('input[name="date_of_birth"]').value = worker.date_of_birth || '';
                }
                
                // Set custom fields
                if (worker.custom_fields) {
                    Object.keys(worker.custom_fields).forEach(fieldName => {
                        const input = form.querySelector(`input[name="${fieldName}"]`);
                        if (input) {
                            input.value = worker.custom_fields[fieldName] || '';
                        }
                    });
                }
            }, 200); // Small delay to allow custom fields to load
            
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
                        <span class="label-text text-black">${field.name}</span>
                        <button type="button" class="btn btn-ghost btn-xs text-red-500 hover:text-red-700" onclick="deleteCustomField(${field.id}, '${field.name}')" title="Delete this field">
                            <i data-feather="trash-2" class="h-4 w-4"></i>
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

function addCustomField() {
    const fieldNameInput = document.getElementById('newFieldName');
    const fieldName = fieldNameInput?.value.trim();
    
    console.log('[addCustomField] Field name:', fieldName);
    
    if (!fieldName) {
        showToast('Please enter a field name', 'warning');
        if (fieldNameInput) fieldNameInput.focus();
        return;
    }
    
    // Check if field name already exists
    const existingFields = Array.from(document.querySelectorAll('#customFieldsContainer .label-text')).map(el => el.textContent.trim());
    console.log('[addCustomField] Existing fields:', existingFields);
    
    if (existingFields.includes(fieldName)) {
        showToast('A field with this name already exists', 'error');
        if (fieldNameInput) {
            fieldNameInput.value = '';
            fieldNameInput.focus();
        }
        return;
    }
    
    console.log('[addCustomField] Sending request to create field...');
    
    fetch('/api/import-field', {
        method: 'POST', 
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name: fieldName, type: 'text' })
    })
    .then(res => {
        console.log('[addCustomField] Response status:', res.status);
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
            // Clear the input field
            if (fieldNameInput) {
                fieldNameInput.value = '';
                fieldNameInput.focus();
            }
            showToast(`Custom field "${fieldName}" added successfully!`, 'success');
            reloadCustomFields();
        }
    })
    .catch(error => {
        console.error('[addCustomField] Error:', error);
        showToast('Failed to add custom field. Please try again.', 'error');
    });
}

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
    
    fetch(`/api/import-field/${data.fieldId}`, { method:'DELETE' })
        .then(res => res.json())
        .then(result => {
            if (result.error) {
                showToast(result.error,'error');
            } else {
                showToast(`Custom field "${data.fieldName}" deleted successfully!`,'success');
                reloadCustomFields();
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
        
        // Setup the Add Field button
        const addFieldBtn = document.getElementById('addCustomFieldBtn');
        if (addFieldBtn) {
            console.log('[openAddWorkerModal] Found Add Custom Field button, setting up event listener');
            
            // Remove any existing click handlers by cloning the button
            const newBtn = addFieldBtn.cloneNode(true);
            addFieldBtn.parentNode.replaceChild(newBtn, addFieldBtn);
            
            // Add fresh click handler
            newBtn.addEventListener('click', function(e) {
                console.log('[Add Field Button Click] Button clicked');
                e.preventDefault();
                e.stopPropagation();
                addCustomField();
            });
        } else {
            console.warn('[openAddWorkerModal] Add Custom Field button not found');
        }
        
        // Setup Enter key listener
        const newFieldInput = document.getElementById('newFieldName');
        if (newFieldInput) {
            console.log('[openAddWorkerModal] Found input field, setting up Enter key listener');
            
            // Clone the input to remove old listeners
            const newInput = newFieldInput.cloneNode(true);
            newFieldInput.parentNode.replaceChild(newInput, newFieldInput);
            
            newInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    console.log('[newFieldName] Enter key pressed, triggering addCustomField');
                    addCustomField();
                }
            });
        } else {
            console.warn('[openAddWorkerModal] Input field not found');
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
}

function closeImportWorkersModal() {
    const modal = document.getElementById('import-workers-modal');
    if (modal) {
        modal.close();
    }
}

function loadImportFields() {
    console.log('Loading import fields...');
    // Load existing import fields
    fetch('/api/import-field')
    .then(response => {
        console.log('Load fields response status:', response.status);
        if (response.status === 401 || response.status === 403) {
            console.warn('User not authenticated, skipping import fields load');
            throw new Error('Authentication required. Please log in again.');
        }
        if (response.status === 400) {
            console.warn('No workspace selected, skipping import fields load');
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
            fieldDiv.className = 'bg-blue-100 p-2 rounded-lg text-blue-700 font-medium truncate';
            fieldDiv.setAttribute('data-field', field.name.replace(/ /g, '_'));
            fieldDiv.textContent = field.name;
            currentFields.appendChild(fieldDiv);
        });
    })
    .catch(error => {
        console.error('Error loading import fields:', error);
    });
}

// Expose to global scope
window.setupAddCustomFieldButton = setupAddCustomFieldButton;
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