/**
 * Onboarding Test and Debug Utilities
 * Add this to any page to test the onboarding system
 */

// Test if onboarding system is loaded
function testOnboardingSystem() {
    console.log('=== Onboarding System Test ===');
    
    // First, check basic system
    if (!window.onboardingSystem) {
        console.error('❌ Onboarding system not found');
        return false;
    }
    
    console.log('✅ Onboarding system loaded');
    
    // Update current page detection
    const detectedPage = window.onboardingSystem.getCurrentPage();
    window.onboardingSystem.currentPage = detectedPage;
    
    console.log('Current URL:', window.location.pathname);
    console.log('Detected page:', detectedPage);
    console.log('Available flows:', Object.keys(window.onboardingSystem.flows));
    
    const currentFlow = window.onboardingSystem.flows[detectedPage];
    if (currentFlow) {
        console.log('✅ Flow exists for current page');
        console.log('Number of steps:', currentFlow.length);
        console.log('Steps:', currentFlow.map((s, i) => `${i + 1}. ${s.title}`));
        
        // Check if elements exist
        console.log('\n=== Checking Elements ===');
        let foundElements = 0;
        let totalElements = 0;
        
        currentFlow.forEach((step, i) => {
            if (step.selector) {
                totalElements++;
                const element = document.querySelector(step.selector);
                if (element) {
                    console.log(`✅ Step ${i + 1} element found:`, step.selector);
                    foundElements++;
                } else {
                    console.warn(`⚠️ Step ${i + 1} element NOT found:`, step.selector);
                }
            }
        });
        
        console.log(`\nElement Summary: ${foundElements}/${totalElements} elements found`);
        
        // Check for help button
        const helpButton = document.querySelector('.onboarding-help-button');
        if (helpButton) {
            console.log('✅ Help button found');
        } else {
            console.warn('⚠️ Help button not found');
        }
        
        return foundElements === totalElements;
    } else {
        console.warn('⚠️ No flow defined for current page');
        console.log('Expected page types: task_attendance, task_hours_worked, task_units_completed');
        
        // Try to detect what's wrong
        const path = window.location.pathname;
        if (path.includes('/task/') && path.includes('/attendance')) {
            console.log('💡 This looks like a task attendance page, but flow not found');
        } else if (path.includes('/task/') && path.includes('/hours-worked')) {
            console.log('💡 This looks like a task hours worked page, but flow not found');
        } else if (path.includes('/task/') && path.includes('/units-completed')) {
            console.log('💡 This looks like a task units completed page, but flow not found');
        }
        
        return false;
    }
}

// Force start onboarding tour
function forceStartTour() {
    console.log('Forcing tour to start...');
    if (window.onboardingSystem) {
        // Clear state first
        localStorage.removeItem('embee_onboarding_completed');
        sessionStorage.removeItem('embee_onboarding_completed');
        sessionStorage.setItem('user_session_started', 'true');
        
        // Update current page detection
        window.onboardingSystem.currentPage = window.onboardingSystem.getCurrentPage();
        
        // Force start (bypasses modal detection)
        window.onboardingSystem.forceStartOnboarding();
    } else {
        console.error('Onboarding system not available');
    }
}

// Clear onboarding state
function clearOnboardingState() {
    localStorage.removeItem('embee_onboarding_completed');
    sessionStorage.removeItem('embee_onboarding_completed');
    sessionStorage.removeItem('user_session_started');
    console.log('✅ Onboarding state cleared');
}

// Quick fix function for immediate troubleshooting
function quickFix() {
    console.log('=== QUICK FIX - Initializing Everything ===');
    
    // Force re-initialize the system
    if (window.onboardingSystem) {
        window.onboardingSystem.currentPage = window.onboardingSystem.getCurrentPage();
        console.log('✅ Re-initialized current page:', window.onboardingSystem.currentPage);
    }
    
    // Make sure help button exists
    let helpButton = document.querySelector('.onboarding-help-button');
    if (!helpButton) {
        console.log('🔧 Adding missing help button...');
        
        helpButton = document.createElement('button');
        helpButton.className = 'onboarding-help-button';
        helpButton.innerHTML = '?';
        helpButton.title = 'Replay tour - Learn how to use all features';
        helpButton.style.cssText = `
            position: fixed;
            bottom: 28px;
            right: 28px;
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 3px solid rgba(255, 255, 255, 0.9);
        `;
        
        helpButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            forceStartTour();
        });
        
        document.body.appendChild(helpButton);
        console.log('✅ Help button added');
    } else {
        console.log('✅ Help button already exists');
    }
    
    // Test the system
    const testResult = testOnboardingSystem();
    
    if (testResult) {
        console.log('🎉 Everything looks good! Click the help button (?) to start the tour.');
    } else {
        console.log('⚠️ Some issues detected. Try running forceStartTour() anyway.');
    }
    
    return testResult;
}

// Make functions available globally
window.testOnboardingSystem = testOnboardingSystem;
window.forceStartTour = forceStartTour;
window.clearOnboardingState = clearOnboardingState;
window.quickFix = quickFix;

console.log('Onboarding test utilities loaded. Available functions:');
console.log('- quickFix() - Fix common issues and test everything');
console.log('- testOnboardingSystem() - Test if onboarding is working');
console.log('- forceStartTour() - Force start the tour');
console.log('- clearOnboardingState() - Clear onboarding completion state');
