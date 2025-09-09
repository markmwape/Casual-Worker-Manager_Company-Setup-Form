#!/bin/bash

# Stripe Webhook Testing Script
# This script helps you test your Stripe integration locally

echo "🚀 Stripe Integration Testing Guide"
echo "=================================="
echo ""

echo "Step 1: Login to Stripe CLI"
echo "Run: stripe login"
echo "Follow the browser instructions to authenticate"
echo ""

echo "Step 2: Start your Flask app (in another terminal)"
echo "Run: python3 main.py"
echo "Make sure it's running on http://localhost:5000"
echo ""

echo "Step 3: Forward webhooks to local server"
echo "Run: stripe listen --forward-to localhost:5000/stripe/webhook"
echo "This will show you the webhook signing secret (whsec_...)"
echo ""

echo "Step 4: Update your .env file"
echo "Copy the webhook secret from step 3 and update:"
echo "STRIPE_WEBHOOK_SECRET=whsec_your_actual_secret_here"
echo ""

echo "Step 5: Test a payment"
echo "Run: stripe trigger payment_intent.succeeded"
echo "This will send a test webhook to your local server"
echo ""

echo "📝 Pricing Configuration"
echo "========================"
echo "Update the price IDs in routes.py (line ~450) with your actual Stripe Price IDs:"
echo "1. Go to https://dashboard.stripe.com/products"
echo "2. Create your products/pricing"
echo "3. Copy the price IDs (price_xxxxx)"
echo "4. Update the price_tier_mapping in routes.py"
echo ""

echo "🎯 Events to configure in Stripe Dashboard:"
echo "- checkout.session.completed (RECOMMENDED - most reliable)"
echo "- customer.subscription.created"
echo "- customer.subscription.updated" 
echo "- customer.subscription.deleted"
echo "- payment_intent.succeeded"
echo "- invoice.payment_succeeded" 
echo "- invoice.payment_failed"
echo ""
echo "💡 Priority: checkout.session.completed is the most reliable event"
echo "   It contains subscription ID which gives you direct access to product info"
