/**
 * Enhanced Casual Worker Manager Onboarding System
 * Improved UX with interactive elements, better animations, and refined flows
 */

class EnhancedOnboardingSystem {
    constructor() {
        this.currentStep = 0;
        this.totalSteps = 0;
        this.isActive = false;
        this.overlay = null;
        this.tooltip = null;
        this.currentPage = this.getCurrentPage();
        this.completedFlows = new Set();
        
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
        const hasSeenOnboarding = localStorage.getItem('embee_onboarding_completed');
        if (hasSeenOnboarding === 'true') return false;
        
        const skipOnboarding = new URLSearchParams(window.location.search).get('skip_onboarding');
        if (skipOnboarding === 'true') return false;
        
        const currentPage = this.getCurrentPage();
        if (currentPage === 'unknown') return false;
        
        const isNewSession = !sessionStorage.getItem('user_session_started');
        if (isNewSession) {
            sessionStorage.setItem('user_session_started', 'true');
            return true;
        }
        
        const forceOnboarding = new URLSearchParams(window.location.search).get('show_onboarding');
        return forceOnboarding === 'true';
    }
    
    async checkAndStartOnboarding() {
        if (!this.shouldShowOnboarding()) return;
        
        try {
            const response = await fetch('/api/user/onboarding-status', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.completed) {
                    localStorage.setItem('embee_onboarding_completed', 'true');
                    return;
                }
                
                if (data.isFirstTime) {
                    setTimeout(() => this.showWelcomeMessage(() => this.startOnboarding()), 800);
                    return;
                }
            }
        } catch (error) {
            console.warn('Onboarding status check failed:', error);
        }
        
