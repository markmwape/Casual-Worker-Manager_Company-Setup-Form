// UX Improvements - Custom Modal System
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

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;
    
    if (type === 'success') {
        toast.classList.add('bg-green-500', 'text-white');
    } else if (type === 'error') {
        toast.classList.add('bg-red-500', 'text-white');
    } else {
        toast.classList.add('bg-blue-500', 'text-white');
    }
    
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'} mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

function showLoading(element) {
    element.disabled = true;
    element.innerHTML = '<div class="loading-spinner mr-2"></div>Loading...';
}

function hideLoading(element, originalText) {
    element.disabled = false;
    element.innerHTML = originalText;
}

// Modal functions
function openLogoutModal() {
    document.getElementById('logout-modal').classList.add('modal-open');
}

// Add team member form submission
document.addEventListener('DOMContentLoaded', function() {
    const addTeamMemberForm = document.getElementById('addTeamMemberForm');
    if (addTeamMemberForm) {
        addTeamMemberForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                email: formData.get('email'),
                role: formData.get('role')
            };
            
            fetch('/api/team-member', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.error) {
                    showToast(result.error, 'error');
                } else {
                    // Add new row to table with improved styling
                    const tbody = document.getElementById('teamMembersTableBody');
                    const tr = document.createElement('tr');
                    tr.className = 'hover:bg-gray-50 transition-colors duration-150';
                    tr.setAttribute('data-user-id', result.user.id);
                    
                    // Check if current user is a Supervisor to conditionally show Actions column
                    const isSupervisor = window.currentUserRole === 'Supervisor';
                    
                    tr.innerHTML = `
                        <td class="py-4">
                            <div class="flex items-center">
                                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                                    <span class="text-blue-600 font-semibold text-sm">${result.user.email[0].toUpperCase()}</span>
                                </div>
                                <span class="font-medium text-gray-800">${result.user.email}</span>
                            </div>
                        </td>
                        <td class="py-4">
                            <span class="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                                ${result.user.role}
                            </span>
                        </td>
                        ${!isSupervisor ? `
                        <td class="py-4">
                            <div class="flex gap-2 justify-center">
                                <button onclick="openEditRoleModal('${result.user.id}', '${result.user.email}', '${result.user.role}')" class="btn btn-ghost btn-sm hover:bg-blue-100 text-blue-600 border border-blue-200 p-2 rounded-md transition-all duration-200 hover:shadow-sm flex items-center justify-center" title="Edit">
                                    <i data-feather="edit" class="w-4 h-4"></i>
                                </button>
                                <button onclick="openRemoveTeamMemberModal('${result.user.id}', '${result.user.email}')" class="btn btn-ghost btn-sm hover:bg-red-100 text-red-600 border border-red-200 p-2 rounded-md transition-all duration-200 hover:shadow-sm flex items-center justify-center" title="Delete">
                                    <i data-feather="trash-2" class="w-4 h-4"></i>
                                </button>
                            </div>
                        </td>
                        ` : ''}
                    `;
                    tbody.appendChild(tr);
                    
                    // Close modal and reset form
                    document.getElementById('add-team-member-modal').close();
                    e.target.reset();
                    
                                        // Show success message
                    showToast('Team member added successfully!', 'success');
                    
                    // Refresh Feather icons
                    reinitializeFeatherIcons();
                }
            })
            .catch(error => {
                console.error('Error adding team member:', error);
                showToast('Failed to add team member', 'error');
            });
        });
    }
});

function openImportWorkersModal() {
    document.getElementById('import-workers-modal').showModal();
    loadImportFields();
}

function loadImportFields() {
    console.log('Loading import fields...');
    // Load existing import fields
    fetch('/api/import-field')
    .then(response => {
        console.log('Load fields response status:', response.status);
        if (response.status === 401 || response.status === 403) {
            throw new Error('Authentication required. Please log in again.');
        }
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(fields => {
        console.log('Loaded fields:', fields);
        const currentFields = document.getElementById('currentFields');
        
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
            fieldDiv.className = 'bg-blue-100 p-2 rounded-lg text-blue-700 font-medium flex justify-between items-center';
            fieldDiv.setAttribute('data-field', field.id);
            fieldDiv.innerHTML = `
                <span class="truncate">${field.name}</span>
                <button type="button" class="btn btn-ghost btn-sm" onclick="removeCustomField(${field.id})">
                    <i class="material-icons text-error">delete</i>
                </button>
            `;
            currentFields.appendChild(fieldDiv);
        });
    })
    .catch(error => {
        console.error('Error loading import fields:', error);
        if (error.message.includes('Authentication required')) {
            showCustomModal('Session Expired', 'Please log in again to use this feature.', 'error');
            window.location.href = '/';
        } else {
            console.error('Failed to load import fields:', error.message);
        }
    });
}

