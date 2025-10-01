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
    // Find the worker row and extract data
    const row = document.querySelector(`.worker-checkbox[data-worker-id="${workerId}"]`).closest('tr');
    const cells = row.querySelectorAll('td');
    // Assuming order: [checkbox, ...fields, created_at, actions]
    // We'll use the add_worker modal as the edit modal for simplicity
    const modal = document.getElementById('add-worker-modal');
    const form = document.getElementById('workerForm');
    // Set form values
    const inputs = form.querySelectorAll('input[name]');
    let cellIdx = 1; // skip checkbox
    inputs.forEach(input => {
        if (cells[cellIdx]) {
            let cellValue = cells[cellIdx].innerText.trim();
            if (cellValue === 'N/A') {
                input.value = '';
            } else {
                // Handle date fields specifically
                if (input.type === 'date' && cellValue) {
                    // The date might be in YYYY-MM-DD format already, but let's make sure
                    try {
                        // If the date is already in the correct format, use it directly
                        const date = new Date(cellValue);
                        if (!isNaN(date.getTime())) {
                            input.value = cellValue;
                        } else {
                            input.value = '';
                        }
                    } catch (e) {
                        input.value = '';
                    }
                } else {
                    input.value = cellValue;
                }
            }
            cellIdx++;
        }
    });
    // Change submit button text
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.textContent = 'Update Worker';
    // Store workerId for update
    form.setAttribute('data-edit-worker-id', workerId);
    // Show modal
    modal.showModal();
};

// Open/close Add Worker Modal
function openAddWorkerModal() {
    const modal = document.getElementById('add-worker-modal');
    if (modal) modal.showModal();
}

function closeAddWorkerModal() {
    const modal = document.getElementById('add-worker-modal');
    if (modal) modal.close();
}

// Open/close Import Workers Modal
function openImportWorkersModal() {
    const modal = document.getElementById('import-workers-modal');
    if (modal) modal.showModal();
}

function closeImportWorkersModal() {
    const modal = document.getElementById('import-workers-modal');
    if (modal) modal.close();
}