        if (this.shouldShowOnboarding()) {
            setTimeout(() => this.startOnboarding(), 800);
        }
    }
    
    showWelcomeMessage(callback) {
        const welcomeHtml = `
            <div id="welcome-message" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4 backdrop-blur-md">
                <div class="bg-gradient-to-br from-white via-blue-50 to-cyan-50 rounded-3xl p-10 max-w-md shadow-2xl transform animate-slideUp border-4 border-white/60">
                    <div class="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-blue-500 via-cyan-500 to-blue-600 rounded-full flex items-center justify-center shadow-xl relative">
                        <span class="text-4xl animate-bounce">✨</span>
                        <div class="absolute inset-0 rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 opacity-30 animate-pulse"></div>
                    </div>
                    <h2 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600 mb-3 text-center">Welcome!</h2>
                    <p class="text-gray-700 text-center mb-2 leading-relaxed font-semibold text-lg">Let us show you around in 2 minutes</p>
                    <p class="text-sm text-gray-600 text-center mb-8">We'll guide you through managing your team</p>
                    
                    <div class="flex gap-3">
                        <button id="start-tour-btn" class="flex-1 px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-2xl font-bold hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg hover:shadow-2xl transform hover:scale-105 hover:-translate-y-1 border-2 border-blue-500">
                            Start Tour 🚀
                        </button>
                        <button id="skip-tour-btn" class="flex-1 px-6 py-4 text-gray-700 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl font-bold hover:from-gray-200 hover:to-gray-300 transition-all shadow-md hover:shadow-lg transform hover:scale-105 border-2 border-gray-300">
                            Skip
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
                    <div class="flex items-start justify-between gap-4 mb-3">
                        <h3 class="tooltip-title flex-1"></h3>
                        <span class="tooltip-progress text-xs font-semibold text-gray-500 whitespace-nowrap">
                            <span class="current-step">1</span>/<span class="total-steps">1</span>
                        </span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
                <div class="tooltip-body">
                    <p class="tooltip-description"></p>
                    <div class="tooltip-highlight-hint"></div>
                    <div class="tooltip-actions">
                        <button class="btn-skip">Skip</button>
                        <div class="nav-buttons">
                            <button class="btn-prev" style="display: none;">← Back</button>
                            <button class="btn-next">Next →</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(this.tooltip);
    }
    
    bindEvents() {
        this.tooltip.querySelector('.btn-next').addEventListener('click', () => this.nextStep());
        this.tooltip.querySelector('.btn-prev').addEventListener('click', () => this.prevStep());
        this.tooltip.querySelector('.btn-skip').addEventListener('click', () => this.endOnboarding());
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isActive) {
                this.endOnboarding();
            }
            if (e.key === 'ArrowRight' && this.isActive) {
                this.nextStep();
            }
            if (e.key === 'ArrowLeft' && this.isActive) {
                this.prevStep();
            }
        });
        
        window.addEventListener('start-onboarding', () => this.startOnboarding());
    }
    
    startOnboarding() {
        if (!this.flows[this.currentPage]) {
            console.warn(`No onboarding flow for: ${this.currentPage}`);
            return;
        }
        
        this.isActive = true;
        this.currentStep = 0;
        this.totalSteps = this.flows[this.currentPage].length;
        
        this.overlay.classList.add('active');
        this.showStep(0);
        
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
        
        // Prevent scroll and re-position spotlight on any scroll attempt
        this.scrollHandler = () => this.updateSpotlightPosition();
        window.addEventListener('scroll', this.scrollHandler, true);
        window.addEventListener('wheel', (e) => e.preventDefault(), { passive: false });
        window.addEventListener('touchmove', (e) => e.preventDefault(), { passive: false });
    }
    
    showStep(stepIndex) {
        const flow = this.flows[this.currentPage];
        if (!flow || stepIndex >= flow.length) return;
        
        const step = flow[stepIndex];
        this.currentStep = stepIndex;
        
        this.tooltip.querySelector('.tooltip-title').textContent = step.title;
        this.tooltip.querySelector('.tooltip-description').innerHTML = step.description;
        this.tooltip.querySelector('.current-step').textContent = stepIndex + 1;
        this.tooltip.querySelector('.total-steps').textContent = this.totalSteps;
        
        const progress = ((stepIndex + 1) / this.totalSteps) * 100;
        this.tooltip.querySelector('.progress-fill').style.width = `${progress}%`;
        
        this.tooltip.querySelector('.btn-prev').style.display = stepIndex === 0 ? 'none' : 'inline-block';
        const isLast = stepIndex === this.totalSteps - 1;
        this.tooltip.querySelector('.btn-next').textContent = isLast ? '✓ Finish' : 'Next →';
        
        // Add helpful hint for clickable elements
        const hint = this.tooltip.querySelector('.tooltip-highlight-hint');
        if (step.action) {
            hint.innerHTML = '<p class="text-xs text-blue-600 mt-3 flex items-center gap-2"><span>👆</span> Try clicking on the highlighted area</p>';
        } else {
            hint.innerHTML = '';
        }
        
        this.positionElements(step);
        this.tooltip.classList.add('active');
        
        if (step.action) step.action();
    }
    
    updateSpotlightPosition() {
        const flow = this.flows[this.currentPage];
        const step = flow[this.currentStep];
        if (step) {
            this.positionElements(step);
        }
    }
    
    scrollToElement(element) {
        if (!element) return;
        
        const rect = element.getBoundingClientRect();
        const isVisible = (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
        
        if (!isVisible) {
            // Calculate scroll position to center the element in viewport
            const elementTop = element.offsetTop;
            const elementHeight = element.offsetHeight;
            const windowHeight = window.innerHeight;
            const scrollTo = elementTop - (windowHeight / 2) + (elementHeight / 2);
            
            // Smooth scroll to element
            window.scrollTo({
                top: Math.max(0, scrollTo),
                behavior: 'smooth'
            });
            
            // Wait for scroll to complete before positioning spotlight
            setTimeout(() => {
                this.updateSpotlightPosition();
            }, 500);
        }
    }
    
    positionElements(step) {
        const target = step.selector ? document.querySelector(step.selector) : null;
        
        if (target && target.offsetParent !== null) {
            // Scroll to element if it's not visible or if step requires scrolling
            if (step.scrollToElement !== false) {
                this.scrollToElement(target);
            }
            
            const rect = target.getBoundingClientRect();
            const spotlight = this.overlay.querySelector('.onboarding-spotlight');
            const padding = step.padding || 12;
            
            spotlight.style.left = `${rect.left - padding}px`;
            spotlight.style.top = `${rect.top - padding}px`;
            spotlight.style.width = `${rect.width + padding * 2}px`;
            spotlight.style.height = `${rect.height + padding * 2}px`;
            spotlight.classList.add('pulse');
            
            this.positionTooltip(rect, step.position || 'bottom');
        } else {
            this.centerTooltip();
        }
    }
    
    positionTooltip(rect, position) {
        const tooltip = this.tooltip;
        const w = tooltip.offsetWidth;
        const h = tooltip.offsetHeight;
        const gap = 24;
        let left, top;
        
        const positions = {
            top: {
                left: rect.left + rect.width / 2 - w / 2,
                top: rect.top - h - gap
            },
            bottom: {
                left: rect.left + rect.width / 2 - w / 2,
                top: rect.bottom + gap
            },
            left: {
                left: rect.left - w - gap,
                top: rect.top + rect.height / 2 - h / 2
            },
            right: {
                left: rect.right + gap,
                top: rect.top + rect.height / 2 - h / 2
            }
        };
        
        ({ left, top } = positions[position]);
        
        left = Math.max(16, Math.min(left, window.innerWidth - w - 16));
        top = Math.max(16, Math.min(top, window.innerHeight - h - 16));
        
        tooltip.style.left = `${left}px`;
        tooltip.style.top = `${top}px`;
    }
    
    centerTooltip() {
        this.tooltip.style.left = '50%';
        this.tooltip.style.top = '50%';
        this.tooltip.style.transform = 'translate(-50%, -50%)';
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
        
        document.body.style.overflow = '';
        document.documentElement.style.overflow = '';
        
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
                <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center shadow-lg">
                    <span class="text-2xl">🎉</span>
                </div>
                <h3 class="text-2xl font-bold text-gray-900 mb-2">All Set!</h3>
                <p class="text-gray-600 mb-6">You're ready to manage your team like a pro</p>
                
                <div class="completion-tips bg-blue-50 rounded-lg p-4 mb-6 text-left border border-blue-200">
                    <p class="font-semibold text-blue-900 mb-3 text-sm">Quick wins to get started:</p>
                    <div class="space-y-2 text-sm text-blue-800">
                        <div class="flex items-start gap-2">
                            <span class="text-lg">👥</span>
                            <span>Add your first workers</span>
                        </div>
                        <div class="flex items-start gap-2">
                            <span class="text-lg">📋</span>
                            <span>Create a task and assign workers</span>
                        </div>
                        <div class="flex items-start gap-2">
                            <span class="text-lg">✅</span>
                            <span>Track attendance and generate reports</span>
                        </div>
                    </div>
                </div>
                
                <button class="btn-dismiss w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-all shadow-md">
                    Get Started
                </button>
            </div>
        `;
        
        document.body.appendChild(message);
        setTimeout(() => message.classList.add('active'), 50);
        
        message.querySelector('.btn-dismiss').addEventListener('click', () => {
            message.remove();
        });
        
        setTimeout(() => message.parentNode && message.remove(), 10000);
    }
    
    // ONBOARDING FLOWS
    
    getSignInFlow() {
        return [
            {
                title: "Welcome to Your Team Hub 🚀",
                description: "Let's get you set up in less than 2 minutes. We'll show you everything you need to manage your workforce effectively.",
                selector: null
            },
            {
                title: "Sign In or Create Account",
                description: "Use Google or email to sign in. New here? Create your company workspace right from this page.",
                selector: ".auth-container, .signin-form",
                position: "bottom",
                padding: 10
            },
            {
                title: "Join or Create Workspace",
                description: "Already have a team? Join with a workspace code. Otherwise, create a new workspace for your company.",
                selector: "[data-onboarding='workspace-section'], .workspace-section",
                position: "top",
                padding: 10
            }
        ];
    }
    
    getHomeFlow() {
        return [
            {
                title: "Your Dashboard 📊",
                description: "This is your mission control. See your team stats, active tasks, and access all features from here.",
                selector: ".dashboard-container, .hero-glass",
                padding: 8
            },
            {
                title: "Team Stats at a Glance",
                description: "Quick overview of workers, active tasks, and recent reports. Click any card to explore.",
                selector: "[data-onboarding='stats-container'], .stat-card",
                position: "bottom",
                padding: 8
            },
            {
                title: "Quick Actions",
                description: "Fast-track buttons to add workers, create tasks, or track attendance without navigating menus.",
                selector: "[data-onboarding='quick-actions'], .quick-action-btn",
                position: "top",
                padding: 8
            },
            {
                title: "Main Navigation",
                description: "Navigate between Workers, Tasks, Reports, and more. Each section has specialized tools for your needs.",
                selector: ".sidebar, .sidebar-container",
                position: "right",
                padding: 8
            }
        ];
    }
    
    getWorkersFlow() {
        return [
            {
                title: "Manage Your Team 👥",
                description: "Central hub for all your workers. Add, update, and organize your team in one place.",
                selector: ".workers-container, .page-container",
                padding: 8
            },
            {
                title: "Add New Workers",
                description: "Click to add individual workers with their contact info, rates, and availability.",
                selector: "[data-onboarding='add-worker-btn'], .btn-primary, .add-worker-btn",
                position: "bottom",
                padding: 8,
                action: () => {}
            },
            {
                title: "Your Workers List",
                description: "All workers in one view. Click any worker to edit details or view their task history.",
                selector: "[data-onboarding='workers-table'], .workers-table, table",
                position: "top",
                padding: 8
            },
            {
                title: "Bulk Import",
                description: "Add multiple workers at once by uploading an Excel spreadsheet. Saves tons of time!",
                selector: "[data-onboarding='import-btn'], .import-workers-btn",
                position: "bottom",
                padding: 8
            }
        ];
    }
    
    getTasksFlow() {
        return [
            {
                title: "Manage Tasks 📋",
                description: "Create projects, assign workers, and track completion all in one place.",
                selector: ".tasks-container, .page-container",
                padding: 8
            },
            {
                title: "Create New Task",
                description: "Set payment type (daily, hourly, or per-piece), add details, and assign workers.",
                selector: "[data-onboarding='create-task-btn'], .btn-primary, .create-task-btn",
                position: "bottom",
                padding: 8,
                action: () => {}
            },
            {
                title: "Task Status Overview",
                description: "See all tasks with their status: Pending, Active, or Completed.",
                selector: "[data-onboarding='tasks-table'], .tasks-table, table",
                position: "top",
                padding: 8
            },
            {
                title: "Record Attendance",
                description: "Click any task to mark workers present/absent and record hours or units worked. Enter units completed for piece-rate tasks or hours worked for hourly tasks to calculate accurate payments.",
                selector: "[data-onboarding='attendance-link'], .task-row a, .attendance-link",
                position: "right",
                padding: 8
            }
        ];
    }
    
    getReportsFlow() {
        return [
            {
                title: "Generate Reports 📈",
                description: "Create payroll, attendance, and performance reports for payouts and analysis.",
                selector: ".reports-container, .page-container",
                padding: 8
            },
            {
                title: "Report Types",
                description: "Choose how to calculate: Per Day, Per Hour, or Per Unit. Matches your payment structure.",
                selector: "[data-onboarding='report-types'], .report-type-selector, .report-tabs",
                position: "bottom",
                padding: 8
            },
            {
                title: "Select Date Range",
                description: "Pick your reporting period: daily, weekly, or custom date range.",
                selector: "[data-onboarding='date-range'], .date-inputs, .date-picker",
                position: "top",
                padding: 8
            },
            {
                title: "Export & Download",
                description: "Download as CSV or Excel for accounting, payroll, or record-keeping.",
                selector: "[data-onboarding='export-buttons'], .export-options, .download-btn",
                position: "left",
                padding: 8,
                scrollToElement: true
            }
        ];
    }
    
    getAttendanceFlow() {
        return [
            {
                title: "Track Attendance ✅",
                description: "Record who showed up and track hours/units for accurate payment calculation.",
                selector: ".attendance-container, .page-container",
                padding: 8
            },
            {
                title: "Worker List",
                description: "All workers assigned to this task. Each row shows status and performance.",
                selector: "[data-onboarding='attendance-table'], .attendance-table, table",
                position: "top",
                padding: 8
            },
            {
                title: "Mark Attendance",
                description: "Check the box for present workers. Only marked workers will be paid for this task.",
                selector: "[data-onboarding='attendance-checkbox'], input[type='checkbox'], .attendance-status",
                position: "right",
                padding: 8
            },
            {
                title: "Record Work Done",
                description: "Enter hours (e.g., 8.5) or units (e.g., 50) completed. Used for payment calculation.",
                selector: "[data-onboarding='hours-input'], input[name*='hours'], .hours-input",
                position: "bottom",
                padding: 8
            },
            {
                title: "Save & Calculate",
                description: "Save all data. Payments calculate automatically based on your rates.",
                selector: "[data-onboarding='save-attendance'], .btn-primary, .save-btn",
                position: "bottom",
                padding: 8,
                action: () => {}
            }
        ];
    }
    
    restartOnboarding() {
        localStorage.removeItem('embee_onboarding_completed');
        sessionStorage.removeItem('embee_onboarding_completed');
        this.startOnboarding();
    }
    
    skipOnboarding() {
        this.endOnboarding();
    }
    
    startOnboardingForPage(pageName) {
        if (this.flows[pageName]) {
            this.currentPage = pageName;
            this.startOnboarding();
        }
    }
}

