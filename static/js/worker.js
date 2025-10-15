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
    
    fetch(`/api/worker/${workerId}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            // Remove the deleted worker's row from the table
            const checkbox = document.querySelector(`.worker-checkbox[data-worker-id="${workerId}"]`);
            if (checkbox) {
                const row = checkbox.closest('tr');
                if (row) row.remove();
            }
            showCustomModal('Success', 'Worker deleted successfully!', 'success');
        }
    })
    .catch(error => {
        showCustomModal('Error', 'Error deleting worker: ' + error.message, 'error');
    })
    .finally(() => {
        closeDeleteWorkerModal();
    });
}

function openDeleteAllWorkersModal() {
    document.getElementById('delete-all-workers-modal').showModal();
}

function deleteAllWorkers() {
    fetch('/api/worker/delete-all', {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            window.location.reload();
        }
    })
    .catch(error => {
        showCustomModal('Error', 'Error deleting all workers: ' + error.message, 'error');
    })
    .finally(() => {
        document.getElementById('delete-all-workers-modal').close();
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
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            window.location.reload();
        }
    })
    .catch(error => {
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
            
            const confirmed = await showCustomConfirm('Confirm Delete', 'Are you sure you want to delete the selected workers?');
            if (!confirmed) return;
            
            fetch('/api/worker/bulk-delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ worker_ids: selectedIds })
            })
            .then(res => res.json())
            .then(result => {
                if (result.error) {
                    showCustomModal('Error', result.error, 'error');
                } else {
                    window.location.reload();
                }
            })
            .catch(error => {
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

// Expose to global scope
window.reloadCustomFields = reloadCustomFields;
window.addCustomField = addCustomField;
window.deleteCustomField = deleteCustomField;
window.confirmDeleteCustomField = confirmDeleteCustomField;