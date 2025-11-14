import { isSignInWithEmailLink, signInWithEmailLink } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Modern notification functions
function showCustomModal(title, message, type = 'info') {
    return new Promise((resolve) => {
        const modal = document.createElement('dialog');
        modal.className = 'modal';
        modal.style.zIndex = '10000';
        
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

// Workspace selection modal
function showWorkspaceSelectionModal(workspaces) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
        modal.style.fontFamily = 'Inter, sans-serif';
        
        const gradientPrimary = 'background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);';
        
        modal.innerHTML = `
            <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
                <div style="${gradientPrimary}" class="p-6">
                    <h2 class="text-2xl font-bold text-white flex items-center gap-2">
                        <i class="fas fa-briefcase"></i>
                        Select Your Workspace
                    </h2>
                    <p class="text-blue-100 mt-2">Choose a workspace to continue</p>
                </div>
                <div class="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
                    <div class="grid gap-4">
                        ${workspaces.map(ws => `
                            <button class="workspace-card text-left p-4 border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-lg transition-all duration-200 group" data-workspace='${JSON.stringify(ws)}'>
                                <div class="flex items-start justify-between">
                                    <div class="flex-1">
                                        <h3 class="text-lg font-bold text-gray-800 group-hover:text-blue-600 mb-1">${ws.name}</h3>
                                        <div class="space-y-1">
                                            <p class="text-sm text-gray-600 flex items-center gap-2">
                                                <i class="fas fa-map-marker-alt text-gray-400"></i>
                                                ${ws.country || 'N/A'}
                                            </p>
                                            <p class="text-sm text-gray-600 flex items-center gap-2">
                                                <i class="fas fa-building text-gray-400"></i>
                                                ${ws.industry || 'N/A'}
                                            </p>
                                            <p class="text-sm text-gray-600 flex items-center gap-2">
                                                <i class="fas fa-code text-gray-400"></i>
                                                Code: <span class="font-mono font-semibold">${ws.code}</span>
                                            </p>
                                        </div>
                                    </div>
                                    <div class="ml-4">
                                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                                            ws.role === 'Admin' ? 'bg-purple-100 text-purple-800' :
                                            ws.role === 'Accountant' ? 'bg-blue-100 text-blue-800' :
                                            'bg-green-100 text-green-800'
                                        }">
                                            ${ws.role}
                                        </span>
                                    </div>
                                </div>
                            </button>
                        `).join('')}
                    </div>
                </div>
                <div class="p-6 border-t border-gray-200 bg-gray-50">
                    <button id="cancel-workspace-selection" class="w-full py-3 px-4 border-2 border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-100 transition">
                        Cancel
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add click handlers for workspace cards
        modal.querySelectorAll('.workspace-card').forEach(card => {
            card.addEventListener('click', function() {
                const workspace = JSON.parse(this.dataset.workspace);
                modal.remove();
                resolve(workspace);
            });
        });
        
        // Cancel button
        modal.querySelector('#cancel-workspace-selection').addEventListener('click', () => {
            modal.remove();
            resolve(null);
        });
    });
}

// Wait for Firebase to be initialized
document.addEventListener('DOMContentLoaded', function() {
    console.log('FinishSignIn page loaded');
    
    // Check if Firebase is available
    if (typeof window.firebaseAuth === 'undefined') {
        console.error('Firebase Auth not initialized');
        showCustomModal('Authentication Error', 'Authentication service not available. Please try again.', 'error');
        return;
    }

    if (isSignInWithEmailLink(window.firebaseAuth, window.location.href)) {
        let email = window.localStorage.getItem('emailForSignIn');
        if (!email) {
            email = window.prompt('Please provide your email for confirmation');
        }
        console.log('Attempting to sign in with email link...');
        signInWithEmailLink(window.firebaseAuth, email, window.location.href)
        .then(async (result) => {
            console.log('Email link sign-in successful');
            window.localStorage.removeItem('emailForSignIn');
            const user = result.user;
            console.log('User data:', user);
            
            // Extract workspace code from URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const workspaceCodeFromUrl = urlParams.get('workspace');
            console.log('Workspace code from URL:', workspaceCodeFromUrl);
            
            // Determine workspaceData from URL parameter or sessionStorage/localStorage
            let workspaceData = null;
            
            if (workspaceCodeFromUrl) {
                console.log('Found workspace code in URL:', workspaceCodeFromUrl);
                // Fetch workspace details by code
                try {
                    const joinResponse = await fetch('/api/workspace/join', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ workspace_code: workspaceCodeFromUrl })
                    });
                    
                    if (joinResponse.ok) {
                        const joinData = await joinResponse.json();
                        if (joinData.success && joinData.workspace) {
                            console.log('Successfully fetched workspace from URL:', joinData.workspace.name);
                            workspaceData = joinData.workspace;
                        }
                    }
                } catch (e) {
                    console.error('Error fetching workspace from URL code:', e);
                }
            }
            
            // If no workspace from URL, try sessionStorage
            if (!workspaceData) {
                const pendingSession = window.sessionStorage.getItem('pending_workspace');
                if (pendingSession) {
                    try {
                        const ws = JSON.parse(pendingSession);
                        if (ws && ws.id) {
                            console.log('Using pending_workspace from sessionStorage:', ws.name);
                            workspaceData = ws;
                        }
                    } catch (e) {
                        console.error('Invalid pending_workspace in sessionStorage:', e);
                    }
                }
            }
            
            // Fallback: Try localStorage (for backward compatibility)
            if (!workspaceData) {
                const pending = window.localStorage.getItem('pendingWorkspace');
                if (pending) {
                    try {
                        const ws = JSON.parse(pending);
                        if (ws && ws.id) {
                            console.log('Using pendingWorkspace from localStorage:', ws.name);
                            workspaceData = ws;
                        }
                    } catch (e) {
                        console.error('Invalid pendingWorkspace in localStorage:', e);
                    }
                }
            }
            
            // Final fallback: fetch workspaces and let user select
            if (!workspaceData) {
                try {
                    const workspacesResponse = await fetch('/api/user/workspaces', {
                        method: 'POST',
                        credentials: 'same-origin',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: user.email })
                    });
                    if (workspacesResponse.ok) {
                        const workspacesJson = await workspacesResponse.json();
                        if (workspacesJson.success && workspacesJson.workspaces.length > 0) {
                            // Show workspace selection modal
                            const selectedWorkspace = await showWorkspaceSelectionModal(workspacesJson.workspaces);
                            if (selectedWorkspace) {
                                workspaceData = selectedWorkspace;
                                console.log('User selected workspace:', selectedWorkspace.name);
                            } else {
                                // User cancelled selection
                                showCustomModal('Selection Required', 'Please select a workspace to continue.', 'warning');
                                return;
                            }
                        }
                    }
                } catch (err) {
                    console.error('Error fetching user workspaces:', err);
                }
            }
            
            // Set session on server including workspaceData if any
            try {
                const sessionPayload = {
                    email: user.email,
                    displayName: user.displayName || '',
                    photoURL: user.photoURL || '',
                    uid: user.uid
                };
                if (workspaceData) {
                    console.log('Setting session with workspace data:', workspaceData.name || workspaceData.id);
                    sessionPayload.workspace_data = workspaceData;
                }
                const response = await fetch('/set_session', {
                    method: 'POST',
                    credentials: 'same-origin',    // include cookies in request
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(sessionPayload)
                });
                if (response.ok) {
                    console.log('Session set successfully');
                    // Clear all pending workspace storage after successful session creation
                    window.localStorage.removeItem('pendingWorkspace');
                    window.sessionStorage.removeItem('pending_workspace');
                    
                    console.log('Redirecting to home');
                    window.location.href = '/home';
                } else {
                    const errorData = await response.json();
                    console.error('Failed to set session:', errorData);
                    showCustomModal('Sign-in Error', 'Failed to complete sign-in: ' + (errorData.error || 'Please try again.'), 'error');
                }
            } catch (error) {
                console.error('Error setting session:', error);
                showCustomModal('Sign-in Error', 'Failed to complete sign-in: ' + error.message, 'error');
            }
        })
        .catch((error) => {
            console.error('Error signing in with email link:', error);
            showCustomModal('Sign-in Failed', 'Sign-in failed: ' + error.message, 'error');
        });
    } else {
        console.log('Not a valid email sign-in link');
        // Redirect to signin page if not a valid email link
        window.location.href = '/signin';
    }
});

// Add global error handling
window.addEventListener('error', function(e) {
    console.error('Global error in finishSignIn:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection in finishSignIn:', e.reason);
});