function closeImportWorkersModal() {
    document.getElementById('import-workers-modal').close();
    window.location.reload();
}

function closeLogoutModal() {
    document.getElementById('logout-modal').classList.remove('modal-open');
}

function openAddWorkerModal() {
    const modal = document.getElementById('add-worker-modal');
    const form = document.getElementById('workerForm');
    
    // Reset form and ensure it's in "add" mode
    if (form) {
        form.reset();
        form.removeAttribute('data-edit-worker-id');
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.textContent = 'Add Worker';
    }
    
    modal.showModal();
}

function closeAddWorkerModal() {
    document.getElementById('add-worker-modal').close();
}

// Handle worker form submission
document.addEventListener('DOMContentLoaded', function() {
    const workerForm = document.getElementById('workerForm');
    if (workerForm) {
        console.log('Worker form found, adding submit handler');
        workerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Worker form submitted');
            
            const formData = new FormData(e.target);
            const data = {};
            
            // Convert form data to JSON
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            console.log('Sending worker data:', data);
            
            const editWorkerId = workerForm.getAttribute('data-edit-worker-id');
            let url, method;
            if (editWorkerId) {
                url = `/api/worker/${editWorkerId}`;
                method = 'PUT';
            } else {
                url = '/api/worker';
                method = 'POST';
            }
            
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(result => {
                console.log('Response result:', result);
                if (result.error) {
                    showToast(result.error, 'error');
                } else {
                    closeAddWorkerModal();
                    showToast(editWorkerId ? 'Worker updated successfully!' : 'Worker added successfully!', 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }
            })
            .catch(error => {
                console.error('Error saving worker:', error);
                showToast('Failed to save worker', 'error');
            })
            .finally(() => {
                workerForm.removeAttribute('data-edit-worker-id');
                const submitBtn = workerForm.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.textContent = 'Add Worker';
            });
        });
    } else {
        console.log('Worker form not found');
    }
    
    // Handle import workers form submission
    const importWorkersForm = document.getElementById('importWorkersForm');
    if (importWorkersForm) {
        console.log('Import workers form found, adding submit handler');
        importWorkersForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Import workers form submitted');
            
            const formData = new FormData(e.target);
            
            fetch('/api/worker/import', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                if (result.error) {
                    showToast(result.error, 'error');
                } else {
                    // Show column mapping section
                    document.getElementById('importForm').classList.add('hidden');
                    document.getElementById('columnMapping').classList.remove('hidden');
                    
                    // Store file ID for later use
                    document.getElementById('columnMapping').dataset.fileId = result.file_id;
                    
                    // Load Excel columns for mapping
                    loadExcelColumns(result.columns);
                }
            })
            .catch(error => {
                console.error('Error uploading file:', error);
                showToast('Failed to upload file', 'error');
            });
        });
    } else {
        console.log('Import workers form not found');
    }
});

