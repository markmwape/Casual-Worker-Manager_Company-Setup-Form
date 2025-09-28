import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Fetch Firebase config from the server
async function getFirebaseConfig() {
  try {
    const response = await fetch('/firebase_config');
    return await response.json();
  } catch (error) {
    console.error('Error fetching Firebase config:', error);
    // Fallback configuration
    return {
      apiKey: "AIzaSyD9_N_0ve9ABFwwnTBn1N2oxlUs6xbT-No",
      authDomain: "ember-accounting.firebaseapp.com",
      projectId: "ember-accounting",
      storageBucket: "ember-accounting.firebasestorage.app",
      messagingSenderId: "328324461979",
      appId: "1:328324461979:web:0cc9ddad6aa3f157359d3e",
      measurementId: "G-F1XTE0TP63"
    };
  }
}

// Initialize Firebase
async function initFirebase() {
  try {
    const firebaseConfig = await getFirebaseConfig();
    console.log('Firebase config loaded:', firebaseConfig);
    
    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);
    
    // Make auth available globally
    window.firebaseAuth = auth;
    window.firebaseApp = app;
    
    console.log('Firebase initialized successfully');
    return auth;
  } catch (error) {
    console.error('Error initializing Firebase:', error);
    throw error;
  }
}

// Initialize Firebase when the script loads
initFirebase().catch(error => {
  console.error('Failed to initialize Firebase:', error);
}); 