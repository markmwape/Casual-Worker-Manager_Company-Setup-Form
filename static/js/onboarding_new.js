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
            <div id="welcome-message" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
                <div class="bg-white rounded-lg p-6 m-4 max-w-md text-center shadow-xl">
                    <div class="text-4xl mb-4">👋</div>
                    <h2 class="text-xl font-bold mb-2">Welcome to Casual Worker Manager!</h2>
                    <p class="text-gray-600 mb-4">Let us show you around with a quick guided tour to help you get started with managing your workforce effectively.</p>
                    <div class="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                        <div class="flex items-center gap-2 text-blue-800">
                            <i class="fas fa-clock"></i>
                            <span class="font-semibold">About Your Trial</span>
                        </div>
                        <p class="text-sm text-blue-700 mt-1">You're currently on a free trial. When your trial period ends, you'll need to choose a subscription plan to continue using all features.</p>
                    </div>
                    <div class="flex gap-2 justify-center">
                        <button id="start-tour-btn" class="btn btn-primary">Start Tour</button>
                        <button id="skip-tour-btn" class="btn btn-outline">Skip for Now</button>
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
                    <h3 class="tooltip-title"></h3>
                    <div class="tooltip-progress">
                        <span class="progress-text">Step <span class="current-step">1</span> of <span class="total-steps">1</span></span>
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                    </div>
                </div>
                <div class="tooltip-body">
                    <p class="tooltip-description"></p>
                    <div class="tooltip-actions">
                        <button class="btn-skip">Skip Tour</button>
                        <div class="nav-buttons">
                            <button class="btn-prev">Previous</button>
                            <button class="btn-next">Next</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="tooltip-arrow"></div>
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
                <div class="completion-animation">
                    <div class="success-checkmark">
                        <div class="check-icon">
                            <span class="icon-line line-tip"></span>
                            <span class="icon-line line-long"></span>
                            <div class="icon-circle"></div>
                            <div class="icon-fix"></div>
                        </div>
                    </div>
                </div>
                <h3>🎉 Onboarding Complete!</h3>
                <p>You're now ready to manage your casual workers like a pro! Remember that your trial has limitations, and you'll need to upgrade when it expires to continue using all features.</p>
                <div class="completion-tips">
                    <p><strong>💡 Quick Tips:</strong></p>
                    <ul class="text-left mt-2 space-y-1">
                        <li>• Start by adding your first workers</li>
                        <li>• Create tasks and assign workers to them</li>
                        <li>• Track attendance and generate reports</li>
                        <li>• Use the help button (?) anytime for guidance</li>
                    </ul>
                </div>
                <div class="completion-actions">
                    <button class="btn-dismiss">Start Managing Workers</button>
                    <button class="btn-replay" onclick="window.onboardingSystem?.restartOnboarding()">Replay Tour</button>
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
                title: "Welcome to Casual Worker Manager!",
                description: "This powerful platform helps you manage your casual workforce efficiently. Let's start with a quick tour to show you everything you need to know about managing workers, tasks, and reports.",
                selector: null
            },
            {
                title: "Sign In to Get Started",
                description: "Use your Google account or email to sign in. If you're new, you can create a workspace for your company right here. This is where your workforce management journey begins!",
                selector: ".auth-container, .signin-form",
                position: "bottom"
            },
            {
                title: "Join or Create Your Workspace",
                description: "If you have a workspace code from your team, enter it here to join an existing workspace. Otherwise, create a new workspace for your organization to start fresh.",
                selector: "[data-onboarding='workspace-section'], .workspace-section",
                position: "top"
            }
        ];
    }
    
    getHomeFlow() {
        return [
            {
                title: "Welcome to Your Dashboard!",
                description: "This is your control center where you can see an overview of your workers, tasks, and business metrics at a glance. Everything you need to manage your workforce is accessible from here.",
                selector: ".dashboard-container, .hero-glass"
            },
            {
                title: "Quick Stats Overview",
                description: "These cards show your key metrics - total workers, active tasks, and reports. Click any card to navigate directly to that section and manage your workforce data.",
                selector: "[data-onboarding='stats-container'], .stat-card",
                position: "bottom"
            },
            {
                title: "Quick Actions",
                description: "Use these buttons to quickly add new workers, create tasks, or record attendance without navigating to other pages. These shortcuts save you time in daily operations.",
                selector: "[data-onboarding='quick-actions'], .quick-action-btn",
                position: "top"
            },
            {
                title: "Navigation Sidebar",
                description: "Use the sidebar to navigate between different sections: Dashboard (home), Workers (team management), Tasks (project management), and Reports (analytics). Each section has specialized tools for managing your business.",
                selector: ".sidebar, .sidebar-container",
                position: "right"
            },
            {
                title: "Team Members",
                description: "See who has access to your workspace and their roles. If you're an admin, you can add new team members and manage their permissions here.",
                selector: "[data-onboarding='team-section'], .team-table",
                position: "top"
            },
            {
                title: "Trial Information",
                description: "Keep track of your trial period here. You can see how much time is remaining and upgrade your plan when needed. The timer shows exactly when your trial expires.",
                selector: ".subscription-success-alert, .trial-info, #trial-info",
                position: "bottom"
            }
        ];
    }
    
    getWorkersFlow() {
        return [
            {
                title: "Worker Management Hub",
                description: "This is your central place for managing all workers. Here you can add new team members, view their details, organize your workforce, and track their information efficiently.",
                selector: ".workers-container, .page-container"
            },
            {
                title: "Add New Workers",
                description: "Click this button to add individual workers to your team. You can enter their personal details, contact information, and any custom fields specific to your business needs.",
                selector: "[data-onboarding='add-worker-btn'], .btn-primary, .add-worker-btn",
                position: "bottom"
            },
            {
                title: "Workers List",
                description: "All your workers are displayed here with their information. You can search for specific workers, filter the list, and click on any worker to edit their details or view their work history.",
                selector: "[data-onboarding='workers-table'], .workers-table, table",
                position: "top"
            },
            {
                title: "Search and Filter Workers",
                description: "Use these tools to quickly find specific workers or filter your team by different criteria. This is especially useful when you have a large workforce to manage.",
                selector: "[data-onboarding='search-workers'], .search-input, input[type='search']",
                position: "bottom"
            },
            {
                title: "Custom Fields",
                description: "Create custom fields to capture additional information about your workers that's specific to your business. This could include skills, certifications, or any other relevant data.",
                selector: "[data-onboarding='custom-fields'], .custom-fields-section",
                position: "left"
            },
            {
                title: "Import Workers from Excel",
                description: "Save time by importing multiple workers at once from an Excel spreadsheet. The system will guide you through mapping your data columns to worker information fields.",
                selector: "[data-onboarding='import-btn'], .import-workers-btn",
                position: "bottom"
            }
        ];
    }
    
    getTasksFlow() {
        return [
            {
                title: "Task Management Center",
                description: "Create and manage all your work projects here. You can assign workers to tasks, set deadlines, define payment structures, and track progress efficiently across all your projects.",
                selector: ".tasks-container, .page-container"
            },
            {
                title: "Create New Tasks",
                description: "Click here to create a new task or project. You can set different payment types (daily rate, hourly rate, or piece-rate work), assign specific workers, and set schedules and deadlines.",
                selector: "[data-onboarding='create-task-btn'], .btn-primary, .create-task-btn",
                position: "bottom"
            },
            {
                title: "Task List & Status Tracking",
                description: "View all your tasks with their current status: Pending (not started), In Progress (currently running), or Completed (finished). Tasks automatically update their status based on start dates and completion.",
                selector: "[data-onboarding='tasks-table'], .tasks-table, table",
                position: "top"
            },
            {
                title: "Payment Structure Options",
                description: "Tasks support different payment structures to match your business needs: daily rates (fixed amount per day), hourly rates (payment per hour worked), or piece-rate work (payment per unit completed).",
                selector: "[data-onboarding='payment-types'], .payment-type-selector",
                position: "left"
            },
            {
                title: "Track Worker Attendance",
                description: "Click on any task to track worker attendance and productivity. You can record who showed up, how many hours they worked, or how many units they completed for accurate payment calculation.",
                selector: "[data-onboarding='attendance-link'], .task-row a, .attendance-link",
                position: "right"
            },
            {
                title: "Assign Workers to Tasks",
                description: "Select which workers will be part of each task. You can assign multiple workers to a single task and track their individual performance and attendance separately.",
                selector: "[data-onboarding='assign-workers'], .worker-assignment",
                position: "top"
            }
        ];
    }
    
    getReportsFlow() {
        return [
            {
                title: "Reports & Analytics Hub",
                description: "Generate comprehensive reports for payroll processing, attendance tracking, and productivity analysis. Export your data in various formats for accounting software or team sharing.",
                selector: ".reports-container, .page-container"
            },
            {
                title: "Report Type Selection",
                description: "Choose from different report types based on your payment structure: 'Per Day' reports for daily-rate workers, 'Per Part' for piece-rate work, or 'Per Hour' for hourly workers. Each type provides relevant calculations.",
                selector: "[data-onboarding='report-types'], .report-type-selector, .report-tabs",
                position: "bottom"
            },
            {
                title: "Date Range Selection",
                description: "Select the specific date range for your report. You can generate reports for daily, weekly, monthly, or custom periods to match your payroll cycles and business needs.",
                selector: "[data-onboarding='date-range'], .date-inputs, .date-picker",
                position: "top"
            },
            {
                title: "Filter Options",
                description: "Use filters to narrow down your reports by specific workers, tasks, or other criteria. This helps you generate focused reports for specific teams or projects.",
                selector: "[data-onboarding='report-filters'], .filter-section",
                position: "left"
            },
            {
                title: "Export and Download",
                description: "Download your reports in CSV or Excel format. These files are perfect for importing into accounting software like Excel, QuickBooks, or for sharing with your accounting team.",
                selector: "[data-onboarding='export-buttons'], .export-options, .download-btn",
                position: "left"
            },
            {
                title: "Custom Report Fields",
                description: "Add custom calculations and additional fields to your reports to match your specific business requirements and payment structures. Customize reports to show exactly what you need.",
                selector: "[data-onboarding='custom-fields-report'], .custom-report-fields",
                position: "right"
            }
        ];
    }
    
    getAttendanceFlow() {
        return [
            {
                title: "Task Attendance Tracking",
                description: "This is where you record worker attendance and track productivity for specific tasks. You can manage who showed up, hours worked, units completed, and calculate accurate payments.",
                selector: ".attendance-container, .page-container"
            },
            {
                title: "Worker Attendance List",
                description: "All workers assigned to this task are listed here. You can see their attendance status, hours worked, and units completed at a glance. Each row represents one worker's performance for this task.",
                selector: "[data-onboarding='attendance-table'], .attendance-table, table",
                position: "top"
            },
            {
                title: "Mark Attendance Status",
                description: "Use these checkboxes to mark workers as Present, Absent, or Late. Only workers marked as present can have hours or units recorded, ensuring accurate payment calculations.",
                selector: "[data-onboarding='attendance-checkbox'], input[type='checkbox'], .attendance-status",
                position: "right"
            },
            {
                title: "Record Hours Worked",
                description: "For hourly-paid tasks, enter the exact hours each worker worked. You can use decimal format (e.g., 8.5 for 8 hours 30 minutes). This directly affects their payment calculation.",
                selector: "[data-onboarding='hours-input'], input[name*='hours'], .hours-input",
                position: "bottom"
            },
            {
                title: "Track Units Completed",
                description: "For piece-rate work, enter how many units each worker completed (e.g., pieces produced, tasks finished, items assembled). Payment is automatically calculated as units × rate per unit.",
                selector: "[data-onboarding='units-input'], input[name*='units'], .units-input",
                position: "top"
            },
            {
                title: "Save Attendance Data",
                description: "Click this button to save all attendance, hours, and units data. The system will automatically calculate payments based on the task's payment structure (daily, hourly, or piece-rate).",
                selector: "[data-onboarding='save-attendance'], .btn-primary, .save-btn",
                position: "bottom"
            },
            {
                title: "Real-time Payment Preview",
                description: "See live payment calculations as you enter data. This shows how much each worker will earn based on their attendance, hours worked, or units completed, helping you verify accuracy.",
                selector: "[data-onboarding='payment-preview'], .payment-calculation, .payment-summary",
                position: "left"
            },
            {
                title: "Add Performance Notes",
                description: "Add notes about worker performance, issues, or special circumstances. These notes help with future scheduling decisions and performance reviews.",
                selector: "[data-onboarding='attendance-notes'], textarea[name*='notes'], .notes-section",
                position: "right"
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
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(2px);
    }
    
    .onboarding-spotlight {
        position: absolute;
        background: transparent;
        border-radius: 12px;
        box-shadow: 
            0 0 0 4px rgba(59, 130, 246, 0.5),
            0 0 0 9999px rgba(0, 0, 0, 0.75);
        pointer-events: none;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 10001;
        animation: spotlightPulse 2s ease-in-out infinite;
    }
    
    @keyframes spotlightPulse {
        0%, 100% {
            box-shadow: 
                0 0 0 4px rgba(59, 130, 246, 0.5),
                0 0 0 9999px rgba(0, 0, 0, 0.75);
        }
        50% {
            box-shadow: 
                0 0 0 8px rgba(59, 130, 246, 0.8),
                0 0 20px rgba(59, 130, 246, 0.6),
                0 0 0 9999px rgba(0, 0, 0, 0.75);
        }
    }
    
    .onboarding-tooltip {
        position: fixed;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e2e8f0;
        border-radius: 20px;
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.25),
            0 0 0 1px rgba(255, 255, 255, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        max-width: 450px;
        min-width: 350px;
        z-index: 10002;
        opacity: 0;
        transform: scale(0.8) translateY(-10px);
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        pointer-events: all;
        backdrop-filter: blur(10px);
    }
    
    .onboarding-tooltip.active {
        opacity: 1;
        transform: scale(1) translateY(0);
        animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3) translateY(-20px);
        }
        50% {
            opacity: 1;
            transform: scale(1.05) translateY(5px);
        }
        70% {
            transform: scale(0.95) translateY(-2px);
        }
        100% {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }
    
    .tooltip-content {
        padding: 28px;
        position: relative;
    }
    
    .tooltip-content::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
        border-radius: 20px 20px 0 0;
    }
    
    .tooltip-header {
        margin-bottom: 20px;
        margin-top: 8px;
    }
    
    .tooltip-title {
        font-size: 20px;
        font-weight: 700;
        background: linear-gradient(135deg, #1e293b 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 16px 0;
        line-height: 1.3;
    }
    
    .tooltip-progress {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .progress-text {
        font-size: 12px;
        color: #6B7280;
        font-weight: 500;
    }
    
    .progress-bar {
        width: 100px;
        height: 4px;
        background: #E5E7EB;
        border-radius: 2px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #1A2B48, #E5B23A);
        border-radius: 2px;
        transition: width 0.3s ease;
    }
    
    .tooltip-description {
        font-size: 14px;
        line-height: 1.6;
        color: #374151;
        margin: 0 0 20px 0;
    }
    
    .tooltip-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .btn-skip {
        background: none;
        border: 1px solid #e2e8f0;
        color: #64748b;
        font-size: 13px;
        cursor: pointer;
        padding: 8px 16px;
        border-radius: 12px;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .btn-skip:hover {
        background: #f1f5f9;
        color: #475569;
        border-color: #cbd5e1;
        transform: translateY(-1px);
    }
    
    .nav-buttons {
        display: flex;
        gap: 12px;
    }
    
    .btn-prev, .btn-next {
        padding: 12px 24px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
        position: relative;
        overflow: hidden;
    }
    
    .btn-prev {
        background: #f8fafc;
        color: #475569;
        border: 1px solid #e2e8f0;
    }
    
    .btn-prev:hover {
        background: #f1f5f9;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .btn-next {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    .btn-next:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.6);
    }
    
    .btn-next:active, .btn-prev:active {
        transform: translateY(0);
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
        transform: translate(-50%, -50%) scale(0.9);
        background: white;
        border-radius: 20px;
        padding: 40px;
        max-width: 500px;
        text-align: center;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        z-index: 10003;
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .onboarding-completion.active {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1);
    }
    
    .completion-content h3 {
        font-size: 24px;
        color: #1A2B48;
        margin: 0 0 12px 0;
    }
    
    .completion-content p {
        color: #6B7280;
        margin: 0 0 20px 0;
        line-height: 1.6;
    }
    
    .completion-tips {
        background: #f0f9ff;
        border: 2px solid #bae6fd;
        border-radius: 12px;
        padding: 16px;
        margin: 20px 0;
        text-align: left;
    }
    
    .completion-tips p {
        color: #0369a1;
        font-weight: 600;
        margin: 0 0 8px 0;
    }
    
    .completion-tips ul {
        color: #0284c7;
        font-size: 14px;
        line-height: 1.4;
    }
    
    .completion-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-top: 24px;
    }
    
    .btn-dismiss, .btn-replay {
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
    }
    
    .btn-dismiss {
        background: linear-gradient(135deg, #1A2B48, #E5B23A);
        color: white;
    }
    
    .btn-dismiss:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(26, 43, 72, 0.3);
    }
    
    .btn-replay {
        background: #f8fafc;
        color: #475569;
        border: 1px solid #e2e8f0;
    }
    
    .btn-replay:hover {
        background: #f1f5f9;
        transform: translateY(-1px);
    }
    
    /* Mobile responsive styles */
    @media (max-width: 768px) {
        .onboarding-tooltip {
            max-width: 90vw;
            min-width: 280px;
            margin: 20px;
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
            padding: 30px 20px;
        }
        
        .completion-actions {
            flex-direction: column;
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
