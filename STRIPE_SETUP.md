# Stripe Integration Setup

## Overview

This application now includes Stripe integration for subscription management. When a user's free trial expires, they will be prompted to subscribe to continue using the service.

## Features

- 30-day free trial for new workspaces
- Subscription required after trial expiration
- Stripe webhook integration for subscription events
- One-time trial extension option
- Automatic subscription status updates

## Environment Variables

**IMPORTANT SECURITY NOTE:** Never commit API keys to your repository. Always use environment variables.

Add these to your environment variables (for production) or `.env` file (for development):

```
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

Copy `.env.template` to `.env` and fill in your actual Stripe keys from your Stripe dashboard.

## Webhook Setup

1. **Create Webhook Endpoint in Stripe Dashboard:**
   - Go to Developers > Webhooks in your Stripe dashboard
   - Click "Add endpoint"
   - URL: `https://your-domain.com/stripe/webhook`
   - Select these events:
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`

2. **Copy Webhook Secret:**
   - After creating the webhook, copy the signing secret
   - Add it to your environment as `STRIPE_WEBHOOK_SECRET`

## How It Works

### Trial Management
1. New workspaces get a 30-day free trial
2. Trial countdown is displayed on the home dashboard
3. When trial expires, users see a subscription required page
4. Users can request a one-time 3-day extension

### Subscription Flow
1. User clicks "Upgrade Now" → Creates Stripe checkout session
2. User completes payment in Stripe → Redirected to success page
3. Webhook updates subscription status in database
4. User gains full access to all features

### Access Control
- Routes are protected with `@subscription_required` decorator
- Expired trials without subscription get 402 Payment Required
- API endpoints return appropriate error responses
- Frontend shows upgrade prompts and handles expired states

### Database Fields

The `Workspace` model includes:
- `subscription_status`: 'trial', 'active', 'canceled', 'past_due', 'trial_extended'
- `stripe_customer_id`: Stripe customer ID
- `stripe_subscription_id`: Stripe subscription ID
- `trial_end_date`: When trial expires
- `subscription_end_date`: When subscription expires

## Testing

For testing with Stripe test mode:
1. Use test card numbers (4242 4242 4242 4242)
2. Trigger webhooks manually in Stripe dashboard
3. Check logs for webhook processing

## Production Deployment

1. Replace test keys with live keys
2. Update webhook endpoint URL to production domain
3. Set up proper error monitoring for webhook failures
4. Consider implementing retry logic for failed webhook events
