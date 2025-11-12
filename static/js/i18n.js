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
        // Always load English as the base
        await loadTranslations('en');
        
        // Get current language preference from API
        const langResponse = await fetch('/api/languages');
        const langData = await langResponse.json();
        currentLanguage = langData.current_language || 'en';
        
        console.log('🌍 Current language from API:', currentLanguage);
        
        // Load translations for the current language if not English
        if (currentLanguage !== 'en') {
            await loadTranslations(currentLanguage);
        }
        
        // Apply translations to page
        translatePage();
        
        // Update language switcher UI to reflect current language
        updateLanguageSwitcherUI(currentLanguage);
        
        console.log('✅ Translations initialized for language:', currentLanguage);
    } catch (error) {
        console.warn('Error initializing translations:', error);
        currentLanguage = 'en';
    }
}

/**
 * Update the language switcher UI to show current language
 */
function updateLanguageSwitcherUI(languageCode) {
    const languageNames = {
        'en': 'English',
        'fr': 'Français',
        'sw': 'Swahili',
        'pt': 'Português',
        'es': 'Español',
        'tr': 'Türkçe',
        'hi': 'हिंदी',
        'zh': '中文',
        'ar': 'العربية',
        'vi': 'Tiếng Việt'
    };
    
    // Update all language switcher buttons
    const buttons = document.querySelectorAll('.language-switcher-btn, .dropdown-toggle, .current-lang-label, .current-lang-display');
    buttons.forEach(btn => {
        const displayName = languageNames[languageCode] || languageCode.toUpperCase();
        if (btn.classList.contains('current-lang-label') || btn.classList.contains('current-lang-display')) {
            btn.textContent = displayName;
        } else {
            // Update button text if it shows language
            const textElement = btn.querySelector('span') || btn;
            if (textElement.textContent && textElement.textContent.trim()) {
                textElement.textContent = displayName;
            }
        }
    });
    
    console.log(`🌍 Updated language switcher UI to: ${languageCode}`);
}

/**
 * Load translation file for a specific language
 */
async function loadTranslations(languageCode) {
    try {
        if (translationsCache[languageCode]) {
            console.log(`Translations for ${languageCode} already cached`);
            return;
        }
        
        const response = await fetch(`/static/translations/${languageCode}.json`);
        if (response.ok) {
            const translations = await response.json();
            translationsCache[languageCode] = translations;
            console.log(`Loaded translations for ${languageCode}:`, Object.keys(translations).length, 'keys');
        } else {
            console.warn(`Failed to load translations for ${languageCode}: ${response.status}`);
        }
    } catch (error) {
        console.warn(`Error loading translations for ${languageCode}:`, error);
    }
}

/**
 * Get translated text by key path (supports nested keys like "sidebar.dashboard")
 * @param {string} keyPath - Translation key path (e.g., "sidebar.dashboard")
 * @returns {string} Translated text or original key if translation not found
 */
function t(keyPath) {
    if (currentLanguage === 'en' || !translationsCache[currentLanguage]) {
        // For English, try to find the key in the EN file, otherwise return the key itself
        if (translationsCache['en']) {
            return getNestedValue(translationsCache['en'], keyPath) || keyPath;
        }
        return keyPath;
    }
    
    // Try to get the translation from the current language
    const translation = getNestedValue(translationsCache[currentLanguage], keyPath);
    if (translation) {
        return translation;
    }
    
    // Fallback to English if available
    if (translationsCache['en']) {
        return getNestedValue(translationsCache['en'], keyPath) || keyPath;
    }
    
    return keyPath;
}

/**
 * Get value from nested object using dot notation
 * @param {object} obj - Object to search in
 * @param {string} path - Dot-separated path (e.g., "sidebar.dashboard")
 * @returns {string|null} Value if found, null otherwise
 */
function getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
        return current && current[key] !== undefined ? current[key] : null;
    }, obj);
}

/**
 * Translate all elements with data-i18n attribute
 */
function translatePage() {
    // Translate text content
    const elements = document.querySelectorAll('[data-i18n]');
    console.log(`Found ${elements.length} elements with data-i18n attribute for language: ${currentLanguage}`);
    
    let translatedCount = 0;
    elements.forEach(element => {
        const keyPath = element.getAttribute('data-i18n');
        const translated = t(keyPath);
        
        console.log(`Translating key: ${keyPath} -> ${translated}`);
        
        if (translated !== keyPath) {
            translatedCount++;
        }
        
        // Handle different element types
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            if (element.hasAttribute('placeholder')) {
                element.setAttribute('placeholder', translated);
            } else {
                element.value = translated;
            }
        } else if (element.tagName === 'OPTION') {
            // For option elements, update the text content
            element.textContent = translated;
        } else {
            element.textContent = translated;
        }
    });
    
    // Translate placeholder attributes
    const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
    console.log(`Found ${placeholderElements.length} elements with data-i18n-placeholder attribute`);
    
    placeholderElements.forEach(element => {
        const keyPath = element.getAttribute('data-i18n-placeholder');
        const translated = t(keyPath);
        
        console.log(`Translating placeholder key: ${keyPath} -> ${translated}`);
        
        if (translated !== keyPath) {
            translatedCount++;
        }
        
        element.setAttribute('placeholder', translated);
    });
    
    console.log(`Translated ${translatedCount} elements to ${currentLanguage}`);
}

/**
 * Change the current language and reload translations
 */
async function setLanguage(languageCode) {
    console.log('🔄 setLanguage called, updating to:', languageCode);
    
    currentLanguage = languageCode;
    
    if (languageCode !== 'en') {
        await loadTranslations(languageCode);
    }
    
    // Update UI
    updateLanguageSwitcherUI(languageCode);
    
    // Translate all page elements
    translatePage();
    
    console.log('✅ Language updated to:', languageCode);
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
