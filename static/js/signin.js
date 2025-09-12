import { sendSignInLinkToEmail, signInWithPopup, GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

let runtimeAppSettingsURL = '';

// Function to fetch runtime app settings URL
async function fetchRuntimeAppSettingsURL() {
    try {
        const response = await fetch('/url');
        const data = await response.json();
        runtimeAppSettingsURL = data.url;
        console.log('Runtime app settings URL fetched:', runtimeAppSettingsURL);
    } catch (error) {
        console.error('Error fetching runtime app settings URL:', error);
    }
}

// Wait for Firebase to be initialized
function waitForFirebase() {
    return new Promise((resolve, reject) => {
        const checkFirebase = () => {
            if (window.firebaseAuth) {
                resolve();
            } else {
                setTimeout(checkFirebase, 100);
            }
        };
        checkFirebase();
        
        // Timeout after 10 seconds
        setTimeout(() => {
            if (!window.firebaseAuth) {
                reject(new Error('Firebase initialization timeout'));
            }
        }, 10000);
    });
}

// Initialize the app
async function initializeApp() {
    try {
        await fetchRuntimeAppSettingsURL();
        await waitForFirebase();
        setupEventListeners();
    } catch (error) {
        console.error('Error initializing app:', error);
        const errorDiv = document.getElementById('signin-error');
        if (errorDiv) {
            errorDiv.textContent = 'Failed to initialize authentication. Please refresh the page.';
            errorDiv.style.color = 'red';
            errorDiv.style.display = 'block';
        }
    }
}

function setupEventListeners() {
    const googleButton = document.getElementById('google-signin');
    const provider = new GoogleAuthProvider();
    let isSigningIn = false; // Prevent multiple simultaneous sign-in attempts

    googleButton.addEventListener('click', async () => {
        if (isSigningIn) {
            console.log('Sign-in already in progress, ignoring click');
            return;
        }

        console.log('Google sign-in button clicked');
        isSigningIn = true;
        
        // Update button state
        const originalText = googleButton.innerHTML;
        googleButton.disabled = true;
        googleButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Signing in...';
        
        try {
            const result = await signInWithPopup(window.firebaseAuth, provider);
            console.log('Google sign-in successful:', result.user);
            const user = result.user;
            
            // Get workspace info from sessionStorage
            const pendingWorkspace = sessionStorage.getItem('pending_workspace');
            const workspaceData = pendingWorkspace ? JSON.parse(pendingWorkspace) : null;
            
            try {
                const sessionResponse = await fetch('/set_session', {
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
                
                if (sessionResponse.ok) {
                    console.log('Session set successfully');
                    
                    if (workspaceData) {
                        // User has workspace data, clear it and go to home
                        sessionStorage.removeItem('pending_workspace');
                        console.log('Redirecting to home (user has workspace)');
                        window.location.href = '/home';
                    } else {
                        // No workspace data - redirect to workspace selection
                        console.log('Redirecting to workspace selection (no workspace data)');
                        window.location.href = '/workspace-selection';
                    }
                } else {
                    const errorData = await sessionResponse.json();
                    console.error('Failed to set session:', errorData);
                    
                    if (sessionResponse.status === 403 && errorData.error && errorData.error.includes('not authorized')) {
                        alert('Access Denied: You are not authorized to access this workspace. Please make sure your admin has added your email to the workspace team members.');
                    } else {
                        alert('Failed to complete sign-in. Please try again.');
                    }
                    
                    // Reset button state on error
                    isSigningIn = false;
                    googleButton.disabled = false;
                    googleButton.innerHTML = originalText;
                }
            } catch (error) {
                console.error('Error setting session:', error);
                alert('Failed to complete sign-in. Please try again.');
                
                // Reset button state on error
                isSigningIn = false;
                googleButton.disabled = false;
                googleButton.innerHTML = originalText;
            }
        } catch (error) {
            console.error('Error during Google sign in:', error.message);
            
            // Handle specific Firebase errors
            if (error.code === 'auth/cancelled-popup-request') {
                console.log('Sign-in popup was cancelled or another popup was already open');
                // Don't show error for cancelled popups as it's user action
            } else if (error.code === 'auth/popup-blocked') {
                alert('Sign-in popup was blocked by your browser. Please allow popups for this site and try again.');
            } else if (error.code === 'auth/popup-closed-by-user') {
                console.log('Sign-in popup was closed by user');
                // Don't show error for user-closed popups
            } else if (error.code === 'auth/network-request-failed') {
                alert('Network error occurred. Please check your internet connection and try again.');
            } else if (error.message && error.message.includes('certificate')) {
                alert('SSL certificate error. Please make sure you are accessing the site via HTTPS or contact support.');
            } else {
                alert('Sign-in failed: ' + error.message);
            }
            
            // Reset button state
            isSigningIn = false;
            googleButton.disabled = false;
            googleButton.innerHTML = originalText;
        }
    });

    document.getElementById('signin-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('Email sign-in form submitted');
        
        const email = document.getElementById('user-email').value;
        const submitButton = e.target.querySelector('button[type="submit"]');
        const emailNotification = document.getElementById('email-sent-notification');
        const signinError = document.getElementById('signin-error');
        const pendingWorkspace = sessionStorage.getItem('pending_workspace');
        const workspaceData = pendingWorkspace ? JSON.parse(pendingWorkspace) : null;
        
        // Clear any previous errors and hide notification
        signinError.style.display = 'none';
        signinError.textContent = '';
        emailNotification.classList.add('hidden');
        
        // Disable submit button and show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending...';
        
        // Add workspace code to the finish signin URL if available
        let finishUrl = runtimeAppSettingsURL + '/finishSignin?email=' + email;
        if (workspaceData) {
            finishUrl += '&workspace=' + encodeURIComponent(workspaceData.code);
        }
        
        const actionCodeSettings = {
            url: finishUrl,
            handleCodeInApp: true,
        };
        
        try {
            await sendSignInLinkToEmail(window.firebaseAuth, email, actionCodeSettings);
            
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.innerHTML = 'Send Sign-in Link';
            
            // Show success notification with spam folder reminder
            emailNotification.classList.remove('hidden');
            
            // Update the email address in the notification
            const emailText = emailNotification.querySelector('.text-green-700');
            emailText.innerHTML = `We've sent a sign-in link to <strong>${email}</strong>. Click the link in the email to continue.`;
            
            // Scroll to notification
            emailNotification.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            window.localStorage.setItem('emailForSignIn', email);
        } catch (error) {
            console.error('Error sending sign-in link to email:', error);
            
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.innerHTML = 'Send Sign-in Link';
            
            // Show error message
            signinError.innerHTML = 'Error sending sign-in link. Please try again.';
            signinError.style.color = 'red';
            signinError.style.display = 'block';
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);