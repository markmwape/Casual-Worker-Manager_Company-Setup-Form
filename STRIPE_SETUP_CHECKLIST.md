# Stripe Setup Checklist

## ✅ Step 1: Get Your Stripe Keys

1. **Go to your Stripe Dashboard:** https://dashboard.stripe.com/
2. **Get your API keys:**
   - Go to "Developers" → "API Keys"
   - Copy your **Publishable key** (starts with `pk_test_` or `pk_live_`)
   - Copy your **Secret key** (starts with `sk_test_` or `sk_live_`)

## ✅ Step 2: Create a Product and Price

1. **Create a product:**
   - Go to "Products" → "Add product"
   - Name: "Professional Plan" (or whatever you want)
   - Price: $29/month (or your desired price)
   - Recurring: Monthly
   - Save the product

2. **Copy the Price ID:**
   - After creating, you'll see a Price ID (starts with `price_`)
   - Copy this ID - you'll need it for the checkout session

## ✅ Step 3: Set up Webhook

1. **Create webhook endpoint:**
   - Go to "Developers" → "Webhooks"
   - Click "Add endpoint"
   - Endpoint URL: `https://your-actual-domain.com/stripe/webhook`
   - Select these events:
     - ✅ `customer.subscription.created`
     - ✅ `customer.subscription.updated` 
     - ✅ `customer.subscription.deleted`
     - ✅ `invoice.payment_succeeded`
     - ✅ `invoice.payment_failed`
   - Click "Add endpoint"

2. **Copy Webhook Secret:**
   - Click on your newly created webhook
   - Copy the "Signing secret" (starts with `whsec_`)

## ✅ Step 4: Update Your .env File

Edit your `.env` file with your actual values:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_actual_webhook_secret_here

# App Configuration  
APP_BASE_URL=https://your-actual-domain.com
```

## ✅ Step 5: Update Price ID in Code

You need to update the price ID in `routes.py` line 450.

## ✅ Step 6: Test Locally

1. **Install Stripe CLI** (for local webhook testing):
   ```bash
   # macOS
   brew install stripe/stripe-cli/stripe
   
   # Or download from: https://github.com/stripe/stripe-cli/releases
   ```

2. **Login to Stripe CLI:**
   ```bash
   stripe login
   ```

3. **Forward webhooks to local server:**
   ```bash
   stripe listen --forward-to localhost:8080/stripe/webhook
   ```

4. **Start your app:**
   ```bash
   python main.py
   ```

5. **Test the flow:**
   - Create a new workspace
   - Go to home page and check trial countdown
   - Try to upgrade (use test card: 4242 4242 4242 4242)

## 🚀 Step 7: Deploy to Production

1. Update your domain in Stripe webhook settings
2. Use live keys instead of test keys
3. Test the production webhook endpoint

---

## Quick Commands to Remember:

**Test webhook locally:**
```bash
stripe listen --forward-to localhost:8080/stripe/webhook
```

**Test with curl:**
```bash
curl -X POST http://localhost:8080/api/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Check webhook logs:**
```bash
stripe logs tail
```
