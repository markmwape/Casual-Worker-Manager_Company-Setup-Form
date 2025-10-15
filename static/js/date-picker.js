// Modern Date Picker Component
class DatePicker {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            defaultDate: new Date(),
            minDate: new Date(1900, 0, 1),
            maxDate: new Date(2100, 11, 31),
            onChange: null,
            theme: 'primary',
            placeholder: 'Select Date',
            ...options
        };
        
        // Handle null defaultDate (for edit task field)
        if (this.options.defaultDate === null) {
            this.currentDate = null;
        } else {
            this.currentDate = new Date(this.options.defaultDate);
        }
        
        this.init();
    }
    
    init() {
        this.createHTML();
        this.populateDropdowns();
        this.setupEventListeners();
        this.updateDisplay();
    }
    
    createHTML() {
        const wrapper = document.createElement('div');
        wrapper.className = 'date-picker-wrapper';
        
        const label = document.createElement('label');
        label.className = 'date-picker-label';
        label.textContent = this.options.placeholder;
        
        const container = document.createElement('div');
        container.className = `date-picker-container ${this.options.theme}`;
        
        // Add calendar icon
        const calendarIcon = document.createElement('i');
        calendarIcon.className = 'fas fa-calendar-alt text-blue-500 mr-2';
        calendarIcon.style.fontSize = '14px';
        
        // Year dropdown
        const yearSelect = document.createElement('select');
        yearSelect.className = 'date-picker-select';
        yearSelect.id = this.container.id + '-year';
        
        // Month dropdown
        const monthSelect = document.createElement('select');
        monthSelect.className = 'date-picker-select';
        monthSelect.id = this.container.id + '-month';
        
        // Day dropdown
        const daySelect = document.createElement('select');
        daySelect.className = 'date-picker-select';
        daySelect.id = this.container.id + '-day';
        
        // Separators
        const separator1 = document.createElement('span');
        separator1.className = 'date-picker-separator';
        separator1.textContent = '/';
        
        const separator2 = document.createElement('span');
        separator2.className = 'date-picker-separator';
        separator2.textContent = '/';
        
        // Hidden input for form submission
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = this.container.name || this.container.id;
        hiddenInput.id = this.container.id + '-value';
        
        // Error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'date-picker-error';
        errorDiv.textContent = 'Please select a valid date';
        
        // Assemble the component
        container.appendChild(calendarIcon);
        container.appendChild(yearSelect);
        container.appendChild(separator1);
        container.appendChild(monthSelect);
        container.appendChild(separator2);
        container.appendChild(daySelect);
        
        wrapper.appendChild(label);
        wrapper.appendChild(container);
        wrapper.appendChild(hiddenInput);
        wrapper.appendChild(errorDiv);
        
        // Replace the original input
        this.container.parentNode.insertBefore(wrapper, this.container);
        this.container.style.display = 'none';
        
        this.wrapper = wrapper;
        this.yearSelect = yearSelect;
        this.monthSelect = monthSelect;
        this.daySelect = daySelect;
        this.hiddenInput = hiddenInput;
        this.errorDiv = errorDiv;
    }
    
    populateDropdowns() {
        // Populate years
        const currentYear = new Date().getFullYear();
        const startYear = this.options.minDate.getFullYear();
        const endYear = this.options.maxDate.getFullYear();
        
        for (let year = startYear; year <= endYear; year++) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            this.yearSelect.appendChild(option);
        }
        
        // Populate months
        const months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        
        months.forEach((month, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = month;
            this.monthSelect.appendChild(option);
        });
        
        // Days will be populated dynamically based on selected month/year
        this.populateDays();
    }
    
    populateDays(selectedDay) {
        // Clear existing days
        this.daySelect.innerHTML = '';
        
        const year = parseInt(this.yearSelect.value);
        const month = parseInt(this.monthSelect.value);
        
        // Get number of days in the selected month
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        // Add day options
        for (let day = 1; day <= daysInMonth; day++) {
            const option = document.createElement('option');
            option.value = day;
            option.textContent = day;
            this.daySelect.appendChild(option);
        }
        // Preserve previously selected day if possible
        if (selectedDay && selectedDay <= daysInMonth) {
            this.daySelect.value = selectedDay;
        } else {
            this.daySelect.value = daysInMonth; // fallback to last valid day
        }
    }
    
    setupEventListeners() {
        this.yearSelect.addEventListener('change', () => {
            const prevDay = parseInt(this.daySelect.value);
            this.populateDays(prevDay);
            this.updateDate();
        });
        
        this.monthSelect.addEventListener('change', () => {
            const prevDay = parseInt(this.daySelect.value);
            this.populateDays(prevDay);
            this.updateDate();
        });
        
        this.daySelect.addEventListener('change', () => {
            this.updateDate();
        });
    }
    
    updateDate() {
        const year = parseInt(this.yearSelect.value);
        const month = parseInt(this.monthSelect.value);
        const day = parseInt(this.daySelect.value);
        
        if (year && month !== undefined && day) {
            this.currentDate = new Date(year, month, day);
            this.hiddenInput.value = this.formatDate(this.currentDate);
            this.validateDate();
            
            if (this.options.onChange) {
                this.options.onChange(this.currentDate, this.formatDate(this.currentDate));
            }
        }
    }
    
    updateDisplay() {
        if (this.currentDate) {
            this.yearSelect.value = this.currentDate.getFullYear();
            this.monthSelect.value = this.currentDate.getMonth();
            this.populateDays();
            this.daySelect.value = this.currentDate.getDate();
            this.hiddenInput.value = this.formatDate(this.currentDate);
        } else {
            // For null currentDate (edit task field), don't set any values
            this.hiddenInput.value = '';
        }
    }
    
    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    validateDate() {
        const selectedDate = new Date(this.currentDate);
        const isValid = selectedDate >= this.options.minDate && selectedDate <= this.options.maxDate;
        
        // Additional validation for task start dates (if this is a task date picker)
        if (this.container.id === 'task-start-date' || this.container.id === 'edit-task-start-date') {
            const currentDate = new Date();
            currentDate.setHours(0, 0, 0, 0);
            selectedDate.setHours(0, 0, 0, 0);
            
            if (selectedDate > currentDate) {
                // Future date selected - show warning but don't mark as error
                this.showFutureDateWarning();
                return true; // Still valid, just future date
            } else {
                this.hideFutureDateWarning();
            }
        }
        
        if (isValid) {
            this.wrapper.classList.remove('error');
        } else {
            this.wrapper.classList.add('error');
        }
        
        return isValid;
    }
    
    showFutureDateWarning() {
        // Create or update warning message
        let warningDiv = this.wrapper.querySelector('.date-picker-warning');
        if (!warningDiv) {
            warningDiv = document.createElement('div');
            warningDiv.className = 'date-picker-warning';
            this.wrapper.appendChild(warningDiv);
        }
        warningDiv.textContent = 'Future date selected - task will be set to "Pending" status';
        warningDiv.style.display = 'block';
    }
    
    hideFutureDateWarning() {
        const warningDiv = this.wrapper.querySelector('.date-picker-warning');
        if (warningDiv) {
            warningDiv.style.display = 'none';
        }
    }
    
    getValue() {
        return this.hiddenInput.value;
    }
    
    setValue(dateString) {
        if (dateString) {
            const date = new Date(dateString);
            if (!isNaN(date.getTime())) {
                this.currentDate = date;
                this.updateDisplay();
                
                // Also update the original input value
                if (this.container) {
                    this.container.value = dateString;
                }
            }
        }
    }
    
    setMinDate(date) {
        this.options.minDate = date;
        this.validateDate();
    }
    
    setMaxDate(date) {
        this.options.maxDate = date;
        this.validateDate();
    }
}

