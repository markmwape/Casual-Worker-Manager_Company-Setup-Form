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
            
            // Get workspace data from URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const workspaceCode = urlParams.get('workspace');
            const fromForgotWorkspace = urlParams.get('from') === 'forgot-workspace';
            const pendingWorkspace = sessionStorage.getItem('pending_workspace');
            const workspaceData = pendingWorkspace ? JSON.parse(pendingWorkspace) : null;
            
            // Send user data to backend
            try {
                const response = await fetch('/set_session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email: user.email,
                        displayName: user.displayName || '',
                        photoURL: user.photoURL || '',
                        uid: user.uid,
                        workspace_data: workspaceData
                    })
                });
                
                if (response.ok) {
                    console.log('Session set successfully');
                    
                    // Check if this is from forgot workspace page
                    if (fromForgotWorkspace) {
                        console.log('User came from forgot workspace, redirecting back with workspaces');
                        // Redirect back to forgot workspace page to show workspaces
                        window.location.href = '/forgot-workspace?signed_in=true&email=' + encodeURIComponent(user.email);
                        return;
                    }
                    
                    if (workspaceData) {
                        // User has workspace data, clear it and go to home
                        sessionStorage.removeItem('pending_workspace');
                        console.log('Redirecting to home (user has workspace)');
                        window.location.href = '/home';
                    } else {
                        // No workspace data - check if user has workspaces and auto-select
                        console.log('No workspace data, checking user workspaces...');
                        
                        try {
                            const workspacesResponse = await fetch('/api/user/workspaces', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({ email: user.email })
                            });
                            
                            if (workspacesResponse.ok) {
                                const workspacesData = await workspacesResponse.json();
                                
                                if (workspacesData.success && workspacesData.workspaces && workspacesData.workspaces.length > 0) {
                                    if (workspacesData.workspaces.length === 1) {
                                        // User has exactly one workspace, auto-select it
                                        const workspace = workspacesData.workspaces[0];
                                        console.log('Auto-selecting single workspace:', workspace.name);
                                        
                                        const selectResponse = await fetch('/api/workspace/join', {
                                            method: 'POST',
                                            headers: {
                                                'Content-Type': 'application/json'
                                            },
                                            body: JSON.stringify({
                                                workspace_code: workspace.code
                                            })
                                        });
                                        
                                        if (selectResponse.ok) {
                                            const selectData = await selectResponse.json();
                                            console.log('Workspace join response:', selectData);
                                            
                                            // Set session with the workspace
                                            const sessionResponse2 = await fetch('/set_session', {
                                                method: 'POST',
                                                headers: {
                                                    'Content-Type': 'application/json'
                                                },
                                                body: JSON.stringify({
                                                    email: user.email,
                                                    displayName: user.displayName || '',
                                                    photoURL: user.photoURL || '',
                                                    uid: user.uid,
                                                    workspace_data: selectData.workspace
                                                })
                                            });
                                            
                                            console.log('Second session response status:', sessionResponse2.status);
                                            if (sessionResponse2.ok) {
                                                const sessionResult = await sessionResponse2.json();
                                                console.log('Second session response:', sessionResult);
                                                console.log('Auto-selected workspace successfully, redirecting to home');
                                                window.location.href = '/home';
                                                return;
                                            } else {
                                                const sessionError = await sessionResponse2.json();
                                                console.error('Second session failed:', sessionError);
                                                // Fallback to workspace selection
                                                window.location.href = '/workspace-selection';
                                                return;
                                            }
                                        }
                                    } else {
                                        // User has multiple workspaces, show workspace selection
                                        console.log(`User has ${workspacesData.workspaces.length} workspaces, redirecting to workspace selection`);
                                        window.location.href = '/workspace-selection';
                                        return;
                                    }
                                }
                            }
                        } catch (error) {
                            console.error('Error checking user workspaces:', error);
                        }
                        
                        // Fallback: redirect to workspace selection (no workspaces found or error)
                        console.log('No workspaces found or error occurred, redirecting to workspace selection');
                        window.location.href = '/workspace-selection';
                    }
                } else {
                    const errorData = await response.json();
                    console.error('Failed to set session:', errorData);
                    
                    if (response.status === 403 && errorData.error && errorData.error.includes('not authorized')) {
                        alert('Access Denied: You are not authorized to access this workspace. Please make sure your admin has added your email to the workspace team members.');
                    } else {
                        alert('Failed to complete sign-in. Please try again.');
                    }
                }
            } catch (error) {
                console.error('Error setting session:', error);
                alert('Failed to complete sign-in. Please try again.');
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