function loadExcelColumns(columns) {
    const mappingTableBody = document.getElementById('mappingTableBody');
    mappingTableBody.innerHTML = '';
    
    // Get current fields (both default and custom)
    const currentFields = document.getElementById('currentFields');
    const fields = Array.from(currentFields.children).map(field => {
        const span = field.querySelector('span');
        return {
            name: span ? span.textContent : field.textContent.trim(),
            id: field.getAttribute('data-field')
        };
    });
    
    // Create mapping rows
    fields.forEach(field => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${field.name}</td>
            <td>
                <select class="select select-bordered w-full" data-field="${field.id}">
                    <option value="">Select Column</option>
                    ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
                </select>
            </td>
        `;
        mappingTableBody.appendChild(tr);
    });
}

function openAddTaskModal() {
    const modal = document.getElementById('add-task-modal');
    if (modal) {
        modal.classList.add('modal-open');
        
        // Set default date to today
        const dateInput = document.getElementById('task-start-date');
        if (dateInput && !dateInput.value) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.value = today;
        }
        
        // Update status indicator
        updateTaskStatusIndicator();
        
        // Set up payment type change handlers
        setupPaymentTypeHandlers();
        
        // Initialize with default payment type (per_day)
        updatePayoutLabels('per_day');
        
        // Debug the form when modal is opened
        const taskForm = document.getElementById('taskForm');
        if (taskForm) {
            console.log('Task form found when modal opened:', taskForm);
            console.log('Form onsubmit:', taskForm.onsubmit);
        } else {
            console.log('Task form not found when modal opened');
        }
    }
}

function setupPaymentTypeHandlers() {
    const paymentTypeInputs = document.querySelectorAll('input[name="payment_type"]');
    paymentTypeInputs.forEach(input => {
        input.addEventListener('change', function() {
            updatePayoutLabels(this.value);
        });
    });
}

function updatePayoutLabels(paymentType) {
    const payoutLabel = document.getElementById('payout-label');
    const payoutInput = document.getElementById('per-day-payout');
    
    if (paymentType === 'per_day') {
        if (payoutLabel) {
            payoutLabel.innerHTML = 'Daily payout per worker <span class="text-xs text-gray-400">(e.g., 25$ , 60 Kwacha)</span>';
        }
        if (payoutInput) {
            payoutInput.placeholder = 'Enter daily payout per worker';
        }
    } else if (paymentType === 'per_part') {
        if (payoutLabel) {
            payoutLabel.innerHTML = 'Payout per part <span class="text-xs text-gray-400">(e.g., 25$ , 60 Kwacha)</span>';
        }
        if (payoutInput) {
            payoutInput.placeholder = 'Enter payout per part';
        }
    }
}

function updateTaskStatusIndicator() {
    const dateInput = document.getElementById('task-start-date');
    const statusIndicator = document.getElementById('task-status-indicator');
    const statusValue = document.getElementById('task-status-value');
    
    if (dateInput && statusIndicator && statusValue) {
        const selectedDate = new Date(dateInput.value);
        const currentDate = new Date();
        currentDate.setHours(0, 0, 0, 0);
        selectedDate.setHours(0, 0, 0, 0);
        
        if (selectedDate < currentDate) {
            statusValue.textContent = 'Invalid';
            statusValue.className = 'text-red-600 font-bold';
            statusIndicator.classList.remove('hidden');
        } else if (selectedDate.getTime() === currentDate.getTime()) {
            statusValue.textContent = 'In Progress';
            statusValue.className = 'text-green-600 font-bold';
            statusIndicator.classList.remove('hidden');
        } else {
            statusValue.textContent = 'Pending';
            statusValue.className = 'text-orange-600 font-bold';
            statusIndicator.classList.remove('hidden');
        }
    }
}

function closeAddTaskModal() {
    document.getElementById('add-task-modal').classList.remove('modal-open');
}

// Payment type logic for add task modal
function setupPaymentTypeToggle() {
    const perPartGroup = document.getElementById('per-part-payout-group');
    const perDayGroup = document.getElementById('per-day-payout-group');
    const radios = document.querySelectorAll('input[name="payment_type"]');
    
    radios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'per_part') {
                perPartGroup.style.display = '';
                perDayGroup.style.display = 'none';
                // Make per-part fields required
                document.getElementById('per-part-payout').required = true;
                document.getElementById('per-part-currency').required = true;
                // Make per-day fields not required
                document.getElementById('per-day-payout').required = false;
                document.getElementById('per-day-currency').required = false;
            } else {
                perPartGroup.style.display = 'none';
                perDayGroup.style.display = '';
                // Make per-day fields required
                document.getElementById('per-day-payout').required = true;
                document.getElementById('per-day-currency').required = true;
                // Make per-part fields not required
                document.getElementById('per-part-payout').required = false;
                document.getElementById('per-part-currency').required = false;
            }
        });
    });
}

function createTask(event) {
    event.preventDefault();
    const form = event.target || document.getElementById('taskForm');
    const nameField = form.querySelector('input[name="name"]');
    const dateField = form.querySelector('input[name="start_date"]');
    const errorDivId = 'task-date-error';
    let errorDiv = document.getElementById(errorDivId);
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = errorDivId;
        errorDiv.className = 'alert alert-error mb-2';
        errorDiv.style.display = 'none';
        form.insertBefore(errorDiv, form.firstChild);
    }
    // Validate start date
    const today = new Date();
    today.setHours(0,0,0,0);
    const selectedDate = new Date(dateField.value);
    selectedDate.setHours(0,0,0,0);
    if (selectedDate < today) {
        errorDiv.textContent = 'Start date cannot be in the past.';
        errorDiv.style.display = '';
        dateField.focus();
        return;
    } else {
        errorDiv.style.display = 'none';
    }
    // Set status based on date
    let status = 'Pending';
    if (selectedDate.getTime() === today.getTime()) {
        status = 'In Progress';
    }
    const formData = new FormData(form);
    const paymentType = formData.get('payment_type') || 'per_day';
    let perPartPayout = null;
    let perPartCurrency = null;
    let perDayPayout = null;
    let perDayCurrency = null;
    
    if (paymentType === 'per_part') {
        perPartPayout = formData.get('per_part_payout');
        perPartCurrency = formData.get('per_part_currency');
        if (!perPartPayout || isNaN(perPartPayout) || Number(perPartPayout) <= 0) {
            errorDiv.textContent = 'Please enter a valid payout per part.';
            errorDiv.style.display = '';
            document.getElementById('per-part-payout').focus();
            return;
        }
        if (!perPartCurrency || perPartCurrency.trim() === '') {
            errorDiv.textContent = 'Please enter a currency for payout per part.';
            errorDiv.style.display = '';
            document.getElementById('per-part-currency').focus();
            return;
        }
    } else {
        perDayPayout = formData.get('per_day_payout');
        perDayCurrency = formData.get('per_day_currency');
        if (!perDayPayout || isNaN(perDayPayout) || Number(perDayPayout) <= 0) {
            errorDiv.textContent = 'Please enter a valid daily payout per worker.';
            errorDiv.style.display = '';
            document.getElementById('per-day-payout').focus();
            return;
        }
        if (!perDayCurrency || perDayCurrency.trim() === '') {
            errorDiv.textContent = 'Please enter a currency for daily payout.';
            errorDiv.style.display = '';
            document.getElementById('per-day-currency').focus();
            return;
        }
    }
    fetch('/api/task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: formData.get('name'),
            description: formData.get('description'),
            start_date: formData.get('start_date'),
            status: status,
            payment_type: paymentType,
            per_part_payout: perPartPayout,
            per_part_currency: perPartCurrency,
            per_day_payout: perDayPayout,
            per_day_currency: perDayCurrency
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            closeAddTaskModal();
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error creating task:', error);
        showCustomModal('Error', 'Failed to create task', 'error');
    });
}

// Expose modal functions globally
window.openLogoutModal = openLogoutModal;
window.closeLogoutModal = closeLogoutModal;
window.openAddWorkerModal = openAddWorkerModal;
window.closeAddWorkerModal = closeAddWorkerModal;
window.openAddTaskModal = openAddTaskModal;
window.closeAddTaskModal = closeAddTaskModal;
window.createTask = createTask;
window.setupPaymentTypeHandlers = setupPaymentTypeHandlers;
window.updatePayoutLabels = updatePayoutLabels;
// ...existing code...
window.openImportWorkersModal = openImportWorkersModal;
window.closeImportWorkersModal = closeImportWorkersModal;
window.loadImportFields = loadImportFields;
window.loadExcelColumns = loadExcelColumns;
window.resetImportForm = resetImportForm;
window.removeCustomField = removeCustomField;
window.openEditRoleModal = openEditRoleModal;
window.closeEditRoleModal = closeEditRoleModal;
window.updateRole = updateRole;
window.openRemoveTeamMemberModal = openRemoveTeamMemberModal;
window.closeRemoveTeamMemberModal = closeRemoveTeamMemberModal;
window.removeTeamMember = removeTeamMember;
window.saveNewField = saveNewField;

function closeAddTeamMemberModal() {
    document.getElementById('add-team-member-modal').close();
}

// Function to reinitialize Feather icons
function reinitializeFeatherIcons() {
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

// Function to create mapping row for Excel columns
function createMappingRow(field, columns) {
    const tr = document.createElement('tr');
    const fieldId = field.toLowerCase().replace(/ /g, '_');
    tr.innerHTML = `
        <td>${field}</td>
        <td>
            <select class="select select-bordered w-full" data-field="${fieldId}">
                <option value="">Select Column</option>
                ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
            </select>
        </td>
    `;
    return tr;
}

// Function to handle importing workers with column mapping
window.importWithMapping = async function() {
    const fileId = document.getElementById('columnMapping').dataset.fileId;
    const mapping = {};
    
    // Get all select elements in mapping table
    const selects = document.querySelectorAll('#mappingTableBody select');
    selects.forEach(select => {
        if (select.value) {
            mapping[select.dataset.field] = select.value;
        }
    });
    
    console.log('Starting import with mapping:', mapping);
    console.log('File ID:', fileId);
    
    // Show loading state
    const importButton = document.querySelector('button[onclick="importWithMapping()"]');
    const originalText = importButton.textContent;
    importButton.disabled = true;
    importButton.innerHTML = '<i class="material-icons">hourglass_empty</i>Importing...';
    
    fetch('/api/worker/import-mapped', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'mapping': JSON.stringify(mapping),
            'file_id': fileId
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(async result => {
        console.log('Import result:', result);
        
        if (result.error) {
            showCustomModal('Import Failed', `Import failed: ${result.error}`, 'error');
        } else {
            // Show success message with details
            const successMsg = `Import completed successfully!\n\nTotal records: ${result.total_records}\nSuccessful imports: ${result.successful_imports}\nDuplicates skipped: ${result.duplicate_records}\nErrors: ${result.error_records}`;
            
            if (result.error_records > 0) {
                const showDetails = await showCustomConfirm('Import Completed', successMsg + '\n\nWould you like to see the error details?');
                if (showDetails && result.error_details) {
                    showCustomModal('Error Details', 'Error details:\n' + result.error_details.join('\n'), 'warning');
                }
            } else {
                showCustomModal('Import Success', successMsg, 'success');
            }
            
            // Switch to results view
            document.getElementById('columnMapping').classList.add('hidden');
            document.getElementById('importResults').classList.remove('hidden');
        }
    })
    .catch(error => {
        console.error('Error importing workers:', error);
        showCustomModal('Import Error', `Failed to import workers: ${error.message}\n\nPlease check the browser console for more details and try again.`, 'error');
    })
    .finally(() => {
        // Reset button state
        importButton.disabled = false;
        importButton.innerHTML = originalText;
    });
}

// Currency selection handling
document.addEventListener('DOMContentLoaded', function() {
    setupPaymentTypeToggle();
    const currencyOptions = document.querySelectorAll('input[name="currency"]');
    const selectedCurrencySymbol = document.getElementById('selectedCurrencySymbol');
    
    // Update currency symbol when a radio button is selected
    currencyOptions.forEach(option => {
        option.addEventListener('change', function() {
            const symbol = this.dataset.symbol;
            selectedCurrencySymbol.textContent = symbol;
        });
    });

    // Set initial currency symbol
    const checkedCurrency = document.querySelector('input[name="currency"]:checked');
    if (checkedCurrency) {
        selectedCurrencySymbol.textContent = checkedCurrency.dataset.symbol;
    }
    
    // Debug task form
    const taskForm = document.getElementById('taskForm');
    if (taskForm) {
        console.log('Task form found:', taskForm);
        console.log('Form onsubmit before:', taskForm.onsubmit);
        
        // Remove any existing onsubmit handler
        taskForm.onsubmit = null;
        
        taskForm.addEventListener('submit', function(e) {
            console.log('Task form submit event triggered');
            console.log('Form validity:', this.checkValidity());
            console.log('Form elements:', this.elements);
            createTask(e);
        });
        

        
        console.log('Form onsubmit after:', taskForm.onsubmit);
    } else {
        console.log('Task form not found');
    }
});

// Ensure the date input cannot select before today
function setTaskStartDateMin() {
    const dateInput = document.getElementById('task-start-date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }
}
document.addEventListener('DOMContentLoaded', setTaskStartDateMin);

/* ---------------------------------------------
   Mobile UX helpers
----------------------------------------------*/
document.addEventListener('DOMContentLoaded', function () {
    const drawerCheckbox = document.getElementById('my-drawer');
    if (!drawerCheckbox) return;

    // 1. Auto-close sidebar after navigating on mobile
    const menuLinks = document.querySelectorAll('.sidebar-menu-item');
    menuLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Delay to allow link navigation when using Turbo/flask refresh
            setTimeout(() => {
                if (window.innerWidth <= 1023) {
                    drawerCheckbox.checked = false;
                }
            }, 150);
        });
    });

    // 2. Close when overlay tapped (safety – DaisyUI should already do this)
    const overlay = document.querySelector('label.drawer-overlay');
    if (overlay) {
        overlay.addEventListener('click', () => {
            drawerCheckbox.checked = false;
        });
    }
});