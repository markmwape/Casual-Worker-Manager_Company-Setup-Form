// Reports page functions
function toggleCustomFields(type) {
    const perDayWindow = document.getElementById('customFieldsWindowPerDay');
    const perPartWindow = document.getElementById('customFieldsWindowPerPart');
    
    if (type === 'perDay') {
        if (perDayWindow) {
            if (perDayWindow.style.display === 'none' || perDayWindow.style.display === '') {
                perDayWindow.style.display = 'block';
            } else {
                perDayWindow.style.display = 'none';
            }
        }
    } else if (type === 'perPart') {
        if (perPartWindow) {
            if (perPartWindow.style.display === 'none' || perPartWindow.style.display === '') {
                perPartWindow.style.display = 'block';
            } else {
                perPartWindow.style.display = 'none';
            }
        }
    }
}

function downloadReport(type) {
    const startDate = document.getElementById('startDate')?.value;
    const endDate = document.getElementById('endDate')?.value;
    
    if (!startDate || !endDate) {
        showCustomModal('Date Range Required', 'Please select both start and end dates before downloading the report.', 'warning');
        return;
    }
    
    // Validate date range
    if (new Date(startDate) > new Date(endDate)) {
        showCustomModal('Invalid Date Range', 'Start date cannot be after end date.', 'warning');
        return;
    }
    
    // Check if report has data
    const tableSelector = type === 'per_day' 
        ? '.bg-white.rounded-3xl.shadow-xl.border.border-green-200 tbody tr' 
        : '.bg-white.rounded-3xl.shadow-xl.border.border-purple-200 tbody tr';
    const rows = document.querySelectorAll(tableSelector);
    
    if (rows.length === 0) {
        showCustomModal('No Data Available', 'There is no data to download for the selected date range. Please adjust your dates or ensure workers have been assigned to tasks.', 'warning');
        return;
    }
    
    const url = `/api/reports?type=${type}&start_date=${startDate}&end_date=${endDate}`;
    
    // Create a temporary link to trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = `${type}_report_${startDate}_to_${endDate}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showToast(`${type.replace('_', ' ')} report download started!`, 'success');
}

