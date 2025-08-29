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
fetchRuntimeAppSettingsURL();

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
    const pendingWorkspace = sessionStorage.getItem('pending_workspace');
    const workspaceData = pendingWorkspace ? JSON.parse(pendingWorkspace) : null;
    
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
        alert('Sign-in link sent! Check your email.');
        window.localStorage.setItem('emailForSignIn', email);
    } catch (error) {
        console.error('Error sending sign-in link to email:', error);
        document.getElementById('signin-error').innerHTML = 'Error sending sign-in link. Please try again.';
        document.getElementById('signin-error').style.color = 'red';
    }
});

// Removed email/password login logic