// Enhanced CSS Styles with Beautiful Aesthetics
const onboardingStyles = `
    @keyframes slideUp {
        from { 
            opacity: 0; 
            transform: translateY(20px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    @keyframes pulse {
        0%, 100% { 
            box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.8),
                        0 0 20px 0 rgba(59, 130, 246, 0.4); 
        }
        50% { 
            box-shadow: 0 0 0 12px rgba(59, 130, 246, 0),
                        0 0 30px 5px rgba(59, 130, 246, 0.2); 
        }
    }
    
    @keyframes glow {
        0%, 100% { 
            filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.6));
        }
        50% { 
            filter: drop-shadow(0 0 16px rgba(59, 130, 246, 0.8));
        }
    }
    
    .onboarding-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 10000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.5s cubic-bezier(0.4, 0, 0.2, 1);
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
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
    }
    
    .onboarding-spotlight {
        position: absolute;
        background: transparent;
        border-radius: 20px;
        box-shadow: 0 0 0 9999px rgba(15, 23, 42, 0.85);
        border: 3px solid #3b82f6;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 10001;
        animation: glow 2s ease-in-out infinite;
    }
    
    .onboarding-spotlight.pulse {
        animation: pulse 2s infinite, glow 2s ease-in-out infinite;
    }
    
    .onboarding-tooltip {
        position: fixed;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 24px;
        box-shadow: 0 25px 60px rgba(30, 58, 138, 0.25),
                    0 10px 30px rgba(59, 130, 246, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9);
        max-width: 420px;
        min-width: 320px;
        z-index: 10002;
        opacity: 0;
        transform: translateY(10px) scale(0.95);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: all;
        border: 2px solid rgba(59, 130, 246, 0.2);
        overflow: hidden;
    }
    
    .onboarding-tooltip.active {
        opacity: 1;
        transform: translateY(0) scale(1);
        animation: fadeIn 0.4s ease;
    }
    
    .tooltip-content {
        padding: 28px;
        position: relative;
        background: transparent;
    }
    
    .tooltip-content::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, 
            #3b82f6 0%, 
            #06b6d4 25%, 
            #8b5cf6 50%, 
            #06b6d4 75%, 
            #3b82f6 100%);
        background-size: 200% 100%;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .tooltip-header {
        margin-bottom: 20px;
    }
    
    .tooltip-title {
        font-size: 20px;
        font-weight: 800;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.4;
        letter-spacing: -0.02em;
    }
    
    .progress-bar {
        width: 100%;
        height: 6px;
        background: linear-gradient(90deg, #e0e7ff 0%, #dbeafe 100%);
        border-radius: 10px;
        overflow: hidden;
        margin-top: 14px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 50%, #8b5cf6 100%);
        background-size: 200% 100%;
        transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 10px;
        animation: shimmer 2s ease-in-out infinite;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.4);
    }
    
    .tooltip-description {
        font-size: 15px;
        line-height: 1.7;
        color: #475569;
        margin: 0 0 12px 0;
        font-weight: 400;
    }
    
    .tooltip-highlight-hint {
        margin-bottom: 6px;
    }
    
    .tooltip-highlight-hint p {
        color: #2563eb;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        padding: 10px 14px;
        border-radius: 12px;
        border: 1px solid #bfdbfe;
        font-weight: 500;
    }
    
    .tooltip-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-top: 24px;
    }
    
    .btn-skip {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border: 2px solid #cbd5e1;
        color: #64748b;
        font-size: 13px;
        cursor: pointer;
        padding: 10px 18px;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 600;
        text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8);
    }
    
    .btn-skip:hover {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
        color: #475569;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(100, 116, 139, 0.2);
    }
    
    .nav-buttons {
        display: flex;
        gap: 10px;
    }
    
    .btn-prev, .btn-next {
        padding: 10px 20px;
        border-radius: 14px;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
        letter-spacing: 0.01em;
    }
    
    .btn-prev {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        color: #1e40af;
        border: 2px solid #93c5fd;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
    }
    
    .btn-prev:hover {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e3a8a;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.25);
    }
    
    .btn-next {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: 2px solid #2563eb;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
    }
    
    .btn-next:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.5);
    }
    
    .btn-next:active, .btn-prev:active {
        transform: translateY(0);
    }
    
    .onboarding-completion {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 28px;
        padding: 40px;
        max-width: 520px;
        text-align: center;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.25),
                    0 10px 30px rgba(59, 130, 246, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9);
        z-index: 10003;
        opacity: 0;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid rgba(59, 130, 246, 0.2);
    }
    
    .onboarding-completion.active {
        opacity: 1;
        animation: slideUp 0.5s ease;
    }
    
    .completion-content h3 {
        font-size: 28px;
        color: #0f172a;
        margin: 0 0 10px 0;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    
    .completion-content p {
        color: #64748b;
        margin: 0 0 24px 0;
        line-height: 1.6;
        font-size: 15px;
    }
    
    .completion-tips {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 2px solid #bfdbfe;
        border-radius: 18px;
        padding: 24px;
        margin: 28px 0;
        text-align: left;
        box-shadow: inset 0 2px 8px rgba(59, 130, 246, 0.1);
    }
    
    .completion-tips p {
        color: #1e40af;
        font-weight: 700;
        margin: 0 0 16px 0;
        font-size: 15px;
    }
    
    .completion-tips .space-y-2 {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .completion-tips .flex {
        background: white;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #bfdbfe;
        transition: all 0.2s;
    }
    
    .completion-tips .flex:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    
    .btn-dismiss {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: 2px solid #2563eb;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35);
        font-weight: 700;
        letter-spacing: 0.01em;
    }
    
    .btn-dismiss:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(37, 99, 235, 0.45);
    }
    
    .onboarding-help-button {
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
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4),
                    0 4px 12px rgba(6, 182, 212, 0.3);
        z-index: 1000;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
        border: 3px solid rgba(255, 255, 255, 0.9);
    }
    
    .onboarding-help-button::before {
        content: '';
        position: absolute;
        inset: -6px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .onboarding-help-button:hover {
        transform: translateY(-6px) scale(1.1) rotate(5deg);
        box-shadow: 0 16px 36px rgba(59, 130, 246, 0.5),
                    0 8px 20px rgba(6, 182, 212, 0.4);
    }
    
    .onboarding-help-button:hover::before {
        opacity: 0.5;
        animation: pulse 1.5s infinite;
    }
    
    .onboarding-help-button:active {
        transform: translateY(-3px) scale(1.05) rotate(5deg);
    }
    
    .onboarding-help-button.hidden {
        opacity: 0;
        pointer-events: none;
        transform: translateY(30px) scale(0.7);
    }
    
    @media (max-width: 768px) {
        .onboarding-tooltip {
            max-width: 88vw;
            min-width: 260px;
        }
        
        .tooltip-content {
            padding: 20px;
        }
        
        .tooltip-title {
            font-size: 16px;
        }
        
        .tooltip-description {
            font-size: 13px;
        }
        
        .tooltip-actions {
            flex-direction: column;
            gap: 10px;
        }
        
        .btn-skip {
            width: 100%;
        }
        
        .nav-buttons {
            width: 100%;
            gap: 10px;
        }
        
        .btn-prev, .btn-next {
            flex: 1;
            padding: 10px 12px;
            font-size: 12px;
        }
        
        .onboarding-completion {
            max-width: 88vw;
            padding: 24px 20px;
        }
        
        .completion-tips {
            padding: 16px;
        }
        
        #welcome-message .bg-white {
            padding: 24px;
        }
    }
    
    @media (max-width: 480px) {
        .onboarding-help-button {
            width: 48px;
            height: 48px;
            font-size: 18px;
            bottom: 16px;
            right: 16px;
        }
        
        .tooltip-title {
            font-size: 15px;
        }
        
        .btn-prev, .btn-next {
            padding: 8px 10px;
            font-size: 11px;
        }
    }
`;

// Initialize onboarding when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const styleSheet = document.createElement('style');
    styleSheet.textContent = onboardingStyles;
    document.head.appendChild(styleSheet);
    
    window.onboardingSystem = new EnhancedOnboardingSystem();
    addHelpButton();
});

function addHelpButton() {
    const helpButton = document.createElement('button');
    helpButton.className = 'onboarding-help-button';
    helpButton.innerHTML = '<i class="fas fa-question"></i>';
    helpButton.title = 'Replay tour - Learn how to use all features';
    helpButton.setAttribute('aria-label', 'Start onboarding tour');
    
    helpButton.addEventListener('click', (e) => {
        e.preventDefault();
        if (window.onboardingSystem) {
            window.onboardingSystem.restartOnboarding();
        }
    });
    
    document.body.appendChild(helpButton);
    
    const observer = new MutationObserver(() => {
        if (window.onboardingSystem?.isActive) {
            helpButton.classList.add('hidden');
        } else {
            helpButton.classList.remove('hidden');
        }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
}

window.EnhancedOnboardingSystem = EnhancedOnboardingSystem;