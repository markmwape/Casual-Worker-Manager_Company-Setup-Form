// Payments Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadPaymentInfo();
});

async function loadPaymentInfo() {
    try {
        const response = await fetch('/api/workspace/payments');
        const data = await response.json();
        
        if (response.ok) {
            displayPaymentInfo(data.workspace);
        } else {
            console.error('Failed to load payment info:', data.error);
            showError('Failed to load payment information');
        }
    } catch (error) {
        console.error('Error loading payment info:', error);
        showError('Network error. Please try again.');
    }
}

function displayPaymentInfo(workspace) {
    // Update workspace info
    document.getElementById('workspace-name').textContent = workspace.name;
    document.getElementById('workspace-code').textContent = `Code: ${workspace.code}`;
    document.getElementById('workspace-code-display').value = workspace.code;
    
    // Update subscription status
    const statusElement = document.getElementById('subscription-status');
    statusElement.textContent = workspace.subscription_status === 'trial' ? 'Trial' : 'Active';
    statusElement.className = workspace.subscription_status === 'trial' ? 'badge badge-info' : 'badge badge-success';
    
    // Show appropriate sections based on status
    if (workspace.subscription_status === 'trial') {
        showTrialStatus(workspace);
        document.getElementById('upgrade-section').classList.remove('hidden');
        document.getElementById('manage-subscription').classList.add('hidden');
        document.getElementById('cancel-section').classList.add('hidden');
    } else {
        showSubscriptionStatus(workspace);
        document.getElementById('upgrade-section').classList.add('hidden');
        document.getElementById('manage-subscription').classList.remove('hidden');
        document.getElementById('cancel-section').classList.remove('hidden');
    }
}

function showTrialStatus(workspace) {
    const trialStatus = document.getElementById('trial-status');
    const trialDaysLeft = document.getElementById('trial-days-left');
    
    if (workspace.is_trial_active) {
        trialDaysLeft.textContent = `${workspace.trial_days_left} days remaining in your free trial`;
        trialStatus.classList.remove('hidden');
        document.getElementById('subscription-status-details').classList.add('hidden');
    } else {
        trialDaysLeft.textContent = 'Your free trial has expired. Please upgrade to continue.';
        trialStatus.classList.remove('hidden');
        document.getElementById('subscription-status-details').classList.add('hidden');
    }
}

function showSubscriptionStatus(workspace) {
    document.getElementById('trial-status').classList.add('hidden');
    document.getElementById('subscription-status-details').classList.remove('hidden');
}

function upgradePlan() {
    // TODO: Implement Stripe checkout
    alert('Upgrade functionality will be implemented with Stripe integration');
}

function manageSubscription() {
    // TODO: Implement subscription management
    alert('Subscription management will be implemented with Stripe integration');
}

function cancelSubscription() {
    if (confirm('Are you sure you want to cancel your subscription? You will lose access to premium features at the end of your billing period.')) {
        // TODO: Implement subscription cancellation
        alert('Subscription cancellation will be implemented with Stripe integration');
    }
}

function copyWorkspaceCode() {
    const codeInput = document.getElementById('workspace-code-display');
    codeInput.select();
    codeInput.setSelectionRange(0, 99999); // For mobile devices
    
    try {
        document.execCommand('copy');
        showSuccess('Workspace code copied to clipboard!');
    } catch (err) {
        console.error('Failed to copy: ', err);
        showError('Failed to copy workspace code');
    }
}

function showSuccess(message) {
    // Create a modern success notification
    const notificationDiv = document.createElement('div');
    notificationDiv.className = 'fixed top-4 right-4 z-50 transform transition-all duration-300 ease-in-out translate-x-full';
    notificationDiv.innerHTML = `
        <div class="bg-white border-l-4 border-green-500 shadow-lg rounded-lg p-4 max-w-sm">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                        <i class="fas fa-check text-green-600 text-sm"></i>
                    </div>
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium text-gray-900">${message}</p>
                </div>
                <div class="ml-auto pl-3">
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times text-sm"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(notificationDiv);
    
    // Animate in
    setTimeout(() => {
        notificationDiv.classList.remove('translate-x-full');
    }, 100);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notificationDiv.classList.add('translate-x-full');
        setTimeout(() => {
            notificationDiv.remove();
        }, 300);
    }, 4000);
}

function showError(message) {
    // Create a modern error notification
    const notificationDiv = document.createElement('div');
    notificationDiv.className = 'fixed top-4 right-4 z-50 transform transition-all duration-300 ease-in-out translate-x-full';
    notificationDiv.innerHTML = `
        <div class="bg-white border-l-4 border-red-500 shadow-lg rounded-lg p-4 max-w-sm">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                        <i class="fas fa-exclamation-triangle text-red-600 text-sm"></i>
                    </div>
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium text-gray-900">${message}</p>
                </div>
                <div class="ml-auto pl-3">
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times text-sm"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(notificationDiv);
    
    // Animate in
    setTimeout(() => {
        notificationDiv.classList.remove('translate-x-full');
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notificationDiv.classList.add('translate-x-full');
        setTimeout(() => {
            notificationDiv.remove();
        }, 300);
    }, 5000);
} 