function closeReportErrorModal() {
    const modal = document.getElementById('reportErrorModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function openAddReportFieldModalPerDayV2() {
    const modal = document.getElementById('add-report-field-modal-per-day');
    if (modal) {
        // Reset the modal for new field creation
        modal.dataset.isEditing = 'false';
        modal.dataset.editingFieldId = '';
        
        // Clear the form
        const form = document.getElementById('reportFieldFormPerDay');
        if (form) form.reset();
        
        const maxLimitWrapper = document.getElementById('maxLimitInputWrapperPerDay');
        if (maxLimitWrapper) maxLimitWrapper.classList.add('hidden');
        
        const enableMaxLimit = document.getElementById('enableMaxLimitPerDay');
        if (enableMaxLimit) enableMaxLimit.checked = false;
        
        const payoutTypeInput = document.getElementById('payoutTypeInputPerDay');
        if (payoutTypeInput) payoutTypeInput.value = 'per_day';
        
        // Reset age condition controls
        const ageWrapper = document.getElementById('ageConditionWrapperPerDay');
        if (ageWrapper) ageWrapper.classList.add('hidden');
        
        const enableAgeCondition = document.getElementById('enableAgeConditionPerDay');
        if (enableAgeCondition) enableAgeCondition.checked = false;
        
        const ageValue = document.getElementById('ageValuePerDay');
        if (ageValue) ageValue.value = '';
        
        const ageConditionValue = document.getElementById('ageConditionValuePerDay');
        if (ageConditionValue) ageConditionValue.value = '';
        
        // Reset button text and heading
        const submitButton = modal.querySelector('.btn-secondary');
        if (submitButton) {
            submitButton.innerHTML = '<i data-feather="plus" class="mr-2"></i>Add Custom Field';
        }
        
        const heading = modal.querySelector('h3');
        if (heading) {
            heading.textContent = 'Add Custom Report Field (Per Day)';
        }
        
        modal.showModal();
    } else {
        console.error('Modal not found: add-report-field-modal-per-day');
        showToast('Error opening modal', 'error');
    }
}

function openAddReportFieldModalPerUnitV2() {
    const modal = document.getElementById('add-report-field-modal-per-unit');
    if (modal) {
        // Reset the modal for new field creation
        modal.dataset.isEditing = 'false';
        modal.dataset.editingFieldId = '';
        
        // Clear the form
        const form = document.getElementById('reportFieldFormPerUnit');
        if (form) form.reset();
        
        const maxLimitWrapper = document.getElementById('maxLimitInputWrapperPerUnit');
        if (maxLimitWrapper) maxLimitWrapper.classList.add('hidden');
        
        const enableMaxLimit = document.getElementById('enableMaxLimitPerUnit');
        if (enableMaxLimit) enableMaxLimit.checked = false;
        
        const payoutTypeInput = document.getElementById('payoutTypeInputPerUnit');
        if (payoutTypeInput) payoutTypeInput.value = 'per_part';
        
        // Reset age condition controls
        const ageWrapper = document.getElementById('ageConditionWrapperPerUnit');
        if (ageWrapper) ageWrapper.classList.add('hidden');
        
        const enableAgeCondition = document.getElementById('enableAgeConditionPerUnit');
        if (enableAgeCondition) enableAgeCondition.checked = false;
        
        const ageValue = document.getElementById('ageValuePerUnit');
        if (ageValue) ageValue.value = '';
        
        const ageConditionValue = document.getElementById('ageConditionValuePerUnit');
        if (ageConditionValue) ageConditionValue.value = '';
        
        // Reset button text and heading
        const submitButton = modal.querySelector('.btn-secondary');
        if (submitButton) {
            submitButton.innerHTML = '<i data-feather="plus" class="mr-2"></i>Add Custom Field';
        }
        
        const heading = modal.querySelector('h3');
        if (heading) {
            heading.textContent = 'Add Custom Report Field (Per Unit)';
        }
        
        modal.showModal();
    } else {
        console.error('Modal not found: add-report-field-modal-per-unit');
        showToast('Error opening modal', 'error');
    }
}

function editReportField(fieldId, fieldName, formula, payoutType) {
    // Fetch the full field data from the API to get max_limit
    fetch(`/api/report-field/${fieldId}`)
        .then(response => response.json())
        .then(fieldData => {
            populateEditModal(fieldId, fieldName, formula, payoutType, fieldData.max_limit || null);
        })
        .catch(error => {
            // If API call fails, fallback to basic edit without max_limit
            console.error('Error fetching field data:', error);
            populateEditModal(fieldId, fieldName, formula, payoutType, null);
        });
}

function populateEditModal(fieldId, fieldName, formula, payoutType, maxLimit) {
    // Determine which modal to use based on payout type
    const isPerDay = payoutType === 'per_day' || payoutType !== 'per_part';
    const modalId = isPerDay ? 'add-report-field-modal-per-day' : 'add-report-field-modal-per-unit';
    const suffix = isPerDay ? 'PerDay' : 'PerUnit';
    
    const modal = document.getElementById(modalId);
    if (!modal) {
        console.error('Modal not found:', modalId);
        return;
    }
    
    // Parse formula for age conditions
    let cleanFormula = formula;
    let hasAgeCondition = false;
    let ageOperator = '>';
    let ageValue = '';
    let conditionValue = '';
    
    // Check if formula has age condition pattern: "value if age op value else (formula)"
    const ageConditionPattern = /^([\d.]+)\s+if\s+age\s+([><=]+)\s+([\d]+)\s+else\s+\((.*)\)$/;
    const match = formula.match(ageConditionPattern);
    if (match) {
        hasAgeCondition = true;
        conditionValue = match[1];
        ageOperator = match[2];
        ageValue = match[3];
        cleanFormula = match[4];
    }
    
    // Get form elements
    const form = modal.querySelector('form');
    const nameInput = form.querySelector('input[name="name"]');
    const formulaTextarea = document.getElementById(`formulaBuilder${suffix}`);
    const fieldIdInput = form.querySelector('input[name="field_id"]');
    
    // Set basic field values
    if (nameInput) nameInput.value = fieldName;
    if (formulaTextarea) formulaTextarea.value = cleanFormula;
    if (fieldIdInput) fieldIdInput.value = fieldId;
    
    // Handle max limit
    const maxLimitCheckbox = document.getElementById(`enableMaxLimit${suffix}`);
    const maxLimitInput = document.getElementById(`maxLimitValue${suffix}`);
    const maxLimitWrapper = document.getElementById(`maxLimitInputWrapper${suffix}`);
    
    if (maxLimit !== null && maxLimit !== undefined && maxLimitCheckbox && maxLimitInput) {
        maxLimitCheckbox.checked = true;
        maxLimitInput.value = maxLimit;
        if (maxLimitWrapper) maxLimitWrapper.classList.remove('hidden');
    } else if (maxLimitCheckbox) {
        maxLimitCheckbox.checked = false;
        if (maxLimitInput) maxLimitInput.value = '';
        if (maxLimitWrapper) maxLimitWrapper.classList.add('hidden');
    }
    
    // Handle age condition
    const ageCheckbox = document.getElementById(`enableAgeCondition${suffix}`);
    const ageWrapper = document.getElementById(`ageConditionWrapper${suffix}`);
    const ageOpSelect = document.getElementById(`ageOperator${suffix}`);
    const ageValInput = document.getElementById(`ageValue${suffix}`);
    const ageCondValInput = document.getElementById(`ageConditionValue${suffix}`);
    
    if (hasAgeCondition && ageCheckbox) {
        ageCheckbox.checked = true;
        if (ageWrapper) ageWrapper.classList.remove('hidden');
        if (ageOpSelect) ageOpSelect.value = ageOperator;
        if (ageValInput) ageValInput.value = ageValue;
        if (ageCondValInput) ageCondValInput.value = conditionValue;
    } else if (ageCheckbox) {
        ageCheckbox.checked = false;
        if (ageWrapper) ageWrapper.classList.add('hidden');
        if (ageOpSelect) ageOpSelect.value = '>';
        if (ageValInput) ageValInput.value = '';
        if (ageCondValInput) ageCondValInput.value = '';
    }
    
    // Update modal heading
    const heading = modal.querySelector('h3');
    if (heading) {
        heading.textContent = `Edit Custom Report Field (${isPerDay ? 'Per Day' : 'Per Unit'})`;
    }
    
    // Update button text
    const submitButton = modal.querySelector('button[onclick*="addCustomField"]');
    if (submitButton) {
        const buttonText = submitButton.querySelector('i') ? 
            '<i data-feather="save" class="mr-2"></i>Update Field' : 
            'Update Field';
        submitButton.innerHTML = buttonText;
        if (window.feather) feather.replace();
    }
    
    // Show the modal
    modal.showModal();
    
    // Re-register event listeners for formula builder
    if (window.registerFormulaBuilderEvents) {
        window.registerFormulaBuilderEvents();
    }
}

async function deleteReportField(fieldId) {
    const confirmed = await showCustomConfirm('Delete Report Field', 'Are you sure you want to delete this report field? This action cannot be undone.');
    if (!confirmed) {
        return;
    }
    
    fetch(`/api/report-field?id=${fieldId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showCustomModal('Error', result.error, 'error');
        } else {
            showCustomModal('Success', 'Report field deleted successfully', 'success');
            setTimeout(() => window.location.reload(), 1000);
        }
    })
    .catch(error => {
        console.error('Error deleting report field:', error);
        showCustomModal('Error', 'Failed to delete report field', 'error');
    });
}

// Worker edit functions
function openEditWorkerModal(workerId) {
    console.log('Opening edit worker modal for worker ID:', workerId);
    
    // First, fetch the worker data
    fetch(`/api/worker/${workerId}`)
        .then(response => response.json())
        .then(worker => {
            if (worker.error) {
                showToast(worker.error, 'error');
                return;
            }
            
            // Populate the form with worker data
            const form = document.getElementById('workerForm');
            if (form) {
                // Set form to edit mode
                form.setAttribute('data-edit-worker-id', workerId);
                
                // Fill in the basic fields
                const firstNameInput = form.querySelector('input[name="first_name"]');
                const lastNameInput = form.querySelector('input[name="last_name"]');
                const dobInput = form.querySelector('input[name="date_of_birth"]');
                
                if (firstNameInput) firstNameInput.value = worker.first_name || '';
                if (lastNameInput) lastNameInput.value = worker.last_name || '';
                if (dobInput) dobInput.value = worker.date_of_birth || '';
                
                // Fill in custom fields
                Object.keys(worker.custom_fields || {}).forEach(fieldName => {
                    const fieldInput = form.querySelector(`input[name="${fieldName}"], select[name="${fieldName}"], textarea[name="${fieldName}"]`);
                    if (fieldInput) {
                        fieldInput.value = worker.custom_fields[fieldName] || '';
                    }
                });
                
                // Update submit button text
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.textContent = 'Update Worker';
                
                // Update modal title
                const modalTitle = document.querySelector('#add-worker-modal h3');
                if (modalTitle) modalTitle.textContent = 'Edit Worker';
                
                // Open the modal
                openAddWorkerModal();
            }
        })
        .catch(error => {
            console.error('Error fetching worker data:', error);
            showToast('Failed to load worker data', 'error');
        });
}

function openDeleteWorkerModal(workerId) {
    const modal = document.getElementById('delete-worker-modal');
    if (modal) {
        // Set the worker ID in a hidden field or data attribute
        const deleteBtn = modal.querySelector('.btn-error');
        if (deleteBtn) {
            deleteBtn.setAttribute('data-worker-id', workerId);
        }
        modal.showModal();
    }
}

// Add event handlers for the delete worker modal
document.addEventListener('DOMContentLoaded', function() {
    const deleteWorkerModal = document.getElementById('delete-worker-modal');
    if (deleteWorkerModal) {
        const confirmDeleteBtn = deleteWorkerModal.querySelector('.btn-error');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', function() {
                const workerId = this.getAttribute('data-worker-id');
                if (workerId) {
                    fetch(`/api/worker/${workerId}`, {
                        method: 'DELETE'
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.error) {
                            showToast(result.error, 'error');
                        } else {
                            showToast('Worker deleted successfully!', 'success');
                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        }
                        deleteWorkerModal.close();
                    })
                    .catch(error => {
                        console.error('Error deleting worker:', error);
                        showToast('Failed to delete worker', 'error');
                        deleteWorkerModal.close();
                    });
                }
            });
        }
    }
    
    // Add event handler to reset the add worker modal when opened
    const addWorkerModal = document.getElementById('add-worker-modal');
    if (addWorkerModal) {
        addWorkerModal.addEventListener('close', function() {
            // Reset the modal title and button text when closed
            const modalTitle = document.querySelector('#add-worker-modal h3');
            const submitBtn = document.querySelector('#workerForm button[type="submit"]');
            const form = document.getElementById('workerForm');
            
            if (modalTitle) modalTitle.textContent = 'Add New Worker';
            if (submitBtn) submitBtn.textContent = 'Add Worker';
            if (form) {
                form.removeAttribute('data-edit-worker-id');
                form.reset();
            }
        });
    }
});

function openDeleteWorkerModal(workerId) {
    const modal = document.getElementById('delete-worker-modal');
    if (modal) {
        // Set the worker ID in a hidden field or data attribute
        const deleteBtn = modal.querySelector('.btn-error');
        if (deleteBtn) {
            deleteBtn.setAttribute('data-worker-id', workerId);
        }
        modal.showModal();
    }
}

function resetImportForm() {
    document.getElementById('columnMapping').classList.add('hidden');
    document.getElementById('importForm').classList.remove('hidden');
    document.getElementById('importResults').classList.add('hidden');
}

async function removeCustomField(fieldId) {
    const confirmed = await showCustomConfirm('Delete Custom Field', 'Are you sure you want to delete this custom field?');
    if (!confirmed) {
        return;
    }
    
    fetch(`/api/import-field/${fieldId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(result => {
            if (result.error) {
                showToast(result.error, 'error');
            } else {
                showToast('Custom field deleted successfully!', 'success');
                loadImportFields();
            }
        })
        .catch(error => {
            console.error('Error deleting custom field:', error);
            showToast('Failed to delete custom field', 'error');
        });
}

function saveNewField() {
    const fieldName = document.getElementById('newFieldName').value.trim();
    
    if (!fieldName) {
        showToast('Please enter a field name', 'warning');
        return;
    }
    
    fetch('/api/import-field', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: fieldName,
            type: 'text'
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showToast(result.error, 'error');
        } else {
            showToast('Custom field added successfully!', 'success');
            document.getElementById('newFieldName').value = '';
            loadImportFields();
        }
    })
    .catch(error => {
        console.error('Error adding custom field:', error);
        showToast('Failed to add custom field', 'error');
    });
}

// Team member modal functions
function openEditRoleModal(userId, email, currentRole) {
    document.getElementById('edit-user-id').value = userId;
    document.getElementById('edit-email').value = email;
    document.getElementById('edit-role').value = currentRole;
    document.getElementById('edit-role-modal').showModal();
}

function closeEditRoleModal() {
    document.getElementById('edit-role-modal').close();
}

function openRemoveTeamMemberModal(userId, email) {
    document.getElementById('remove-user-id').value = userId;
    document.getElementById('remove-email').textContent = email;
    document.getElementById('remove-team-member-modal').showModal();
}

function closeRemoveTeamMemberModal() {
    document.getElementById('remove-team-member-modal').close();
}

function updateRole(event) {
    // This function is now handled by the form event listener in home.html
    event.preventDefault();
}

function removeTeamMember(event) {
    // This function is now handled by the form event listener in home.html
    event.preventDefault();
}

// Add event handlers for the delete worker modal
document.addEventListener('DOMContentLoaded', function() {
    const deleteWorkerModal = document.getElementById('delete-worker-modal');
    if (deleteWorkerModal) {
        const confirmDeleteBtn = deleteWorkerModal.querySelector('.btn-error');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', function() {
                const workerId = this.getAttribute('data-worker-id');
                if (workerId) {
                    fetch(`/api/worker/${workerId}`, {
                        method: 'DELETE'
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.error) {
                            showToast(result.error, 'error');
                        } else {
                            showToast('Worker deleted successfully!', 'success');
                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        }
                        deleteWorkerModal.close();
                    })
                    .catch(error => {
                        console.error('Error deleting worker:', error);
                        showToast('Failed to delete worker', 'error');
                        deleteWorkerModal.close();
                    });
                }
            });
        }
    }
});

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

