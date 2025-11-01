import { sendSignInLinkToEmail, signInWithPopup, GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

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

// Helper to handle a signed-in user (popup or redirect)
async function processSignIn(user) {
    try {
        const pendingWorkspace = sessionStorage.getItem('pending_workspace');
        const workspaceData = pendingWorkspace ? JSON.parse(pendingWorkspace) : null;
        const response = await fetch('/set_session', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                email: user.email,
                displayName: user.displayName || '',
                photoURL: user.photoURL || '',
                uid: user.uid,
                workspace_data: workspaceData
            })
        });
        if (response.ok) {
            if (workspaceData) {
                sessionStorage.removeItem('pending_workspace');
                window.location.href = '/home';
            } else {
                window.location.href = '/workspace-selection';
            }
        } else {
            const err = await response.json();
            console.error('Session set error', err);
            showCustomModal('Sign-in Error', 'Failed to complete sign-in.', 'error');
        }
    } catch(e) {
        console.error('Error setting session', e);
        showCustomModal('Sign-in Error', 'Failed to complete sign-in.', 'error');
    }
}

function setupEventListeners() {
    const googleButton = document.getElementById('google-signin');
    const provider = new GoogleAuthProvider();
    let isSigningIn = false; // Prevent multiple simultaneous sign-in attempts

    googleButton.addEventListener('click', async () => {
        console.log('Google sign-in button clicked');
        const originalText = googleButton.innerHTML;
        googleButton.disabled = true;
        googleButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Signing in...';
        try {
            const result = await signInWithPopup(window.firebaseAuth, provider);
            console.log('Google sign-in successful:', result.user);
            const user = result.user;
            const pendingWorkspace = sessionStorage.getItem('pending_workspace');
            const workspaceData = pendingWorkspace ? JSON.parse(pendingWorkspace) : null;

            try {
                const sessionResponse = await fetch('/set_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
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
                        sessionStorage.removeItem('pending_workspace');
                        window.location.href = '/home';
                    } else {
                        window.location.href = '/workspace-selection?signed_in=true&email=' + encodeURIComponent(user.email);
                    }
                } else {
                    const errorData = await sessionResponse.json();
                    console.error('Failed to set session:', errorData);
                    if (sessionResponse.status === 403 && errorData.error && errorData.error.includes('not authorized')) {
                        showCustomModal('Access Denied', 'You are not authorized to access this workspace. Please make sure your admin has added your email to the workspace team members.', 'error');
                    } else {
                        showCustomModal('Sign-in Error', 'Failed to complete sign-in. Please try again.', 'error');
                    }
                    googleButton.disabled = false;
                    googleButton.innerHTML = originalText;
                }
            } catch (innerError) {
                console.error('Error setting session:', innerError);
                showCustomModal('Sign-in Error', 'Failed to complete sign-in. Please try again.', 'error');
                googleButton.disabled = false;
                googleButton.innerHTML = originalText;
            }
        } catch (error) {
            console.error('Error during Google sign in:', error.message);
            showCustomModal('Sign-in Failed', 'Sign-in failed: ' + error.message, 'error');
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
        } else {
            // If coming from forgot_workspace flow, indicate that to finishSignin
            finishUrl += '&from=forgot-workspace';
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