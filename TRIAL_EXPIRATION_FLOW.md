# What Happens When Trial Ends - Complete Flow

## Overview
When a user's trial expires, they are prevented from accessing most features and redirected to a subscription/upgrade page.

---

## Trial Expiration Detection

### Middleware: `subscription_required` (subscription_middleware.py)
This decorator is applied to **most routes** in the application and checks subscription status before allowing access.

```python
@subscription_required  # Applied to most routes
def some_protected_route():
    # Only accessible with valid trial or subscription
    pass
```

### Status Checking Logic

The `check_subscription_status()` function determines the workspace's status:

1. **Active Paid Subscription** ✅
   - Has Stripe subscription ID
   - `subscription_status == 'active'`
   - `subscription_end_date > now`
   - **Result:** Full access granted

2. **Trial Active** ✅
   - No paid subscription OR trial not ended
   - `trial_end_date > now` (more than 1 day left)
   - **Result:** Full access granted

3. **Trial Expiring Soon** ⚠️
   - `trial_end_date` is 0-1 days away
   - **Result:** Access granted BUT shows warning

4. **Trial Expired** ❌
   - `trial_end_date < now` (past the date)
   - No active paid subscription
   - **Result:** Access BLOCKED

5. **Subscription Past Due** ⚠️❌
   - Payment failed
   - 3-day grace period given
   - **Result:** 
     - Days 1-3: Access granted with warning
     - Day 4+: Access BLOCKED

6. **Subscription Canceled/Unpaid** ❌
   - `subscription_status` is 'canceled', 'unpaid', or 'incomplete'
   - **Result:** Access BLOCKED

---

## What Happens Step-by-Step

### When User Tries to Access Protected Page After Trial Expires:

```
1. User clicks on /home, /workers, /tasks, etc.
                    ↓
2. @subscription_required decorator runs
                    ↓
3. Checks: Is user authenticated? ✅
                    ↓
4. Gets workspace from session
                    ↓
5. Calls check_subscription_status(workspace)
                    ↓
6. Calculates: trial_end_date < now? ✅ (EXPIRED)
                    ↓
7. No active paid subscription? ✅
                    ↓
8. subscription_status returns 'expired'
                    ↓
9. For JSON/API requests:
   - Returns 402 Payment Required error
   - JSON: {"error": "Subscription required", "trial_expired": true}
                    ↓
10. For regular page requests:
    - Redirects to subscription_required.html page
    - Shows Stripe pricing table
    - Shows "Request 3-day extension" button (if not used)
```

---

## The Subscription Required Page

When trial expires, users see: `templates/subscription_required.html`

### Page Content:

1. **Header**
   - "Trial Expired"
   - "Your 30-day free trial has ended"

2. **Workspace Info**
   - Shows workspace name and code
   - Reminds them what features they'll keep

3. **Features List**
   - Full worker management access
   - Advanced reporting & analytics
   - Task assignment & tracking
   - Team collaboration tools
   - Attendance monitoring
   - Priority email support

4. **Stripe Pricing Table** (Embedded)
   - Shows all available plans:
     - **Starter**: 1-25 workers - $20/month
     - **Growth**: 26-100 workers - $50/month
     - **Enterprise**: 101-250 workers - $150/month
     - **Corporate**: 251-1,000 workers - $350/month
   - "Start trial" buttons for each tier
   - Direct payment through Stripe

5. **Manage Existing Billing Button**
   - Links to Stripe billing portal
   - For users who already subscribed

6. **3-Day Extension Option** (if available)
   - Shows button: "Request 3-day extension (one-time only)"
   - Only appears if `workspace.extension_used == False`
   - If already used, shows: "Trial extension has already been used"

---

## Routes That Are BLOCKED When Trial Expires

All routes with `@subscription_required` decorator:

### Main Pages:
- `/home` - Dashboard
- `/workers` - Worker management
- `/tasks` - Task management
- `/attendance` - Attendance tracking
- `/reports` - Reports and analytics
- `/settings` - Settings pages

### Worker Operations:
- `/add_worker` - Add new worker
- `/edit_worker/<id>` - Edit worker
- `/delete_worker/<id>` - Delete worker
- `/import_workers` - Bulk import