// Expose functions globally for reports page
window.toggleCustomFields = toggleCustomFields;
window.downloadReport = downloadReport;
window.openEditWorkerModal = openEditWorkerModal;
window.openDeleteWorkerModal = openDeleteWorkerModal;
window.closeReportErrorModal = closeReportErrorModal;
window.openAddReportFieldModalPerDayV2 = openAddReportFieldModalPerDayV2;
window.openAddReportFieldModalPerUnitV2 = openAddReportFieldModalPerUnitV2;
window.editReportField = editReportField;
window.deleteReportField = deleteReportField;

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
        
        // Reset modal title
        const modalTitle = modal.querySelector('h3');
        if (modalTitle) {
            modalTitle.textContent = 'Add New Worker';
        }
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.textContent = 'Add Worker';
    }
    
    modal.showModal();
}

function closeAddWorkerModal() {
    const modal = document.getElementById('add-worker-modal');
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

function saveNewField() {
    const fieldNameInput = document.getElementById('newFieldName');
    const fieldName = fieldNameInput?.value?.trim();
    
    if (!fieldName) {
        showToast('Please enter a field name', 'error');
        return;
    }
    
    // Save new field to backend
    fetch('/api/import-field', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: fieldName,
            type: 'text'
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showToast(result.error, 'error');
        } else {
            showToast('Field added successfully!', 'success');
            fieldNameInput.value = '';
            loadImportFields(); // Reload the fields
        }
    })
    .catch(error => {
        console.error('Error saving field:', error);
        showToast('Failed to save field', 'error');
    });
}

