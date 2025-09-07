import { sendSignInLinkToEmail, signInWithPopup, GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

let runtimeAppSettingsURL = '';

// Function to fetch runtime app settings URL
async function fetchRuntimeAppSettingsURL() {
    try {
        const response = await fetch('/url');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        runtimeAppSettingsURL = data.url || window.location.origin;
        console.log('Runtime app settings URL fetched:', runtimeAppSettingsURL);
    } catch (error) {
        console.warn('Error fetching runtime app settings URL, using fallback:', error);
        // Fallback to current origin
        runtimeAppSettingsURL = window.location.origin;
    }
}

// Wait for Firebase to be initialized
function waitForFirebase() {
    return new Promise((resolve, reject) => {
        // Check if Firebase is already initialized
        if (window.firebaseAuth && window.firebaseInitialized) {
            resolve();
            return;
        }
        
        // Listen for Firebase ready event
        const handleFirebaseReady = () => {
            window.removeEventListener('firebaseReady', handleFirebaseReady);
            if (window.firebaseAuth && window.firebaseInitialized) {
                resolve();
            } else {
                reject(new Error('Firebase failed to initialize'));
            }
        };
        
        window.addEventListener('firebaseReady', handleFirebaseReady);
        
        // Fallback timeout after 5 seconds (reduced from 10)
        setTimeout(() => {
            window.removeEventListener('firebaseReady', handleFirebaseReady);
            if (window.firebaseAuth && window.firebaseInitialized) {
                resolve();
            } else {
                reject(new Error('Firebase initialization timeout'));
            }
        }, 5000);
    });
}

// Initialize the app
async function initializeApp() {
    try {
        // Show loading state
        const googleButton = document.getElementById('google-signin');
        const emailButton = document.querySelector('#signin-form button[type="submit"]');
        
        if (googleButton) {
            googleButton.disabled = true;
            googleButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Initializing...';
        }
        if (emailButton) {
            emailButton.disabled = true;
        }
        
        await fetchRuntimeAppSettingsURL();
        await waitForFirebase();
        
        // Re-enable buttons and restore original text
        if (googleButton) {
            googleButton.disabled = false;
            googleButton.innerHTML = '<i class="fab fa-google mr-2"></i>Sign in with Google';
        }
        if (emailButton) {
            emailButton.disabled = false;
        }
        
        setupEventListeners();
        console.log('App initialized successfully');
    } catch (error) {
        console.error('Error initializing app:', error);
        const errorDiv = document.getElementById('signin-error');
        if (errorDiv) {
            errorDiv.textContent = 'Failed to initialize authentication. Please refresh the page.';
            errorDiv.style.color = 'red';
            errorDiv.style.display = 'block';
        }
        
        // Re-enable buttons even on error so user can retry
        const googleButton = document.getElementById('google-signin');
        const emailButton = document.querySelector('#signin-form button[type="submit"]');
        
        if (googleButton) {
            googleButton.disabled = false;
            googleButton.innerHTML = '<i class="fab fa-google mr-2"></i>Sign in with Google (Retry)';
        }
        if (emailButton) {
            emailButton.disabled = false;
        }
    }
}

function setupEventListeners() {
    const googleButton = document.getElementById('google-signin');
    const provider = new GoogleAuthProvider();

    googleButton.addEventListener('click', () => {
        console.log('Google sign-in button clicked');
        signInWithPopup(window.firebaseAuth, provider)
        .then(async (result) => {
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
                        ...user,
                        workspace_data: workspaceData
                    })
                });
                
                if (sessionResponse.ok) {
                    console.log('Session set successfully, redirecting to home');
                    // Clear workspace data from sessionStorage
                    if (workspaceData) {
                        sessionStorage.removeItem('pending_workspace');
                    }
                    window.location.href = '/home';
                } else {
                    const errorData = await sessionResponse.json();
                    console.error('Failed to set session:', errorData);
                    
                    if (sessionResponse.status === 403 && errorData.error && errorData.error.includes('not authorized')) {
                        alert('Access Denied: You are not authorized to access this workspace. Please make sure your admin has added your email to the workspace team members.');
                    } else {
                        alert('Failed to complete sign-in. Please try again.');
                    }
                }
            } catch (error) {
                console.error('Error setting session:', error);
                alert('Failed to complete sign-in. Please try again.');
            }
        }).catch((error) => {
            console.error('Error during Google sign in:', error.message);
            alert('Sign-in failed: ' + error.message);
        });
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