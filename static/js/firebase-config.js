/* This file is intended for client-side Firebase SDK usage. */
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

let app=null;
let auth=null;

// Fetch the Firebase configuration from the backend
async function fetchFirebaseConfig() {
  try {
    const response = await fetch('/firebase_config');
    const firebaseConfig = await response.json();
    // Initialize Firebase with the retrieved configuration
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    // Enable the Google sign-in button once Firebase is initialized
    document.getElementById('google-signin').disabled = false;
  } catch (error) {
    console.error('Error fetching Firebase configuration:', error);
  }
}
// Initially disable the Google sign-in button until Firebase is initialized
document.getElementById('google-signin').disabled = true;
fetchFirebaseConfig();

export { app, auth };