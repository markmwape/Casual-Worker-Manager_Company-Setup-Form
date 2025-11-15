# Casual Worker Manager - Complete Onboarding Tour Guide

## Overview
This comprehensive onboarding tour guides new users through all main features of the Casual Worker Manager platform, from sign-in to advanced functionality. The tour excludes billing/payment features and focuses on core workforce management capabilities.

## Tour Structure

### 🎯 **Trial Timer Information**
Throughout the tour, users are informed about their trial period and what happens when it expires:
- Real-time countdown timer shows remaining trial time
- Clear explanation that a subscription is required after trial expiration
- Non-intrusive reminders about trial limitations

---

## 📋 **Page-by-Page Onboarding Steps**

### 1. 🔐 **Sign-In Page** (3 steps)

**Purpose**: Welcome users and guide them through authentication and workspace setup.

| Step | Tooltip Title | Tooltip Description | Target Element | Position |
|------|---------------|-------------------|----------------|----------|
| 1 | Welcome to Casual Worker Manager! | This powerful platform helps you manage your casual workforce efficiently. Let's start with a quick tour to show you everything you need to know about managing workers, tasks, and reports. | `null` (centered) | center |
| 2 | Sign In to Get Started | Use your Google account or email to sign in. If you're new, you can create a workspace for your company right here. This is where your workforce management journey begins! | `.auth-container, .signin-form` | bottom |
| 3 | Join or Create Your Workspace | If you have a workspace code from your team, enter it here to join an existing workspace. Otherwise, create a new workspace for your organization to start fresh. | `[data-onboarding='workspace-section'], .workspace-section` | top |

**Best Practices**: 
- Ensure users understand the workspace concept
- Highlight both joining existing workspaces and creating new ones

---

### 2. 🏠 **Home Dashboard** (6 steps)

**Purpose**: Introduce the main control center where users get an overview of their workforce operations.

| Step | Tooltip Title | Tooltip Description | Target Element | Position |
|------|---------------|-------------------|----------------|----------|
| 1 | Welcome to Your Dashboard! | This is your control center where you can see an overview of your workers, tasks, and business metrics at a glance. Everything you need to manage your workforce is accessible from here. | `.dashboard-container, .hero-glass` | center |
| 2 | Quick Stats Overview | These cards show your key metrics - total workers, active tasks, and reports. Click any card to navigate directly to that section and manage your workforce data. | `[data-onboarding='stats-container'], .stat-card` | bottom |
| 3 | Quick Actions | Use these buttons to quickly add new workers, create tasks, or record attendance without navigating to other pages. These shortcuts save you time in daily operations. | `[data-onboarding='quick-actions'], .quick-action-btn` | top |
| 4 | Navigation Sidebar | Use the sidebar to navigate between different sections: Dashboard (home), Workers (team management), Tasks (project management), and Reports (analytics). Each section has specialized tools for managing your business. | `.sidebar, .sidebar-container` | right |
| 5 | Team Members | See who has access to your workspace and their roles. If you're an admin, you can add new team members and manage their permissions here. | `[data-onboarding='team-section'], .team-table` | top |
| 6 | Trial Information | Keep track of your trial period here. You can see how much time is remaining and upgrade your plan when needed. The timer shows exactly when your trial expires. | `.subscription-success-alert, .trial-info, #trial-info` | bottom |

**Best Practices**:
- Emphasize the dashboard as the central hub
- Show how stats cards provide quick navigation
- Explain trial limitations clearly but positively

---

### 3. 👥 **Workers Page** (6 steps)

**Purpose**: Guide users through comprehensive worker management features.

| Step | Tooltip Title | Tooltip Description | Target Element | Position |
|------|---------------|-------------------|----------------|----------|
| 1 | Worker Management Hub | This is your central place for managing all workers. Here you can add new team members, view their details, organize your workforce, and track their information efficiently. | `.workers-container, .page-container` | center |
| 2 | Add New Workers | Click this button to add individual workers to your team. You can enter their personal details, contact information, and any custom fields specific to your business needs. | `[data-onboarding='add-worker-btn'], .btn-primary, .add-worker-btn` | bottom |
| 3 | Workers List | All your workers are displayed here with their information. You can search for specific workers, filter the list, and click on any worker to edit their details or view their work history. | `[data-onboarding='workers-table'], .workers-table, table` | top |
| 4 | Search and Filter Workers | Use these tools to quickly find specific workers or filter your team by different criteria. This is especially useful when you have a large workforce to manage. | `[data-onboarding='search-workers'], .search-input, input[type='search']` | bottom |
| 5 | Custom Fields | Create custom fields to capture additional information about your workers that's specific to your business. This could include skills, certifications, or any other relevant data. | `[data-onboarding='custom-fields'], .custom-fields-section` | left |
| 6 | Import Workers from Excel | Save time by importing multiple workers at once from an Excel spreadsheet. The system will guide you through mapping your data columns to worker information fields. | `[data-onboarding='import-btn'], .import-workers-btn` | bottom |

