/**
 * Multi-language Translation System
 * Load and manage translations for the application
 */

let translationsCache = {};
let currentLanguage = 'en';

/**
 * Initialize the translation system
 */
async function initializeTranslations() {
    try {
        // Get current language preference
        const langResponse = await fetch('/api/languages');
        const langData = await langResponse.json();
        currentLanguage = langData.current_language || 'en';
        
        // Load translations for the current language
        if (currentLanguage !== 'en') {
            await loadTranslations(currentLanguage);
        }
    } catch (error) {
        console.warn('Error initializing translations:', error);
        currentLanguage = 'en';
    }
}

/**
 * Load translation file for a specific language
 */
async function loadTranslations(languageCode) {
    try {
        const response = await fetch(`/static/translations/${languageCode}.json`);
        if (response.ok) {
            translationsCache[languageCode] = await response.json();
        }
    } catch (error) {
        console.warn(`Error loading translations for ${languageCode}:`, error);
    }
}

/**
 * Get translated text
 * @param {string} text - English text to translate
 * @returns {string} Translated text or original text if translation not found
 */
function t(text) {
    if (currentLanguage === 'en' || !translationsCache[currentLanguage]) {
        return text;
    }
    
    return translationsCache[currentLanguage][text] || text;
}

/**
 * Translate all elements with data-i18n attribute
 */
function translatePage() {
    const elements = document.querySelectorAll('[data-i18n]');
    
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translated = t(key);
        
        // Handle different element types
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            if (element.placeholder) {
                element.setAttribute('placeholder', translated);
            }
        } else {
            element.textContent = translated;
        }
    });
}

/**
 * Change the current language and reload translations
 */
async function setLanguage(languageCode) {
    currentLanguage = languageCode;
    
    if (languageCode !== 'en') {
        await loadTranslations(languageCode);
    }
    
    translatePage();
}

// Initialize translations when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTranslations);
} else {
    initializeTranslations();
}

// Export for use in other scripts
window.i18n = {
    t,
    translatePage,
    setLanguage,
    initializeTranslations,
    currentLanguage: () => currentLanguage
};