// Initialize all date pickers on page load
document.addEventListener('DOMContentLoaded', function() {
    // Find all date inputs and convert them to date pickers
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Skip if already converted
        if (input.dataset.datePickerInitialized) return;
        // Skip custom date picker for task-start-date to use native date picker modal
        if (input.id === 'task-start-date') return;
        
        // Get URL parameters for date values
        const urlParams = new URLSearchParams(window.location.search);
        let startDate = urlParams.get('start_date');
        let endDate = urlParams.get('end_date');
        
        // Set default values if not provided
        if (!startDate || !endDate) {
            endDate = new Date().toISOString().split('T')[0];
            startDate = new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0];
        }
        
        // Set the input value based on its ID
        if (input.id === 'startDate' && startDate) {
            input.value = startDate;
        } else if (input.id === 'endDate' && endDate) {
            input.value = endDate;
        }
        
        // Set maximum date to today for task start dates
        let maxDate = new Date(2100, 11, 31);
        if (input.id === 'task-start-date' || input.id === 'edit-task-start-date') {
            maxDate = new Date(); // Today is the maximum for task start dates
        }
        
        const datePicker = new DatePicker(input, {
            defaultDate: input.value ? new Date(input.value) : (input.id === 'edit-task-start-date' ? null : new Date()),
            maxDate: maxDate,
            onChange: function(date, formattedDate) {
                // Update the original input's value
                input.value = formattedDate;
                
                // Trigger the original input's change event
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
                
                // Update task status indicator if this is a task date picker
                if (input.id === 'task-start-date' && typeof updateTaskStatusIndicator === 'function') {
                    updateTaskStatusIndicator();
                }
                
                // If the input has an onchange attribute, execute it
                if (input.hasAttribute('onchange')) {
                    const onchangeCode = input.getAttribute('onchange');
                    try {
                        eval(onchangeCode);
                    } catch (e) {
                        console.error('Error executing onchange:', e);
                    }
                }
            }
        });
        
        // Store the date picker instance for later access
        input.datePickerInstance = datePicker;
        input.dataset.datePickerInitialized = 'true';
    });
    
    // Set up date validation for pages with start/end date pairs
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    if (startDateInput && endDateInput) {
        // Function to update end date minimum based on start date
        function updateEndDateMin() {
            if (startDateInput.value && startDateInput.datePickerInstance) {
                const startDate = new Date(startDateInput.value);
                startDateInput.datePickerInstance.setMinDate(new Date(1900, 0, 1));
                endDateInput.datePickerInstance.setMinDate(startDate);
                
                // If end date is before start date, set it to 1 day after start date
                if (endDateInput.value && new Date(endDateInput.value) < startDate) {
                    const newEndDate = new Date(startDate);
                    newEndDate.setDate(newEndDate.getDate() + 1);
                    endDateInput.datePickerInstance.setValue(newEndDate.toISOString().split('T')[0]);
                }
            }
        }
        
        // Function to update start date maximum based on end date
        function updateStartDateMax() {
            if (endDateInput.value && endDateInput.datePickerInstance) {
                const endDate = new Date(endDateInput.value);
                endDateInput.datePickerInstance.setMaxDate(new Date(2100, 11, 31));
                startDateInput.datePickerInstance.setMaxDate(endDate);
                
                // If start date is after end date, set it to 1 day before end date
                if (startDateInput.value && new Date(startDateInput.value) > endDate) {
                    const newStartDate = new Date(endDate);
                    newStartDate.setDate(newStartDate.getDate() - 1);
                    startDateInput.datePickerInstance.setValue(newStartDate.toISOString().split('T')[0]);
                }
            }
        }
        
        // Add event listeners for real-time validation
        startDateInput.addEventListener('change', updateEndDateMin);
        endDateInput.addEventListener('change', updateStartDateMax);
        
        // Initialize constraints
        updateEndDateMin();
        updateStartDateMax();
    }
});

// Global function to create date pickers manually
window.createDatePicker = function(container, options) {
    return new DatePicker(container, options);
};