/**
 * Language Switcher - Optimized External JavaScript
 * Handles language selection and UI updates efficiently
 */

// Cache for avoiding repeated API calls
let languagesCache = null;
let initializationInProgress = false;

/**
 * Initialize language switcher - called once on page load
 */
function initLanguageSwitcher() {
    // Prevent multiple simultaneous initializations
    if (initializationInProgress) {
        console.log('Language switcher initialization already in progress');
        return;
    }
    
    initializationInProgress = true;
    
    try {
        console.log('Initializing language switcher...');
        
        // Fetch available languages with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
        
        fetch('/api/languages', { signal: controller.signal })
            .then(response => {
                clearTimeout(timeoutId);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                languagesCache = data; // Cache the response
                populateLanguageMenus(data);
                initializationInProgress = false;
            })
            .catch(error => {
                clearTimeout(timeoutId);
                console.error('Error loading languages:', error);
                
                // Use fallback data
                const fallbackData = {
                    languages: {
                        'en': 'English',
                        'fr': 'Français',
                        'es': 'Español',
                        'pt': 'Português',
                        'sw': 'Swahili'
                    },
                    current_language: 'en'
                };
                
                languagesCache = fallbackData;
                populateLanguageMenus(fallbackData);
                initializationInProgress = false;
            });
    } catch (error) {
        console.error('Error initializing language switcher:', error);
        initializationInProgress = false;
    }
}

/**
 * Populate all language menus on the page
 */
function populateLanguageMenus(data) {
    const languages = data.languages || {};
    const currentLanguage = data.current_language || 'en';
    
    const languageMenus = document.querySelectorAll('.language-menu');
    
    languageMenus.forEach((menu, index) => {
        menu.innerHTML = ''; // Clear existing
        
        // Sort alphabetically
        const sorted = Object.entries(languages).sort((a, b) => a[1].localeCompare(b[1]));
        
        sorted.forEach(([code, name]) => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            
            a.textContent = name;
            a.href = 'javascript:void(0)';
            a.setAttribute('data-lang', code);
            a.className = code === currentLanguage ? 'active' : '';
            
            a.onclick = function(e) {
                e.preventDefault();
                changeLanguage(code);
            };
            
            li.appendChild(a);
            menu.appendChild(li);
        });
        
        console.log(`Menu ${index + 1} populated with ${sorted.length} languages`);
    });
    
    // Update current language labels
    const labels = document.querySelectorAll('.current-lang-label');
    labels.forEach(label => {
        label.textContent = languages[currentLanguage] || 'English';
    });
}

/**
 * Change language with proper feedback
 */
function changeLanguage(langCode) {
    console.log('Changing to:', langCode);
    
    const buttons = document.querySelectorAll('.language-switcher-btn');
    const labels = document.querySelectorAll('.current-lang-label');
    
    // Show loading
    buttons.forEach(btn => btn.classList.add('loading'));
    labels.forEach(label => label.textContent = '⏳');
    
    // Close dropdowns
    document.querySelectorAll('.language-menu').forEach(menu => {
        menu.classList.remove('opacity-100', 'visible');
        menu.classList.add('opacity-0', 'invisible');
    });
    
    fetch('/api/change-language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: langCode })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            // Success feedback
            buttons.forEach(btn => {
                btn.classList.remove('loading');
                btn.classList.add('success');
            });
            
            const langNames = {
                'en': 'English', 'fr': 'Français', 'sw': 'Swahili',
                'pt': 'Português', 'es': 'Español', 'tr': 'Türkçe',
                'hi': 'हिंदी', 'zh': '中文', 'ar': 'العربية', 'vi': 'Tiếng Việt'
            };
            
            labels.forEach(label => {
                label.textContent = langNames[langCode] || langCode.toUpperCase();
            });
            
            // Reload after short delay
            setTimeout(() => window.location.reload(), 500);
        } else {
            throw new Error(result.message || 'Failed to change language');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Error feedback
        buttons.forEach(btn => {
            btn.classList.remove('loading');
            btn.classList.add('error');
        });
        labels.forEach(label => label.textContent = '❌');
        
        setTimeout(() => {
            buttons.forEach(btn => btn.classList.remove('error'));
            initLanguageSwitcher();
        }, 2000);
    });
}

/**
 * Setup dropdown behavior
 */
function setupDropdownBehavior() {
    document.querySelectorAll('.language-switcher-btn').forEach(button => {
        button.setAttribute('aria-haspopup', 'true');
        button.setAttribute('aria-expanded', 'false');
        
        button.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdown = this.closest('.dropdown');
            const menu = dropdown.querySelector('.language-menu');
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Close others
            document.querySelectorAll('.dropdown').forEach(other => {
                if (other !== dropdown) {
                    const otherBtn = other.querySelector('.language-switcher-btn');
                    const otherMenu = other.querySelector('.language-menu');
                    if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
                    if (otherMenu) {
                        otherMenu.classList.remove('opacity-100', 'visible');
                        otherMenu.classList.add('opacity-0', 'invisible');
                    }
                }
            });
            
            // Toggle current
            if (isExpanded) {
                console.log('Closing menu...');
                this.setAttribute('aria-expanded', 'false');
                menu.classList.remove('opacity-100', 'visible');
                menu.classList.add('opacity-0', 'invisible');
            } else {
                console.log('Opening menu...');
                this.setAttribute('aria-expanded', 'true');
                menu.classList.remove('opacity-0', 'invisible');
                menu.classList.add('opacity-100', 'visible');
                
                // Force display with inline styles as backup
                menu.style.display = 'block';
                menu.style.opacity = '1';
                menu.style.visibility = 'visible';
                menu.style.pointerEvents = 'auto';
                menu.style.backgroundColor = '#ffff00'; // Bright yellow
                menu.style.border = '5px solid #ff0000'; // Thick red border
                menu.style.position = 'fixed';
                menu.style.top = '60px';
                menu.style.right = '20px';
                menu.style.zIndex = '99999';
                
                console.log('Menu classes:', menu.className);
                console.log('Menu computed display:', window.getComputedStyle(menu).display);
                console.log('Menu computed visibility:', window.getComputedStyle(menu).visibility);
                console.log('Menu computed opacity:', window.getComputedStyle(menu).opacity);
                console.log('Menu position:', menu.getBoundingClientRect());
                console.log('Menu HTML:', menu.outerHTML);
            }
        };
    });
    
    // Close on outside click
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.language-switcher-container')) {
            document.querySelectorAll('.language-switcher-btn').forEach(btn => {
                btn.setAttribute('aria-expanded', 'false');
            });
            document.querySelectorAll('.language-menu').forEach(menu => {
                menu.classList.remove('opacity-100', 'visible');
                menu.classList.add('opacity-0', 'invisible');
            });
        }
    });
}

/**
 * Initialize on DOM ready
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        initLanguageSwitcher();
        setupDropdownBehavior();
    });
} else {
    initLanguageSwitcher();
    setupDropdownBehavior();
}

// Make functions globally available
window.changeLanguage = changeLanguage;
window.initLanguageSwitcher = initLanguageSwitcher;
