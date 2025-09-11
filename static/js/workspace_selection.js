// Workspace Selection JavaScript

// Fix for scrollHeight error and other potential DOM issues
if (typeof document !== 'undefined' && document.body) {
    // Safe to access document.body.scrollHeight
    try {
        // Initialize any scroll-related functionality safely
        const body = document.body;
        if (body && typeof body.scrollHeight !== 'undefined') {
            // Safe to use scrollHeight
        }
    } catch (error) {
        console.warn('ScrollHeight access error:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const joinForm = document.getElementById('join-workspace-form');
    const createForm = document.getElementById('create-workspace-form');
    const joinError = document.getElementById('join-error');
    const createError = document.getElementById('create-error');

    // Check for workspace code in URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const workspaceCodeFromUrl = urlParams.get('code');
    
    if (workspaceCodeFromUrl) {
        const workspaceCodeInput = document.getElementById('workspace-code');
        workspaceCodeInput.value = workspaceCodeFromUrl.toUpperCase();
        // Scroll to the join form
        joinForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // Highlight the join form temporarily
        const joinCard = joinForm.closest('.card');
        if (joinCard) {
            joinCard.style.boxShadow = '0 0 20px rgba(16, 185, 129, 0.3)';
            setTimeout(() => {
                joinCard.style.boxShadow = '';
            }, 3000);
        }
    }

    // Format workspace code input
    const workspaceCodeInput = document.getElementById('workspace-code');
    workspaceCodeInput.addEventListener('input', function(e) {
        let value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
        e.target.value = value;
    });

    // Handle join workspace form submission
    joinForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const workspaceCode = document.getElementById('workspace-code').value.trim();
        
        if (workspaceCode.length !== 16) {
            showError(joinError, 'Please enter a valid 16-character workspace code');
            return;
        }

        try {
            const response = await fetch('/api/workspace/join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    workspace_code: workspaceCode
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Store workspace info in session and redirect to login
                sessionStorage.setItem('pending_workspace', JSON.stringify(data.workspace));
                window.location.href = '/signin?workspace=' + encodeURIComponent(workspaceCode);
            } else {
                showError(joinError, data.error || 'Failed to join workspace');
            }
        } catch (error) {
            console.error('Error joining workspace:', error);
            showError(joinError, 'Network error. Please try again.');
        }
    });

    // Handle create workspace form submission
    createForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            company_name: document.getElementById('company-name').value.trim(),
            country: document.getElementById('country').value.trim(),
            industry_type: document.getElementById('industry-type').value.trim(),
            company_phone: document.getElementById('company-phone').value.trim(),
            company_email: document.getElementById('company-email').value.trim()
        };

        // Validate form data
        const requiredFields = ['company_name', 'country', 'industry_type', 'company_phone', 'company_email'];
        const missingFields = requiredFields.filter(field => !formData[field]);
        
        if (missingFields.length > 0) {
            showError(createError, `Please fill in all required fields: ${missingFields.join(', ')}`);
            return;
        }

        // Validate email format
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailPattern.test(formData.company_email)) {
            showError(createError, 'Please enter a valid email address');
            return;
        }

        // Validate phone number (basic validation)
        if (formData.company_phone.length < 8) {
            showError(createError, 'Please enter a valid phone number');
            return;
        }

        try {
            const response = await fetch('/api/workspace/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                // Store workspace info and redirect to login
                // Add deferred creation flag for new workspaces
                data.workspace.deferred_creation = true;
                sessionStorage.setItem('pending_workspace', JSON.stringify(data.workspace));
                window.location.href = '/signin?workspace=' + encodeURIComponent(data.workspace.code);
            } else {
                showError(createError, data.error || 'Failed to create workspace');
            }
        } catch (error) {
            console.error('Error creating workspace:', error);
            showError(createError, 'Network error. Please try again.');
        }
    });

    function showError(element, message) {
        element.textContent = message;
        element.classList.remove('hidden');
        setTimeout(() => {
            element.classList.add('hidden');
        }, 5000);
    }

    // Clear errors when user starts typing
    joinForm.addEventListener('input', function() {
        joinError.classList.add('hidden');
    });

    createForm.addEventListener('input', function() {
        createError.classList.add('hidden');
    });
}); 