function resetImportForm() {
    // Hide column mapping and show import form
    document.getElementById('columnMapping').classList.add('hidden');
    document.getElementById('importForm').classList.remove('hidden');
    
    // Reset the form
    const form = document.getElementById('importWorkersForm');
    if (form) {
        form.reset();
    }
}

async function removeCustomField(fieldId) {
    const confirmed = await showCustomConfirm('Remove Custom Field', 'Are you sure you want to remove this custom field?');
    if (!confirmed) {
        return;
    }
    
    fetch(`/api/import-field/${fieldId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showToast(result.error, 'error');
        } else {
            showToast('Field removed successfully!', 'success');
            loadImportFields(); // Reload the fields
        }
    })
    .catch(error => {
        console.error('Error removing field:', error);
        showToast('Failed to remove field', 'error');
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
    const perPartPayoutGroup = document.getElementById('per-part-payout-group');
    const perDayPayoutGroup = document.getElementById('per-day-payout-group');
    const perPartPayout = document.getElementById('per-part-payout');
    const perPartCurrency = document.getElementById('per-part-currency');
    const perDayPayout = document.getElementById('per-day-payout');
    const perDayCurrency = document.getElementById('per-day-currency');
    
    if (paymentType === 'per_day') {
        if (perPartPayoutGroup) perPartPayoutGroup.style.display = 'none';
        if (perDayPayoutGroup) perDayPayoutGroup.style.display = '';
        
        // Update required attributes
        if (perPartPayout) perPartPayout.removeAttribute('required');
        if (perPartCurrency) perPartCurrency.removeAttribute('required');
        if (perDayPayout) perDayPayout.setAttribute('required', 'required');
        if (perDayCurrency) perDayCurrency.setAttribute('required', 'required');
        
        if (payoutLabel) {
            payoutLabel.innerHTML = 'Daily payout per worker <span class="text-xs text-gray-400">(e.g., 25$ , 60 Kwacha)</span>';
        }
        if (payoutInput) {
            payoutInput.placeholder = 'Enter daily payout per worker';
        }
    } else if (paymentType === 'per_part') {
        if (perPartPayoutGroup) perPartPayoutGroup.style.display = '';
        if (perDayPayoutGroup) perDayPayoutGroup.style.display = 'none';
        
        // Update required attributes
        if (perPartPayout) perPartPayout.setAttribute('required', 'required');
        if (perPartCurrency) perPartCurrency.setAttribute('required', 'required');
        if (perDayPayout) perDayPayout.removeAttribute('required');
        if (perDayCurrency) perDayCurrency.removeAttribute('required');
        
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
        
        // More robust validation for payout
        const payoutValue = perPartPayout ? parseFloat(perPartPayout) : null;
        if (!perPartPayout || perPartPayout.trim() === '' || isNaN(payoutValue) || payoutValue <= 0) {
            errorDiv.textContent = 'Please enter a valid payout per part (must be a positive number).';
            errorDiv.style.display = '';
            document.getElementById('per-part-payout').focus();
            return;
        }
        if (!perPartCurrency || perPartCurrency.trim() === '') {
            errorDiv.textContent = 'Please select a currency for payout per part.';
            errorDiv.style.display = '';
            document.getElementById('per-part-currency').focus();
            return;
        }
    } else {
        perDayPayout = formData.get('per_day_payout');
        perDayCurrency = formData.get('per_day_currency');
        
        // More robust validation for payout
        const payoutValue = perDayPayout ? parseFloat(perDayPayout) : null;
        if (!perDayPayout || perDayPayout.trim() === '' || isNaN(payoutValue) || payoutValue <= 0) {
            errorDiv.textContent = 'Please enter a valid daily payout per worker (must be a positive number).';
            errorDiv.style.display = '';
            document.getElementById('per-day-payout').focus();
            return;
        }
        if (!perDayCurrency || perDayCurrency.trim() === '') {
            errorDiv.textContent = 'Please select a currency for daily payout.';
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

// Additional missing functions
function deleteTask() {
    const taskId = document.getElementById('delete-task-id')?.value;
    if (!taskId) return;
    
    fetch(`/api/task/${taskId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showToast(result.error, 'error');
        } else {
            showToast('Task deleted successfully!', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    })
    .catch(error => {
        console.error('Error deleting task:', error);
        showToast('Failed to delete task', 'error');
    })
    .finally(() => {
        document.getElementById('delete-task-modal')?.close();
    });
}

function closeEditTaskModal() {
    const modal = document.getElementById('edit-task-modal');
    if (modal) {
        modal.classList.remove('modal-open');
    }
}

async function deleteAllWorkers() {
    const confirmed = await showCustomConfirm('Delete All Workers', 'Are you sure you want to delete ALL workers? This action cannot be undone.');
    if (!confirmed) {
        return;
    }
    
    fetch('/api/worker/delete-all', {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showToast(result.error, 'error');
        } else {
            showToast('All workers deleted successfully!', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    })
    .catch(error => {
        console.error('Error deleting all workers:', error);
        showToast('Failed to delete all workers', 'error');
    })
    .finally(() => {
        document.getElementById('delete-all-workers-modal')?.close();
    });
}

// Note: addWorkerToTask and closeAddWorkerToTaskModal functions are now handled in the modal template

// Expose additional functions globally
window.deleteTask = deleteTask;
window.closeEditTaskModal = closeEditTaskModal;
window.deleteAllWorkers = deleteAllWorkers;

// Report field functions
// Note: All report field modal functions (addCustomFieldPerDay, addCustomFieldPerUnit,
// insertOperator, insertNumber, closeAddReportFieldModalPerDay, closeAddReportFieldModalPerUnit)
// are now defined in templates/modals/add_report_field.html to ensure correct element IDs
// and avoid conflicts between old and new modal implementations.

// Additional worker management functions
function openEditWorkerModal(workerId) {
    fetch(`/api/worker/${workerId}`)
    .then(response => response.json())
    .then(worker => {
        if (worker.error) {
            showToast(worker.error, 'error');
            return;
        }
        
        // Fill the form with worker data
        const form = document.getElementById('workerForm');
        if (form) {
            form.setAttribute('data-edit-worker-id', workerId);
            
            // Set form field values
            const firstNameField = form.querySelector('input[name="first_name"]');
            const lastNameField = form.querySelector('input[name="last_name"]');
            const dobField = form.querySelector('input[name="date_of_birth"]');
            
            if (firstNameField) firstNameField.value = worker.first_name || '';
            if (lastNameField) lastNameField.value = worker.last_name || '';
            if (dobField) dobField.value = worker.date_of_birth || '';
            
            // Set custom field values
            if (worker.custom_field_values) {
                worker.custom_field_values.forEach(customValue => {
                    const field = form.querySelector(`input[name="custom_field_${customValue.custom_field_id}"]`);
                    if (field) {
                        field.value = customValue.value || '';
                    }
                });
            }
            
            // Change submit button text
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.textContent = 'Update Worker';
        }
        
        // Open the modal
        const modal = document.getElementById('add-worker-modal');
        if (modal) {
            modal.showModal();
        }
    })
    .catch(error => {
        console.error('Error loading worker:', error);
        showToast('Failed to load worker data', 'error');
    });
}

function openDeleteWorkerModal(workerId) {
    const modal = document.getElementById('delete-worker-modal');
    const input = document.getElementById('delete-worker-id');
    
    if (input) {
        input.value = workerId;
    }
    
    if (modal) {
        modal.showModal();
    }
}

async function deleteSelectedWorkers() {
    const checkedBoxes = document.querySelectorAll('.worker-checkbox:checked');
    if (checkedBoxes.length === 0) {
        showToast('Please select workers to delete', 'warning');
        return;
    }
    
    const confirmed = await showCustomConfirm('Delete Selected Workers', `Are you sure you want to delete ${checkedBoxes.length} selected worker(s)?`);
    if (!confirmed) {
        return;
    }
    
    const workerIds = Array.from(checkedBoxes).map(cb => cb.dataset.workerId);
    
    fetch('/api/worker/delete-selected', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ worker_ids: workerIds })
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showToast(result.error, 'error');
        } else {
            showToast(`${result.deleted_count} worker(s) deleted successfully!`, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    })
    .catch(error => {
        console.error('Error deleting workers:', error);
        showToast('Failed to delete workers', 'error');
    });
}

