# Stripe Product ID to Subscription Tier Mapping

## Your Product IDs:
- `prod_T1ELaKIPUK85by` → **Starter** tier
- `prod_T1EOEHvwiG2NHk` → **Growth** tier  
- `prod_T1EQLnddFuPiqg` → **Corporate** OR **Enterprise** tier*

*Note: Corporate and Enterprise share the same product ID. The system distinguishes them by:
- Price ID (if you create separate prices for each)
- Payment amount (Enterprise typically higher cost)
- You can customize this logic in `get_subscription_tier_from_product()`

## How It Works:

### When Stripe sends a webhook:
1. **Checkout Session Completed** (BEST) → Gets subscription ID → Retrieves product ID from subscription
2. **Subscription Created** → Gets product ID directly from subscription data  
3. **Payment Intent Succeeded** → Extracts product ID from invoice/subscription
4. **System maps product ID** → Determines correct tier automatically
5. **User gets upgraded** → Workspace subscription_tier field updated

### Supported Tiers in Database:
- `starter`
- `growth` 
- `corporate`
- `enterprise`

## Testing:

### Test specific tiers:
```bash
# Test checkout session completed (RECOMMENDED)
curl -X POST http://localhost:5000/test/checkout-session-webhook \
  -H "Content-Type: application/json" \
  -d '{"tier": "starter"}'

curl -X POST http://localhost:5000/test/checkout-session-webhook \
  -H "Content-Type: application/json" \
  -d '{"tier": "growth"}'

curl -X POST http://localhost:5000/test/checkout-session-webhook \
  -H "Content-Type: application/json" \
  -d '{"tier": "corporate"}'

curl -X POST http://localhost:5000/test/checkout-session-webhook \
  -H "Content-Type: application/json" \
  -d '{"tier": "enterprise"}'

# Alternative: Test subscription webhook
curl -X POST http://localhost:5000/test/subscription-webhook \
  -H "Content-Type: application/json" \
  -d '{"tier": "starter"}'
```

### Check workspace tier after payment:
```sql
SELECT id, name, subscription_status, subscription_tier, subscription_end_date 
FROM workspace 
WHERE stripe_customer_id = 'cus_your_customer_id';
```

## Customization:

To distinguish Corporate vs Enterprise with same product ID:
1. **Option 1**: Create separate Price IDs in Stripe Dashboard
2. **Option 2**: Set different amounts and use amount-based logic  
3. **Option 3**: Add metadata to Stripe products/prices

Update the `get_subscription_tier_from_product()` function in routes.py to customize the logic.
