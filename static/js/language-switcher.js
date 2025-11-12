/**
 * Language Switcher - Optimized External JavaScript
 * Handles language selection and UI updates efficiently
 */

// Cache for avoiding repeated API calls
let languagesCache = null;
let initializationInProgress = false;

/**
 * Toggle dropdown function (Enhanced for all page contexts)
 */
function toggleDropdown(dropdownElement) {
    console.log('Toggle dropdown called');
    
    // Find the menu - support both class names
    const menu = dropdownElement.querySelector('.dropdown-menu') || dropdownElement.querySelector('.language-menu');
    const button = dropdownElement.querySelector('.dropdown-toggle') || dropdownElement.querySelector('.language-switcher-btn');
    
    if (!menu) {
        console.error('No dropdown menu found');
        return;
    }
    
    if (!button) {
        console.error('No dropdown button found');
        return;
    }
    
    // Close all other dropdowns first
    const allDropdowns = document.querySelectorAll('.language-switcher, .language-switcher-container');
    allDropdowns.forEach(dropdown => {
        if (dropdown !== dropdownElement) {
            const otherMenu = dropdown.querySelector('.dropdown-menu') || dropdown.querySelector('.language-menu');
            const otherButton = dropdown.querySelector('.dropdown-toggle') || dropdown.querySelector('.language-switcher-btn');
            const otherDropdown = dropdown.querySelector('.dropdown');
            
            if (otherMenu) {
                // Hide other menus
                otherMenu.classList.add('invisible', 'opacity-0');
                otherMenu.classList.remove('visible', 'opacity-100');
                otherMenu.style.display = 'none';
            }
            
            if (otherButton) {
                otherButton.setAttribute('aria-expanded', 'false');
            }
            
            if (otherDropdown) {
                otherDropdown.classList.remove('show');
            }
        }
    });
    
    // Toggle current dropdown
    const isVisible = menu.classList.contains('visible') || 
                     menu.classList.contains('opacity-100') || 
                     button.getAttribute('aria-expanded') === 'true';
    
    const parentDropdown = dropdownElement.querySelector('.dropdown');
    
    if (isVisible) {
        // Hide dropdown
        menu.classList.add('invisible', 'opacity-0');
        menu.classList.remove('visible', 'opacity-100');
        menu.style.display = 'none';
        button.setAttribute('aria-expanded', 'false');
        if (parentDropdown) {
            parentDropdown.classList.remove('show');
        }
        console.log('Dropdown closed');
    } else {
        // Show dropdown
        menu.classList.remove('invisible', 'opacity-0');
        menu.classList.add('visible', 'opacity-100');
        menu.style.display = 'block';
        button.setAttribute('aria-expanded', 'true');
        if (parentDropdown) {
            parentDropdown.classList.add('show');
        }
        console.log('Dropdown opened');
    }
}

/**
 * Set language function (API endpoint compatible)
 */
async function setLanguage(language) {
    console.log('Setting language to:', language);
    
    try {
        const response = await fetch('/api/language/set', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language: language })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('Language set successfully');
            // Reload page to apply new language
            window.location.reload();
        } else {
            console.error('Failed to set language:', data.message);
            alert('Failed to change language: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error setting language:', error);
        alert('Error changing language. Please try again.');
    }
}

/**
 * Initialize language switcher - called once on page load
 */
