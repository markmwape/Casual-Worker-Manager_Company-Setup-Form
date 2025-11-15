/**
 * Onboarding Test and Debug Utilities
 * Add this to any page to test the onboarding system
 */

// Test if onboarding system is loaded
function testOnboardingSystem() {
    console.log('=== Onboarding System Test ===');
    
    if (!window.onboardingSystem) {
        console.error('❌ Onboarding system not found');
        return false;
    }
    
    console.log('✅ Onboarding system loaded');
    console.log('Current page:', window.onboardingSystem.currentPage);
    console.log('Available flows:', Object.keys(window.onboardingSystem.flows));
    
    const currentFlow = window.onboardingSystem.flows[window.onboardingSystem.currentPage];
    if (currentFlow) {
        console.log('✅ Flow exists for current page');
        console.log('Number of steps:', currentFlow.length);
        console.log('Steps:', currentFlow.map((s, i) => `${i + 1}. ${s.title}`));
        
        // Check if elements exist
        console.log('\n=== Checking Elements ===');
        currentFlow.forEach((step, i) => {
            if (step.selector) {
                const element = document.querySelector(step.selector);
                if (element) {
                    console.log(`✅ Step ${i + 1} element found:`, step.selector);
                } else {
                    console.warn(`⚠️ Step ${i + 1} element NOT found:`, step.selector);
                }
            }
        });
    } else {
        console.warn('⚠️ No flow defined for current page');
    }
    
    return true;
}

// Force start onboarding tour
function forceStartTour() {
    console.log('Forcing tour to start...');
    if (window.onboardingSystem) {
        window.onboardingSystem.restartOnboarding();
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

// Make functions available globally
window.testOnboardingSystem = testOnboardingSystem;
window.forceStartTour = forceStartTour;
window.clearOnboardingState = clearOnboardingState;

console.log('Onboarding test utilities loaded. Available functions:');
console.log('- testOnboardingSystem() - Test if onboarding is working');
console.log('- forceStartTour() - Force start the tour');
console.log('- clearOnboardingState() - Clear onboarding completion state');
