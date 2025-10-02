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
            
            // Determine workspaceData from pendingWorkspace if available
            // Try to use pendingWorkspace from localStorage
            let workspaceData = null;
            const pending = window.localStorage.getItem('pendingWorkspace');
            if (pending) {
                try {
                    const ws = JSON.parse(pending);
                    if (ws && ws.id) {
                        console.log('Using pendingWorkspace from localStorage:', ws.name);
                        workspaceData = { id: ws.id };
                    }
                } catch (e) {
                    console.error('Invalid pendingWorkspace in localStorage:', e);
                }
            }
            // Fallback: fetch and select first workspace if no pendingWorkspace
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
                if (workspaceData) sessionPayload.workspace_data = workspaceData;
                const response = await fetch('/set_session', {
                    method: 'POST',
                    credentials: 'same-origin',    // include cookies in request
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(sessionPayload)
                });
                if (response.ok) {
                    console.log('Session set successfully, redirecting to home');
                    // Clear pendingWorkspace after successful session creation
                    window.localStorage.removeItem('pendingWorkspace');
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