**Best Practices**:
- Highlight both individual and bulk worker addition
- Emphasize search and organization features
- Show flexibility with custom fields

---

### 4. 📋 **Tasks Page** (6 steps)

**Purpose**: Demonstrate task creation, management, and worker assignment capabilities.

| Step | Tooltip Title | Tooltip Description | Target Element | Position |
|------|---------------|-------------------|----------------|----------|
| 1 | Task Management Center | Create and manage all your work projects here. You can assign workers to tasks, set deadlines, define payment structures, and track progress efficiently across all your projects. | `.tasks-container, .page-container` | center |
| 2 | Create New Tasks | Click here to create a new task or project. You can set different payment types (daily rate, hourly rate, or piece-rate work), assign specific workers, and set schedules and deadlines. | `[data-onboarding='create-task-btn'], .btn-primary, .create-task-btn` | bottom |
| 3 | Task List & Status Tracking | View all your tasks with their current status: Pending (not started), In Progress (currently running), or Completed (finished). Tasks automatically update their status based on start dates and completion. | `[data-onboarding='tasks-table'], .tasks-table, table` | top |
| 4 | Payment Structure Options | Tasks support different payment structures to match your business needs: daily rates (fixed amount per day), hourly rates (payment per hour worked), or piece-rate work (payment per unit completed). | `[data-onboarding='payment-types'], .payment-type-selector` | left |
| 5 | Track Worker Attendance | Click on any task to track worker attendance and productivity. You can record who showed up, how many hours they worked, or how many units they completed for accurate payment calculation. | `[data-onboarding='attendance-link'], .task-row a, .attendance-link` | right |
| 6 | Assign Workers to Tasks | Select which workers will be part of each task. You can assign multiple workers to a single task and track their individual performance and attendance separately. | `[data-onboarding='assign-workers'], .worker-assignment` | top |

**Best Practices**:
- Explain different payment models clearly
- Show the connection between tasks and attendance tracking
- Highlight flexibility in worker assignment

---

### 5. 📈 **Reports Page** (6 steps)

**Purpose**: Guide users through report generation, filtering, and export capabilities.

| Step | Tooltip Title | Tooltip Description | Target Element | Position |
|------|---------------|-------------------|----------------|----------|
| 1 | Reports & Analytics Hub | Generate comprehensive reports for payroll processing, attendance tracking, and productivity analysis. Export your data in various formats for accounting software or team sharing. | `.reports-container, .page-container` | center |
| 2 | Report Type Selection | Choose from different report types based on your payment structure: 'Per Day' reports for daily-rate workers, 'Per Part' for piece-rate work, or 'Per Hour' for hourly workers. Each type provides relevant calculations. | `[data-onboarding='report-types'], .report-type-selector, .report-tabs` | bottom |
| 3 | Date Range Selection | Select the specific date range for your report. You can generate reports for daily, weekly, monthly, or custom periods to match your payroll cycles and business needs. | `[data-onboarding='date-range'], .date-inputs, .date-picker` | top |
| 4 | Filter Options | Use filters to narrow down your reports by specific workers, tasks, or other criteria. This helps you generate focused reports for specific teams or projects. | `[data-onboarding='report-filters'], .filter-section` | left |
| 5 | Export and Download | Download your reports in CSV or Excel format. These files are perfect for importing into accounting software like Excel, QuickBooks, or for sharing with your accounting team. | `[data-onboarding='export-buttons'], .export-options, .download-btn` | left |
| 6 | Custom Report Fields | Add custom calculations and additional fields to your reports to match your specific business requirements and payment structures. Customize reports to show exactly what you need. | `[data-onboarding='custom-fields-report'], .custom-report-fields` | right |

**Best Practices**:
- Connect report types to payment structures
- Emphasize integration with accounting software
- Show customization capabilities

---

### 6. ✅ **Attendance Tracking Page** (8 steps)

**Purpose**: Detailed guidance on recording worker attendance and calculating payments.