// Add select all functionality
document.addEventListener('DOMContentLoaded', function() {
    const selectAllCheckbox = document.getElementById('selectAllWorkers');
    const workerCheckboxes = document.querySelectorAll('.worker-checkbox');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            workerCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateDeleteSelectedBtn();
        });
    }
    
    workerCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateDeleteSelectedBtn);
    });
    
    function updateDeleteSelectedBtn() {
        const checkedBoxes = document.querySelectorAll('.worker-checkbox:checked');
        if (deleteSelectedBtn) {
            if (checkedBoxes.length > 0) {
                deleteSelectedBtn.classList.remove('hidden');
            } else {
                deleteSelectedBtn.classList.add('hidden');
            }
        }
        
        // Update select all checkbox state
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = checkedBoxes.length === workerCheckboxes.length;
            selectAllCheckbox.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < workerCheckboxes.length;
        }
    }
});

// Export additional worker functions
window.openEditWorkerModal = openEditWorkerModal;
window.openDeleteWorkerModal = openDeleteWorkerModal;
window.deleteSelectedWorkers = deleteSelectedWorkers;

// Additional utility functions
function closeSuccessAlert() {
    const alert = document.querySelector('.alert-success');
    if (alert) {
        alert.style.display = 'none';
    }
}

function copyWorkspaceCode() {
    const codeElement = document.querySelector('[data-workspace-code]');
    if (codeElement) {
        const code = codeElement.value || codeElement.textContent;
        if (code && code.trim()) {
            navigator.clipboard.writeText(code.trim()).then(() => {
                showToast('Workspace code copied to clipboard!', 'success');
            }).catch(() => {
                showToast('Failed to copy workspace code', 'error');
            });
        } else {
            showToast('No workspace code found to copy', 'error');
        }
    } else {
        showToast('Workspace code element not found', 'error');
    }
}

