/**
 * Casual Worker Manager - Complete Interactive Onboarding System
 * Comprehensive guided tour from sign-in through all main features
 * Features: Dashboard, Workers, Tasks, and Reports (excludes billing/payments)
 */

class OnboardingSystem {
    constructor() {
        this.currentStep = 0;
        this.totalSteps = 0;
        this.isActive = false;
        this.overlay = null;
        this.tooltip = null;
        this.currentPage = this.getCurrentPage();
        
        // Onboarding flow configuration
        this.flows = {
            'signin': this.getSignInFlow(),
            'home': this.getHomeFlow(),
            'workers': this.getWorkersFlow(),
            'tasks': this.getTasksFlow(),
            'reports': this.getReportsFlow(),
            'attendance': this.getAttendanceFlow()
        };
        
        this.init();
    }
    
    init() {
        this.createOverlay();
        this.createTooltip();
        this.bindEvents();
        
        // Check if user should see onboarding
        this.checkAndStartOnboarding();
    }
    
    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/signin' || path === '/finishSignin') return 'signin';
        if (path === '/home' || path === '/') return 'home';
        if (path === '/workers') return 'workers';
        if (path === '/tasks' || path.includes('/task/')) return 'tasks';
        if (path === '/reports') return 'reports';
        if (path.includes('/attendance') || path.includes('/task_attendance')) return 'attendance';
        return 'unknown';
    }
    
    shouldShowOnboarding() {
        // Multiple checks to ensure onboarding only shows for first-time users
        
        // 1. Check localStorage - most reliable for returning users
        const hasSeenOnboarding = localStorage.getItem('embee_onboarding_completed');
        if (hasSeenOnboarding === 'true') {
            return false;
        }
        
        // 2. Check URL parameter to skip onboarding
        const skipOnboarding = new URLSearchParams(window.location.search).get('skip_onboarding');
        if (skipOnboarding === 'true') {
            return false;
        }
        
        // 3. Check session storage (in case localStorage is disabled)
        const sessionCompleted = sessionStorage.getItem('embee_onboarding_completed'); 
        if (sessionCompleted === 'true') {
            return false;
        }
        
        // 4. Additional check: Don't show onboarding if user is on certain pages
        const currentPage = this.getCurrentPage();
        if (currentPage === 'unknown') {
            return false;
        }
        
        // 5. Check if user just signed in (new session indicator)
        // This helps identify truly first-time users vs returning users
        const isNewSession = !sessionStorage.getItem('user_session_started');
        if (isNewSession) {
            sessionStorage.setItem('user_session_started', 'true');
            return true; // Show onboarding for new sessions
        }
        
        // 6. Fallback: Only show if explicitly requested
        const forceOnboarding = new URLSearchParams(window.location.search).get('show_onboarding');
        return forceOnboarding === 'true';
    }
    
    async checkAndStartOnboarding() {
        // First do quick client-side check
        if (!this.shouldShowOnboarding()) {
            return;
        }
        
        // Additional server-side check for more accurate first-time user detection
        try {
            const response = await fetch('/api/user/onboarding-status', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // If server says user has completed onboarding, don't show it
                if (data.completed) {
                    localStorage.setItem('embee_onboarding_completed', 'true');
                    return;
                }
                
                // If server confirms this is a first-time user, show onboarding
                if (data.isFirstTime) {
                    setTimeout(() => this.showWelcomeMessage(() => this.startOnboarding()), 1000);
                    return;
                }
            }
        } catch (error) {
            console.warn('Could not check server-side onboarding status:', error);
            // Fall back to client-side only detection
        }
        
        // Fallback to client-side detection if server check fails
        if (this.shouldShowOnboarding()) {
            setTimeout(() => this.startOnboarding(), 1000);
        }
    }
    
    // Show a welcome message for first-time users
    showWelcomeMessage(callback) {
        const welcomeHtml = `
            <div id="welcome-message" class="fixed inset-0 bg-black bg-opacity-40 z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-2xl p-8 m-4 max-w-lg text-center shadow-2xl transform animate-fadeIn">
                    <div class="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                        <span class="text-2xl">👋</span>
                    </div>
                    <h2 class="text-2xl font-bold mb-3 text-gray-800">Welcome!</h2>
                    <p class="text-gray-600 mb-6 leading-relaxed">Ready for a quick 2-minute tour? We'll show you the essentials to get started managing your team.</p>
                    <div class="mb-6 text-sm text-gray-500 flex items-center justify-center gap-2">
                        <i class="fas fa-clock text-blue-500"></i>
                        <span>You're on a free trial - upgrade anytime to unlock all features</span>
                    </div>
                    <div class="flex gap-3 justify-center">
                        <button id="start-tour-btn" class="px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors">
                            Start Quick Tour
                        </button>
                        <button id="skip-tour-btn" class="px-6 py-3 text-gray-600 rounded-xl font-medium hover:bg-gray-100 transition-colors">
                            Skip for Now
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', welcomeHtml);
        
        document.getElementById('start-tour-btn').addEventListener('click', () => {
            document.getElementById('welcome-message').remove();
            callback();
        });
        
        document.getElementById('skip-tour-btn').addEventListener('click', () => {
            document.getElementById('welcome-message').remove();
            localStorage.setItem('embee_onboarding_completed', 'true');
        });
    }
    
    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'onboarding-overlay';
        this.overlay.innerHTML = `
            <div class="onboarding-backdrop"></div>
            <div class="onboarding-spotlight"></div>
        `;
        document.body.appendChild(this.overlay);
    }
    
    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'onboarding-tooltip';
        this.tooltip.innerHTML = `
            <div class="tooltip-content">
                <div class="tooltip-header">
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="tooltip-title"></h3>
                        <div class="tooltip-progress">
                            <span class="progress-text"><span class="current-step">1</span>/<span class="total-steps">1</span></span>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
                <div class="tooltip-body">
                    <p class="tooltip-description"></p>
                    <div class="tooltip-actions">
                        <button class="btn-skip">Skip</button>
                        <div class="nav-buttons">
                            <button class="btn-prev">← Back</button>
                            <button class="btn-next">Next →</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(this.tooltip);
    }
    
    bindEvents() {
        // Navigation buttons
        this.tooltip.querySelector('.btn-next').addEventListener('click', () => this.nextStep());
        this.tooltip.querySelector('.btn-prev').addEventListener('click', () => this.prevStep());
        this.tooltip.querySelector('.btn-skip').addEventListener('click', () => this.endOnboarding());
        
        // Escape key to exit
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isActive) {
                this.endOnboarding();
            }
        });
        
        // Manual onboarding trigger
        window.addEventListener('start-onboarding', () => this.startOnboarding());
    }
    
    startOnboarding() {
        if (!this.flows[this.currentPage]) {
            console.warn(`No onboarding flow defined for page: ${this.currentPage}`);
            return;
        }
        
        this.isActive = true;
        this.currentStep = 0;
        this.totalSteps = this.flows[this.currentPage].length;
        
        this.overlay.classList.add('active');
        this.showStep(this.currentStep);
        
        // Disable page scrolling
        document.body.style.overflow = 'hidden';
    }
    
    showStep(stepIndex) {
        const flow = this.flows[this.currentPage];
        if (!flow || stepIndex >= flow.length) return;
        
        const step = flow[stepIndex];
        this.currentStep = stepIndex;
        
        // Update tooltip content
        this.tooltip.querySelector('.tooltip-title').textContent = step.title;
        this.tooltip.querySelector('.tooltip-description').innerHTML = step.description;
        this.tooltip.querySelector('.current-step').textContent = stepIndex + 1;
        this.tooltip.querySelector('.total-steps').textContent = this.totalSteps;
        
        // Update progress bar
        const progress = ((stepIndex + 1) / this.totalSteps) * 100;
        this.tooltip.querySelector('.progress-fill').style.width = `${progress}%`;
        
        // Update navigation buttons
        this.tooltip.querySelector('.btn-prev').style.display = stepIndex === 0 ? 'none' : 'inline-block';
        this.tooltip.querySelector('.btn-next').textContent = stepIndex === this.totalSteps - 1 ? 'Finish' : 'Next';
        
        // Position spotlight and tooltip
        this.positionElements(step);
        
        // Show tooltip
        this.tooltip.classList.add('active');
        
        // Execute step action if any
        if (step.action) {
            step.action();
        }
    }
    
    positionElements(step) {
        const targetElement = step.selector ? document.querySelector(step.selector) : null;
        
        if (targetElement) {
            const rect = targetElement.getBoundingClientRect();
            const spotlight = this.overlay.querySelector('.onboarding-spotlight');
            
            // Position spotlight
            spotlight.style.left = `${rect.left - 10}px`;
            spotlight.style.top = `${rect.top - 10}px`;
            spotlight.style.width = `${rect.width + 20}px`;
            spotlight.style.height = `${rect.height + 20}px`;
            
            // Position tooltip
            this.positionTooltip(rect, step.position || 'bottom');
        } else {
            // No target element, center tooltip
            this.centerTooltip();
        }
    }
    
    positionTooltip(targetRect, position) {
        const tooltip = this.tooltip;
        const tooltipRect = tooltip.getBoundingClientRect();
        let left, top;
        
        switch (position) {
            case 'top':
                left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
                top = targetRect.top - tooltipRect.height - 20;
                break;
            case 'bottom':
                left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
                top = targetRect.bottom + 20;
                break;
            case 'left':
                left = targetRect.left - tooltipRect.width - 20;
                top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
                break;
            case 'right':
                left = targetRect.right + 20;
                top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
                break;
        }
        
        // Ensure tooltip stays within viewport
        left = Math.max(10, Math.min(left, window.innerWidth - tooltipRect.width - 10));
        top = Math.max(10, Math.min(top, window.innerHeight - tooltipRect.height - 10));
        
        tooltip.style.left = `${left}px`;
        tooltip.style.top = `${top}px`;
    }
    
    centerTooltip() {
        const tooltip = this.tooltip;
        tooltip.style.left = '50%';
        tooltip.style.top = '50%';
        tooltip.style.transform = 'translate(-50%, -50%)';
    }
    
    nextStep() {
        if (this.currentStep < this.totalSteps - 1) {
            this.showStep(this.currentStep + 1);
        } else {
            this.endOnboarding(true);
        }
    }
    
    prevStep() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }
    
    endOnboarding(completed = false) {
        this.isActive = false;
        this.overlay.classList.remove('active');
        this.tooltip.classList.remove('active');
        
        // Re-enable page scrolling
        document.body.style.overflow = '';
        
        if (completed) {
            localStorage.setItem('embee_onboarding_completed', 'true');
            this.showCompletionMessage();
        }
    }
    
    showCompletionMessage() {
        const message = document.createElement('div');
        message.className = 'onboarding-completion';
        message.innerHTML = `
            <div class="completion-content">
                <div class="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                    <span class="text-2xl">✅</span>
                </div>
                <h3 class="text-xl font-bold text-gray-800 mb-3">You're All Set!</h3>
                <p class="text-gray-600 mb-6">Ready to start managing your team. Remember, you're on a free trial - upgrade anytime for full access.</p>
                <div class="completion-tips bg-blue-50 rounded-lg p-4 mb-6">
                    <p class="font-semibold text-blue-800 mb-2">Next Steps:</p>
                    <div class="text-sm text-blue-700 space-y-1">
                        <div>1. Add your first workers</div>
                        <div>2. Create a task and assign workers</div>
                        <div>3. Track attendance and generate reports</div>
                    </div>
                </div>
                <div class="completion-actions flex gap-3 justify-center">
                    <button class="btn-dismiss px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
                        Get Started
                    </button>
                    <button class="btn-replay px-6 py-3 text-gray-600 rounded-lg font-medium hover:bg-gray-100 transition-colors" onclick="window.onboardingSystem?.restartOnboarding()">
                        Replay Tour
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(message);
        setTimeout(() => message.classList.add('active'), 100);
        
        message.querySelector('.btn-dismiss').addEventListener('click', () => {
            message.remove();
        });
        
        setTimeout(() => {
            if (message.parentNode) {
                message.remove();
            }
        }, 8000);
    }
    
    // ONBOARDING FLOWS FOR EACH PAGE
    
    getSignInFlow() {
        return [
            {
                title: "Let's Get Started! 🚀",
                description: "Welcome to your workforce management platform. We'll show you the key features in just a few quick steps.",
                selector: null
            },
            {
                title: "Sign In",
                description: "Use Google or email to sign in. New here? You can create your company workspace right from this page.",
                selector: ".auth-container, .signin-form",
                position: "bottom"
            },
            {
                title: "Workspace Setup",
                description: "Join your team's workspace with a code, or create a new one for your company.",
                selector: "[data-onboarding='workspace-section'], .workspace-section",
                position: "top"
            }
        ];
    }
    
    getHomeFlow() {
        return [
            {
                title: "Your Dashboard 📊",
                description: "This is your control center. See your team stats and access everything in one place.",
                selector: ".dashboard-container, .hero-glass"
            },
            {
                title: "Key Metrics",
                description: "These cards show your workers, tasks, and reports. Click any card to dive deeper.",
                selector: "[data-onboarding='stats-container'], .stat-card",
                position: "bottom"
            },
            {
                title: "Quick Actions",
                description: "Fast shortcuts to add workers, create tasks, or record attendance.",
                selector: "[data-onboarding='quick-actions'], .quick-action-btn",
                position: "top"
            },
            {
                title: "Main Navigation",
                description: "Use the sidebar to navigate: Workers, Tasks, and Reports. Each has specialized tools.",
                selector: ".sidebar, .sidebar-container",
                position: "right"
            }
        ];
    }
    
    getWorkersFlow() {
        return [
            {
                title: "Manage Your Team 👥",
                description: "Add, organize, and track all your workers in one place.",
                selector: ".workers-container, .page-container"
            },
            {
                title: "Add Workers",
                description: "Click here to add new team members with their details and contact info.",
                selector: "[data-onboarding='add-worker-btn'], .btn-primary, .add-worker-btn",
                position: "bottom"
            },
            {
                title: "Workers List",
                description: "View all your workers here. Click on any worker to edit their details.",
                selector: "[data-onboarding='workers-table'], .workers-table, table",
                position: "top"
            },
            {
                title: "Import from Excel",
                description: "Add multiple workers at once by uploading a spreadsheet.",
                selector: "[data-onboarding='import-btn'], .import-workers-btn",
                position: "bottom"
            }
        ];
    }
    
    getTasksFlow() {
        return [
            {
                title: "Manage Tasks 📋",
                description: "Create projects, assign workers, and track progress all in one place.",
                selector: ".tasks-container, .page-container"
            },
            {
                title: "Create Tasks",
                description: "Click here to create new tasks. Set payment type (daily, hourly, or per-piece) and assign workers.",
                selector: "[data-onboarding='create-task-btn'], .btn-primary, .create-task-btn",
                position: "bottom"
            },
            {
                title: "Task Status",
                description: "See all tasks with their status: Pending, In Progress, or Completed.",
                selector: "[data-onboarding='tasks-table'], .tasks-table, table",
                position: "top"
            },
            {
                title: "Track Attendance",
                description: "Click any task to record who showed up and track hours or units completed.",
                selector: "[data-onboarding='attendance-link'], .task-row a, .attendance-link",
                position: "right"
            }
        ];
    }
    
    getReportsFlow() {
        return [
            {
                title: "Generate Reports 📈",
                description: "Create payroll and attendance reports for your team.",
                selector: ".reports-container, .page-container"
            },
            {
                title: "Report Types",
                description: "Choose 'Per Day', 'Per Hour', or 'Per Part' based on how you pay workers.",
                selector: "[data-onboarding='report-types'], .report-type-selector, .report-tabs",
                position: "bottom"
            },
            {
                title: "Select Date Range",
                description: "Pick the time period for your report - daily, weekly, or custom range.",
                selector: "[data-onboarding='date-range'], .date-inputs, .date-picker",
                position: "top"
            },
            {
                title: "Export Reports",
                description: "Download as CSV or Excel for your accounting software or records.",
                selector: "[data-onboarding='export-buttons'], .export-options, .download-btn",
                position: "left"
            }
        ];
    }
    
    getAttendanceFlow() {
        return [
            {
                title: "Track Attendance ✅",
                description: "Record who showed up and track hours or units completed for payment.",
                selector: ".attendance-container, .page-container"
            },
            {
                title: "Worker List",
                description: "See all workers assigned to this task. Each row shows their attendance and performance.",
                selector: "[data-onboarding='attendance-table'], .attendance-table, table",
                position: "top"
            },
            {
                title: "Mark Present/Absent",
                description: "Check the box to mark workers as present. Only present workers get paid.",
                selector: "[data-onboarding='attendance-checkbox'], input[type='checkbox'], .attendance-status",
                position: "right"
            },
            {
                title: "Record Hours or Units",
                description: "Enter hours worked (e.g., 8.5) or units completed (e.g., 50 pieces) for payment calculation.",
                selector: "[data-onboarding='hours-input'], input[name*='hours'], .hours-input",
                position: "bottom"
            },
            {
                title: "Save Data",
                description: "Click to save all attendance data. Payments are calculated automatically.",
                selector: "[data-onboarding='save-attendance'], .btn-primary, .save-btn",
                position: "bottom"
            }
        ];
    }
    
    // PUBLIC METHODS
    
    // Restart onboarding (removes completion flag and starts tour)
    restartOnboarding() {
        localStorage.removeItem('embee_onboarding_completed');
        sessionStorage.removeItem('embee_onboarding_completed');
        this.startOnboarding();
    }
    
    // Skip onboarding entirely
    skipOnboarding() {
        this.endOnboarding();
    }
    
    // Start onboarding for a specific page (useful for testing)
    startOnboardingForPage(pageName) {
        if (this.flows[pageName]) {
            this.currentPage = pageName;
            this.startOnboarding();
        } else {
            console.warn(`No onboarding flow found for page: ${pageName}`);
        }
    }
}

// CSS Styles for onboarding
const onboardingStyles = `
    .onboarding-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 10000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .onboarding-overlay.active {
        opacity: 1;
        pointer-events: all;
    }
    
    .onboarding-backdrop {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(1px);
    }
    
    .onboarding-spotlight {
        position: absolute;
        background: transparent;
        border-radius: 8px;
        box-shadow: 
            0 0 0 3px rgba(59, 130, 246, 0.6),
            0 0 0 9999px rgba(0, 0, 0, 0.5);
        pointer-events: none;
        transition: all 0.3s ease;
        z-index: 10001;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .onboarding-tooltip {
        position: fixed;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        max-width: 380px;
        min-width: 300px;
        z-index: 10002;
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.2s ease;
        pointer-events: all;
    }
    
    .onboarding-tooltip.active {
        opacity: 1;
        transform: translateY(0);
        animation: fadeIn 0.3s ease;
    }
    
    .tooltip-content {
        padding: 24px;
        position: relative;
    }
    
    .tooltip-content::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        border-radius: 16px 16px 0 0;
    }
    
    .tooltip-header {
        margin-bottom: 16px;
        margin-top: 4px;
    }
    
    .tooltip-title {
        font-size: 18px;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
        line-height: 1.4;
    }
    
    .tooltip-progress {
        align-items: center;
    }
    
    .progress-text {
        font-size: 12px;
        color: #6b7280;
        font-weight: 500;
    }
    
    .progress-bar {
        width: 100%;
        height: 3px;
        background: #f3f4f6;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 8px;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    
    .tooltip-description {
        font-size: 14px;
        line-height: 1.5;
        color: #4b5563;
        margin: 0 0 20px 0;
    }
    
    .tooltip-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .btn-skip {
        background: none;
        border: none;
        color: #6b7280;
        font-size: 13px;
        cursor: pointer;
        padding: 8px 12px;
        border-radius: 6px;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    
    .btn-skip:hover {
        background: #f3f4f6;
        color: #374151;
    }
    
    .nav-buttons {
        display: flex;
        gap: 8px;
    }
    
    .btn-prev, .btn-next {
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
    }
    
    .btn-prev {
        background: #f9fafb;
        color: #374151;
        border: 1px solid #e5e7eb;
    }
    
    .btn-prev:hover {
        background: #f3f4f6;
    }
    
    .btn-next {
        background: #3b82f6;
        color: white;
    }
    
    .btn-next:hover {
        background: #2563eb;
    }
    
    .tooltip-arrow {
        position: absolute;
        width: 12px;
        height: 12px;
        background: white;
        transform: rotate(45deg);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Completion message styles */
    .onboarding-completion {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        border-radius: 16px;
        padding: 32px;
        max-width: 450px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        z-index: 10003;
        opacity: 0;
        transition: all 0.3s ease;
    }
    
    .onboarding-completion.active {
        opacity: 1;
        animation: fadeIn 0.3s ease;
    }
    
    .completion-content h3 {
        font-size: 20px;
        color: #1f2937;
        margin: 0 0 12px 0;
        font-weight: 600;
    }
    
    .completion-content p {
        color: #6b7280;
        margin: 0 0 24px 0;
        line-height: 1.5;
    }
    
    .completion-tips {
        background: #f0f9ff;
        border: 1px solid #e0f2fe;
        border-radius: 8px;
        padding: 16px;
        margin: 24px 0;
        text-align: left;
    }
    
    .completion-tips p {
        color: #0369a1;
        font-weight: 600;
        margin: 0 0 8px 0;
        font-size: 14px;
    }
    
    .completion-tips div {
        color: #0284c7;
        font-size: 13px;
        line-height: 1.4;
    }
    
    .completion-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-top: 0;
    }
    
    /* Mobile responsive styles */
    @media (max-width: 768px) {
        .onboarding-tooltip {
            max-width: 90vw;
            min-width: 280px;
            margin: 16px;
        }
        
        .tooltip-content {
            padding: 20px;
        }
        
        .tooltip-title {
            font-size: 16px;
        }
        
        .tooltip-actions {
            flex-direction: column;
            gap: 12px;
            align-items: stretch;
        }
        
        .nav-buttons {
            width: 100%;
            justify-content: space-between;
        }
        
        .btn-prev, .btn-next {
            flex: 1;
        }
        
        .onboarding-completion {
            max-width: 90vw;
            padding: 24px 20px;
            margin: 16px;
        }
        
        .completion-actions {
            flex-direction: column;
            gap: 8px;
        }
        
        #welcome-message .bg-white {
            margin: 16px;
            padding: 24px;
        }
    }
    
    /* Help button styles */
    .onboarding-help-button {
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 56px;
        height: 56px;
        background: linear-gradient(135deg, #1A2B48, #E5B23A);
        color: white;
        border: none;
        border-radius: 50%;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(26, 43, 72, 0.3);
        z-index: 1000;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .onboarding-help-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(26, 43, 72, 0.4);
    }
    
    .onboarding-help-button.hidden {
        opacity: 0;
        pointer-events: none;
        transform: translateY(20px);
    }
`;

// Initialize onboarding system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Inject styles
    const styleSheet = document.createElement('style');
    styleSheet.textContent = onboardingStyles;
    document.head.appendChild(styleSheet);
    
    // Initialize onboarding system
    window.onboardingSystem = new OnboardingSystem();
    
    // Add help button for manual onboarding restart
    addHelpButton();
});

function addHelpButton() {
    const helpButton = document.createElement('button');
    helpButton.className = 'onboarding-help-button';
    helpButton.innerHTML = '<i class="fas fa-question"></i>';
    helpButton.title = 'Take a tour of the application - Learn how to manage workers, tasks, and reports';
    
    helpButton.addEventListener('click', () => {
        if (window.onboardingSystem) {
            window.onboardingSystem.restartOnboarding();
        }
    });
    
    document.body.appendChild(helpButton);
    
    // Hide help button during onboarding
    const observer = new MutationObserver(() => {
        if (window.onboardingSystem && window.onboardingSystem.isActive) {
            helpButton.classList.add('hidden');
        } else {
            helpButton.classList.remove('hidden');
        }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
}

// Export for external use
window.OnboardingSystem = OnboardingSystem;