### Task Operations:
- `/add_task` - Create task
- `/edit_task/<id>` - Edit task
- `/delete_task/<id>` - Delete task

### Attendance Operations:
- `/mark_attendance` - Mark attendance
- `/attendance/<date>` - View attendance

### Report Operations:
- `/generate_report` - Generate reports
- `/export_report` - Export reports

### API Endpoints:
- Most `/api/*` endpoints that require workspace access

---

## Routes That STILL WORK When Trial Expires

Routes excluded from subscription check:

### Authentication:
- `/` - Landing page
- `/signin` - Sign in page
- `/finish-signin` - Auth callback
- `/logout` - Logout

### Workspace Management:
- `/api/workspace/create` - Create new workspace
- `/api/workspace/join` - Join existing workspace
- `/api/workspace/payments` - Check subscription info

### Legal Pages:
- `/terms-of-use` - Terms of service
- `/privacy-policy` - Privacy policy
- `/legal-compliance` - Legal compliance

### Stripe/Payment:
- `/stripe/webhook` - Stripe webhooks
- `/api/request-trial-extension` - Request extension ✅ (NEW)

---

## User Experience After Trial Expires

### Scenario 1: User Has Used Extension
```
Trial ends (30 days) → User sees subscription page
                     → Extension button NOT shown
                     → Must subscribe to continue
                     → Can choose any plan
                     → Payment through Stripe
                     → Immediate access after payment
```

### Scenario 2: User Has NOT Used Extension
```
Trial ends (30 days) → User sees subscription page
                     → "Request 3-day extension" button shown
                     → User clicks button
                     → Confirmation dialog appears
                     → Clicks "Confirm"
                     → Backend adds 3 days to trial_end_date
                     → Sets extension_used = True
                     → Redirects to /home
                     → User has 3 more days
                     → After 3 days: Must subscribe (no more extensions)
```

### Scenario 3: User Subscribes
```
Trial expired → Clicks pricing plan
             → Stripe checkout opens
             → Enters payment info
             → Payment succeeds
             → Stripe webhook notifies server
             → Server updates workspace:
                 - stripe_subscription_id = <id>
                 - subscription_status = 'active'
                 - subscription_tier = <selected tier>
                 - trial_end_date = None
                 - subscription_end_date = <30 or 365 days>
             → User automatically gets access
             → Redirected to /home
             → Full access restored
```

---

## Database Fields Tracking Trial Status

### Workspace Table:
```sql
- trial_end_date (DATETIME)
  → When the trial period ends
  → NULL = no trial or trial cleared (paid user)

- extension_used (BOOLEAN)
  → TRUE = User already used their 3-day extension
  → FALSE = Extension still available

- subscription_status (VARCHAR)
  → 'trial' = On trial period
  → 'active' = Active paid subscription
  → 'past_due' = Payment failed
  → 'canceled' = Subscription canceled

- stripe_subscription_id (VARCHAR)
  → Stripe subscription ID (if they paid)
  → NULL = Never subscribed

- subscription_end_date (DATETIME)
  → When paid subscription ends
  → Used for renewals
```

---

## Grace Periods

### Trial Extension: 3 Days
- One-time only
- User-requested
- Must be on trial (not expired paid subscription)

### Payment Failed Grace: 3 Days
- Automatic
- For paid subscribers whose payment failed
- After 3 days: Access revoked

---

## Recovery Options for Expired Users

1. **Subscribe** - Choose any plan and pay
2. **Request Extension** - One-time 3-day extension (if not used)
3. **Contact Support** - Email support for special cases
4. **Manage Billing** - Update payment method if subscription failed

---

## Summary

**In short:**
- **Trial ends** → User can't access most features
- **Redirected** → To subscription_required.html page
- **Options shown:**
  1. Subscribe to a plan (via Stripe)
  2. Request 3-day extension (one-time)
  3. Manage existing billing
- **After payment** → Immediate access restored
- **No payment** → Workspace remains locked

The system is designed to be **clear, fair, and flexible** - giving users multiple chances to continue with a 30-day trial + optional 3-day extension before requiring payment.
