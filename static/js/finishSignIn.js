import { isSignInWithEmailLink, signInWithEmailLink } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Wait for Firebase to be initialized
document.addEventListener('DOMContentLoaded', function() {
    console.log('FinishSignIn page loaded');
    
    // Check if Firebase is available
    if (typeof window.firebaseAuth === 'undefined') {
        console.error('Firebase Auth not initialized');
        alert('Authentication service not available. Please try again.');
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
            
            // Determine workspaceData from URL parameter or sessionStorage/localStorage
            let workspaceData = null;
            
            // First, try to get workspace code from URL parameter
            const urlParams = new URLSearchParams(window.location.search);
            const workspaceCodeFromUrl = urlParams.get('workspace');
            
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
            
            // Final fallback: fetch and select first workspace if no pendingWorkspace
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
                            const ws = workspacesJson.workspaces[0];
                            console.log('Auto-selecting workspace:', ws.name);
                            workspaceData = { id: ws.id };
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
                    console.log('Session set successfully, redirecting to home');
                    // Clear all pending workspace storage after successful session creation
                    window.localStorage.removeItem('pendingWorkspace');
                    window.sessionStorage.removeItem('pending_workspace');
                    window.location.href = '/home';
                } else {
                    const errorData = await response.json();
                    console.error('Failed to set session:', errorData);
                    alert('Failed to complete sign-in: ' + (errorData.error || 'Please try again.'));
                }
            } catch (error) {
                console.error('Error setting session:', error);
                alert('Failed to complete sign-in: ' + error.message);
            }
        })
        .catch((error) => {
            console.error('Error signing in with email link:', error);
            alert('Sign-in failed: ' + error.message);
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