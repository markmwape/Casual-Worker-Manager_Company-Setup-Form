// This script fetches runtime app settings and exports them for use in other scripts
let runtime_app_settings = {};

async function fetchRuntimeAppSettings() {
    try {
        const response = await fetch('/runtime-app-settings-url');
        runtime_app_settings = await response.json();
    } catch (error) {
        console.error('Error fetching runtime app settings:', error);
    }
}

fetchRuntimeAppSettings();

export { runtime_app_settings };