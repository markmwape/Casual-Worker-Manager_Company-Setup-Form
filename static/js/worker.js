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
            window.location.reload();
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