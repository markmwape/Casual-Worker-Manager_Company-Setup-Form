function toggleEditWorkersMode() {
    const deleteColumns = document.querySelectorAll('[id^="deleteColumn-"]');
    const deleteColumnHeader = document.getElementById('deleteColumnHeader');
    const editToggleButton = document.getElementById('editWorkersToggle');
    const deleteAllBtn = document.getElementById('deleteAllBtn');

    deleteColumns.forEach(column => {
        column.classList.toggle('hidden');
    });

    deleteColumnHeader.classList.toggle('hidden');
    deleteAllBtn.classList.toggle('hidden');
    editToggleButton.classList.toggle('btn-outline');
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
            alert(result.error);
        } else {
            window.location.reload();
        }
    })
    .catch(error => {
        alert('Error deleting worker: ' + error.message);
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
            alert(result.error);
        } else {
            window.location.reload();
        }
    })
    .catch(error => {
        alert('Error deleting all workers: ' + error.message);
    })
    .finally(() => {
        document.getElementById('delete-all-workers-modal').close();
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
        deleteSelectedBtn.addEventListener('click', function() {
            const selectedIds = Array.from(checkboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.getAttribute('data-worker-id'));
            if (selectedIds.length === 0) return;
            if (!confirm('Are you sure you want to delete the selected workers?')) return;
            fetch('/api/worker/bulk-delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ worker_ids: selectedIds })
            })
            .then(res => res.json())
            .then(result => {
                if (result.error) {
                    alert(result.error);
                } else {
                    window.location.reload();
                }
            })
            .catch(error => {
                alert('Error deleting selected workers: ' + error.message);
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
            input.value = cells[cellIdx].innerText.trim() === 'N/A' ? '' : cells[cellIdx].innerText.trim();
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