function initLanguageSwitcher() {
    // Prevent multiple simultaneous initializations
    if (initializationInProgress) {
        console.log('⚠️ Language switcher initialization already in progress');
        return;
    }
    
    initializationInProgress = true;
    
    try {
        console.log('🌐 Initializing language switcher...');
        console.log('Page URL:', window.location.href);
        
        // Check if language switcher elements exist
        const containers = document.querySelectorAll('.language-switcher-container');
        console.log(`Found ${containers.length} language switcher container(s)`);
        
        if (containers.length === 0) {
            console.warn('⚠️ No language switcher containers found on page');
            initializationInProgress = false;
            return;
        }
        
        // Fetch available languages with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            console.error('⏱️ API request timeout after 5 seconds');
            controller.abort();
        }, 5000);
        
        console.log('📡 Fetching languages from /api/languages...');
        
        fetch('/api/languages', { signal: controller.signal })
            .then(response => {
                clearTimeout(timeoutId);
                console.log(`✓ Response received with status: ${response.status}`);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('✓ Languages data received:', data);
                languagesCache = data; // Cache the response
                populateLanguageMenus(data);
                initializationInProgress = false;
                console.log('✅ Language switcher initialized successfully');
            })
            .catch(error => {
                clearTimeout(timeoutId);
                console.error('❌ Error loading languages:', error);
                
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
                
                console.log('Using fallback language data:', fallbackData);
                languagesCache = fallbackData;
                populateLanguageMenus(fallbackData);
                initializationInProgress = false;
                console.log('⚠️ Language switcher initialized with fallback data');
            });
    } catch (error) {
        console.error('❌ Error initializing language switcher:', error);
        initializationInProgress = false;
    }
}

/**
 * Populate all language menus on the page
 */
function populateLanguageMenus(data) {
    console.log('Populating language menus with data:', data);
    
    const languages = data.languages || {};
    const currentLanguage = data.current_language || 'en';
    
    console.log(`Current language: ${currentLanguage}`);
    console.log(`Available languages:`, languages);
    
    const languageMenus = document.querySelectorAll('.language-menu');
    console.log(`Found ${languageMenus.length} language menu(s)`);
    
    if (languageMenus.length === 0) {
        console.warn('No language menus found on page!');
        return;
    }
    
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
            a.setAttribute('role', 'menuitem');
            a.className = code === currentLanguage ? 'active' : '';
            
            a.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                changeLanguage(code);
            };
            
            li.appendChild(a);
            menu.appendChild(li);
        });
        
        console.log(`✓ Menu ${index + 1} populated with ${sorted.length} languages`);
    });
    
    // Update current language labels
    const labels = document.querySelectorAll('.current-lang-label');
    console.log(`Found ${labels.length} language label(s)`);
    
    const displayName = languages[currentLanguage] || 'English';
    labels.forEach((label, index) => {
        label.textContent = displayName;
        console.log(`✓ Label ${index + 1} updated to: ${displayName}`);
    });
    
    console.log('Language menus populated successfully');
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
    console.log('Setting up dropdown behavior...');
    
    const buttons = document.querySelectorAll('.language-switcher-btn');
    console.log(`Found ${buttons.length} language switcher button(s)`);
    
    buttons.forEach((button, index) => {
        button.setAttribute('aria-haspopup', 'true');
        button.setAttribute('aria-expanded', 'false');
        
        button.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdown = this.closest('.dropdown');
            const menu = dropdown.querySelector('.language-menu');
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            console.log(`Button ${index + 1} clicked. Current state: ${isExpanded ? 'open' : 'closed'}`);
            
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
                // Remove inline styles when closing
                setTimeout(() => {
                    if (!menu.classList.contains('visible')) {
                        menu.style.display = '';
                        menu.style.opacity = '';
                        menu.style.visibility = '';
                        menu.style.pointerEvents = '';
                    }
                }, 200);
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
                
                console.log('Menu should now be visible. Classes:', menu.className);
                console.log('Menu inline styles:', menu.style.cssText);
            }
        };
        
        console.log(`✓ Button ${index + 1} configured`);
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
                // Clear inline styles after animation
                setTimeout(() => {
                    if (!menu.classList.contains('visible')) {
                        menu.style.display = '';
                        menu.style.opacity = '';
                        menu.style.visibility = '';
                        menu.style.pointerEvents = '';
                    }
                }, 200);
            });
        }
    });
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.language-switcher-btn').forEach(btn => {
                btn.setAttribute('aria-expanded', 'false');
            });
            document.querySelectorAll('.language-menu').forEach(menu => {
                menu.classList.remove('opacity-100', 'visible');
                menu.classList.add('opacity-0', 'invisible');
            });
        }
    });
    
    console.log('Dropdown behavior setup complete');
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