function closeReportErrorModal() {
    const modal = document.getElementById('reportErrorModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function toggleUnitsSearch() {
    const searchContainer = document.getElementById('searchContainer');
    const searchBtn = document.getElementById('showSearchBtn');
    
    if (searchContainer && searchBtn) {
        if (searchContainer.classList.contains('hidden')) {
            searchContainer.classList.remove('hidden');
            searchBtn.style.display = 'none';
        } else {
            searchContainer.classList.add('hidden');
            searchBtn.style.display = 'block';
        }
    }
}

// Export utility functions
window.closeSuccessAlert = closeSuccessAlert;
window.copyWorkspaceCode = copyWorkspaceCode;
window.closeReportErrorModal = closeReportErrorModal;
window.openAddReportFieldModalPerDayV2 = openAddReportFieldModalPerDayV2;
window.openAddReportFieldModalPerUnitV2 = openAddReportFieldModalPerUnitV2;
window.toggleUnitsSearch = toggleUnitsSearch;

// Additional report field management functions
// Export report field management functions
window.editReportField = editReportField;
window.deleteReportField = deleteReportField;

// Report preview update function
function updateReportPreview() {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    const startDate = startDateInput?.dataset.isoDate;
    const endDate = endDateInput?.dataset.isoDate;
    
    if (startDate && endDate) {
        console.log('Updating report preview for date range:', startDate, 'to', endDate);
        // This would typically reload the report data via AJAX
        // For now, we'll just reload the page with query parameters
        const params = new URLSearchParams();
        params.append('start_date', startDate);
        params.append('end_date', endDate);
        
        // Update the current URL without reloading the page
        const newUrl = `${window.location.pathname}?${params.toString()}`;
        window.history.replaceState({}, '', newUrl);
        
        // In a full implementation, you would fetch new data via AJAX
        // For now, let's reload the page to apply the date filter
        window.location.reload();
    }
}

// Export report preview function
window.updateReportPreview = updateReportPreview;

// Ensure copyWorkspaceCode is available globally
window.copyWorkspaceCode = copyWorkspaceCode;

// Ensure all critical functions are available
window.showToast = showToast;
window.showCustomModal = showCustomModal;
window.showCustomConfirm = showCustomConfirm;