| Step | Tooltip Title | Tooltip Description | Target Element | Position |
|------|---------------|-------------------|----------------|----------|
| 1 | Task Attendance Tracking | This is where you record worker attendance and track productivity for specific tasks. You can manage who showed up, hours worked, units completed, and calculate accurate payments. | `.attendance-container, .page-container` | center |
| 2 | Worker Attendance List | All workers assigned to this task are listed here. You can see their attendance status, hours worked, and units completed at a glance. Each row represents one worker's performance for this task. | `[data-onboarding='attendance-table'], .attendance-table, table` | top |
| 3 | Mark Attendance Status | Use these checkboxes to mark workers as Present, Absent, or Late. Only workers marked as present can have hours or units recorded, ensuring accurate payment calculations. | `[data-onboarding='attendance-checkbox'], input[type='checkbox'], .attendance-status` | right |
| 4 | Record Hours Worked | For hourly-paid tasks, enter the exact hours each worker worked. You can use decimal format (e.g., 8.5 for 8 hours 30 minutes). This directly affects their payment calculation. | `[data-onboarding='hours-input'], input[name*='hours'], .hours-input` | bottom |
| 5 | Track Units Completed | For piece-rate work, enter how many units each worker completed (e.g., pieces produced, tasks finished, items assembled). Payment is automatically calculated as units × rate per unit. | `[data-onboarding='units-input'], input[name*='units'], .units-input` | top |
| 6 | Save Attendance Data | Click this button to save all attendance, hours, and units data. The system will automatically calculate payments based on the task's payment structure (daily, hourly, or piece-rate). | `[data-onboarding='save-attendance'], .btn-primary, .save-btn` | bottom |
| 7 | Real-time Payment Preview | See live payment calculations as you enter data. This shows how much each worker will earn based on their attendance, hours worked, or units completed, helping you verify accuracy. | `[data-onboarding='payment-preview'], .payment-calculation, .payment-summary` | left |
| 8 | Add Performance Notes | Add notes about worker performance, issues, or special circumstances. These notes help with future scheduling decisions and performance reviews. | `[data-onboarding='attendance-notes'], textarea[name*='notes'], .notes-section` | right |

**Best Practices**:
- Show real-time calculation feedback
- Explain different input methods for different payment types
- Emphasize accuracy in attendance recording

---

## 🎉 **Tour Complete Message**

**Final Step: Completion Celebration**

**Title**: "🎉 Onboarding Complete!"

**Message**: "You're now ready to manage your casual workers like a pro! Remember that your trial has limitations, and you'll need to upgrade when it expires to continue using all features."

**Quick Tips Included**:
- Start by adding your first workers
- Create tasks and assign workers to them
- Track attendance and generate reports
- Use the help button (?) anytime for guidance

**Action Buttons**:
- **Primary**: "Start Managing Workers" (dismisses and begins workflow)
- **Secondary**: "Replay Tour" (restarts the onboarding)

---

## 🛠 **Implementation Notes for Developers**

### For Intro.js Implementation:
```javascript
const steps = [
  {
    intro: "Welcome to Casual Worker Manager! This powerful platform helps you manage your casual workforce efficiently...",
    position: 'center'
  },
  {
    element: '.auth-container',
    intro: "Use your Google account or email to sign in...",
    position: 'bottom'
  }
  // ... continue with all steps
];
```

### For Shepherd.js Implementation:
```javascript
const tour = new Shepherd.Tour({
  steps: [
    {
      title: 'Welcome to Casual Worker Manager!',
      text: 'This powerful platform helps you manage your casual workforce efficiently...',
      buttons: [
        { text: 'Next', action: tour.next }
      ]
    }
    // ... continue with all steps
  ]
});
```

### For React Joyride Implementation:
```javascript
const steps = [
  {
    target: 'body',
    content: 'Welcome to Casual Worker Manager! This powerful platform helps you manage your casual workforce efficiently...',
    placement: 'center',
    disableBeacon: true,
  },
  {
    target: '.auth-container',
    content: 'Use your Google account or email to sign in...',
    placement: 'bottom',
  }
  // ... continue with all steps
];
```

---

## 📱 **Mobile Responsiveness**

The tour is fully optimized for mobile devices with:
- Responsive tooltip sizing
- Touch-friendly navigation buttons
- Adaptive positioning for small screens
- Readable font sizes on mobile

---

## ⚡ **Key Features**

- **Progressive Disclosure**: Information revealed step-by-step
- **Context-Aware**: Different tours for different pages
- **Trial-Aware**: Consistent messaging about trial limitations
- **Help Access**: Floating help button for tour restart
- **Keyboard Support**: ESC key to exit, arrow keys for navigation
- **Skip Options**: Users can skip individual steps or entire tour
- **Progress Tracking**: Visual progress bar and step counters
- **Celebration**: Engaging completion message with confetti

---

## 🎯 **Success Metrics**

Track these metrics to measure onboarding effectiveness:
- **Completion Rate**: % of users who complete the full tour
- **Drop-off Points**: Where users most commonly exit
- **Feature Adoption**: Usage of features introduced in tour
- **Time to First Value**: How quickly users complete first meaningful action
- **Help Button Usage**: How often users restart the tour

This comprehensive onboarding system ensures new users understand all core features while maintaining awareness of trial limitations and the need for eventual subscription upgrades.
