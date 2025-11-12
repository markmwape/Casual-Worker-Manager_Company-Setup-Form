// Import showToast from global scope if available, or provide fallback
const showToast = window.showToast || function(message, type = 'success') {
    console.log(`[Toast ${type}]:`, message);
    alert(message);
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
        showCustomModal('Error', 'No worker selected', 'error');
        closeDeleteWorkerModal();
        return;
    }
    
    fetch(`/api/worker/${workerId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            // Handle non-200 responses
            return response.json().then(data => {
                throw new Error(data.error || `HTTP error ${response.status}`);
            }).catch(err => {
                throw new Error(`HTTP error ${response.status}`);
            });
        }
        return response.json();
    })
    .then(result => {
        closeDeleteWorkerModal();
        
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            showCustomModal('Success', 'Worker deleted successfully!', 'success').then(() => {
                // Reload page to refresh the worker list
                window.location.reload();
            });
        }
    })
    .catch(error => {
        closeDeleteWorkerModal();
        console.error('Delete error:', error);
        showCustomModal('Error', 'Error deleting worker: ' + error.message, 'error');
    });
}

function openDeleteAllWorkersModal() {
    document.getElementById('delete-all-workers-modal').showModal();
}

function deleteAllWorkers() {
    fetch('/api/worker/delete-all', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            // Handle non-200 responses
            return response.json().then(data => {
                throw new Error(data.error || data.message || `HTTP error ${response.status}`);
            }).catch(err => {
                if (err.message) throw err;
                throw new Error(`HTTP error ${response.status}`);
            });
        }
        return response.json();
    })
    .then(result => {
        document.getElementById('delete-all-workers-modal').close();
        
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            showCustomModal('Success', result.message || 'All workers deleted successfully', 'success').then(() => {
                window.location.reload();
            });
        }
    })
    .catch(error => {
        document.getElementById('delete-all-workers-modal').close();
        console.error('Delete all error:', error);
        showCustomModal('Error', 'Error deleting all workers: ' + error.message, 'error');
    });
}

async function deleteSelectedWorkers() {
    const checkboxes = document.querySelectorAll('.worker-checkbox');
    const selectedIds = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.getAttribute('data-worker-id'));
    
    if (selectedIds.length === 0) {
        showCustomModal('Selection Required', 'Please select workers to delete', 'warning');
        return;
    }
    
    const confirmed = await showCustomConfirm('Confirm Delete', `Are you sure you want to delete ${selectedIds.length} selected worker(s)?`);
    if (!confirmed) {
        return;
    }
    
    fetch('/api/worker/bulk-delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ worker_ids: selectedIds })
    })
    .then(response => {
        if (!response.ok) {
            // Handle non-200 responses
            return response.json().then(data => {
                throw new Error(data.error || data.message || `HTTP error ${response.status}`);
            }).catch(err => {
                if (err.message) throw err;
                throw new Error(`HTTP error ${response.status}`);
            });
        }
        return response.json();
    })
    .then(result => {
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            showCustomModal('Success', result.message || `${selectedIds.length} workers deleted successfully`, 'success').then(() => {
                window.location.reload();
            });
        }
    })
    .catch(error => {
        console.error('Bulk delete error:', error);
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
        if (anyChecked) {
            deleteSelectedBtn.classList.remove('hidden');
        } else {
            deleteSelectedBtn.classList.add('hidden');
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
            if (!cb.checked && selectAll.checked) {
                selectAll.checked = false;
            }
        });
    });

    if (deleteSelectedBtn) {
        deleteSelectedBtn.addEventListener('click', async function() {
            const selectedIds = Array.from(checkboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.getAttribute('data-worker-id'));
            if (selectedIds.length === 0) return;
            
            const confirmed = await showCustomConfirm('Confirm Delete', `Are you sure you want to delete ${selectedIds.length} selected worker(s)?`);
            if (!confirmed) return;
            
            fetch('/api/worker/bulk-delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ worker_ids: selectedIds })
            })
            .then(response => {
                if (!response.ok) {
                    // Handle non-200 responses
                    return response.json().then(data => {
                        throw new Error(data.error || data.message || `HTTP error ${response.status}`);
                    }).catch(err => {
                        if (err.message) throw err;
                        throw new Error(`HTTP error ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(result => {
                if (result.error) {
                    showCustomModal('Error', result.error, 'error');
                } else {
                    showCustomModal('Success', result.message || `${selectedIds.length} workers deleted successfully`, 'success').then(() => {
                        window.location.reload();
                    });
                }
            })
            .catch(error => {
                console.error('Bulk delete error:', error);
                showCustomModal('Error', 'Error deleting selected workers: ' + error.message, 'error');
            });
        });
    }
});

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
    fetch('/api/import-field')
        .then(res => res.json())
        .then(fields => {
            const container = document.getElementById('customFieldsContainer');
            if (!container) return;
            container.innerHTML = '';
            fields.forEach(field => {
                const div = document.createElement('div');
                div.className = 'form-control w-full custom-field-item';
                div.innerHTML = `
                    <label class="label">
                        <span class="label-text text-black">${field.name}</span>
                        <button type="button" class="btn btn-ghost btn-xs text-red-500 hover:text-red-700" onclick="deleteCustomField(${field.id}, '${field.name}')">
                            <i data-feather="trash-2" class="h-4 w-4"></i>
                        </button>
                    </label>
                    <input type="text" name="custom_field_${field.id}" class="input input-bordered w-full h-10" placeholder="Enter ${field.name}">
                `;
                container.appendChild(div);
            });
            if (window.feather) feather.replace();
        });
}

function addCustomField() {
    const fieldName = document.getElementById('newFieldName')?.value.trim();
    if (!fieldName) {
        showToast('Please enter a field name', 'warning');
        return;
    }
    fetch('/api/import-field', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name: fieldName, type: 'text' })
    })
    .then(res => res.json())
    .then(result => {
        if (result.error) {
            showToast(result.error, 'error');
        } else {
            document.getElementById('newFieldName').value = '';
            showToast(`Custom field "${fieldName}" added successfully!`, 'success');
            reloadCustomFields();
        }
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
                showToast(`Custom field "${data.fieldName}" deleted!`,'success');
                reloadCustomFields();
            }
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
    
    modal.showModal();
    
    // Replace feather icons
    if (window.feather) {
        feather.replace();
    }
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
window.reloadCustomFields = reloadCustomFields;
window.addCustomField = addCustomField;
window.deleteCustomField = deleteCustomField;
window.confirmDeleteCustomField = confirmDeleteCustomField;
window.openAddWorkerModal = openAddWorkerModal;
window.closeAddWorkerModal = closeAddWorkerModal;
window.openDeleteWorkerModal = openDeleteWorkerModal;
window.closeDeleteWorkerModal = closeDeleteWorkerModal;
window.deleteWorker = deleteWorker;
window.openImportWorkersModal = openImportWorkersModal;
window.closeImportWorkersModal = closeImportWorkersModal;
window.loadImportFields = loadImportFields;