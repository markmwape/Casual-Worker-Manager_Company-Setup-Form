"""
Centralized Subscription Tier Configuration
===========================================

This file contains all tier specifications, limits, and features.
Easy to update pricing, worker limits, and add new restrictions or benefits.

Update this file to modify tier specifications without touching other code.
"""

from datetime import datetime, timedelta

# Tier Specifications - Simplified: Primary differentiator is worker limit!
TIER_SPECS = {
    'trial': {
        'name': '🎉 Free Trial',
        'description': '30-day free trial with full access',
        'price_monthly_usd': 0,
        'price_yearly_usd': 0,
        'worker_limit': None,  # Unlimited during trial
        'support_level': 'Email Support',
        'features': {
            'worker_management': True,
            'task_management': True, 
            'attendance_tracking': True,
            'reporting': True,
        },
        'limits': {
            'max_workers': None,  # Unlimited during trial
        }
    },
    
    'starter': {
        'name': '👥 Starter',
        'description': 'Up to 50 workers',
        'price_monthly_usd': 40,
        'price_yearly_usd': 400,
        'worker_limit': 50,
        'support_level': 'Email Support',
        'features': {
            'worker_management': True,
            'task_management': True, 
            'attendance_tracking': True,
            'reporting': True,
        },
        'limits': {
            'max_workers': 50,
        }
    },
    
    'growth': {
        'name': '📈 Growth',
        'description': 'Up to 250 workers', 
        'price_monthly_usd': 120,
        'price_yearly_usd': 1200,
        'worker_limit': 250,
        'support_level': 'Priority Email Support',
        'features': {
            'worker_management': True,
            'task_management': True,
            'attendance_tracking': True,
            'reporting': True,
        },
        'limits': {
            'max_workers': 250,
        }
    },
    
    'enterprise': {
        'name': '🏢 Enterprise', 
        'description': 'Up to 1,000 workers',
        'price_monthly_usd': 220,
        'price_yearly_usd': 2200,
        'worker_limit': 1000,
        'support_level': 'Phone & Email Support',
        'features': {
            'worker_management': True,
            'task_management': True,
            'attendance_tracking': True,
            'reporting': True,
        },
        'limits': {
            'max_workers': 1000,
        }
    },
    
    'corporate': {
        'name': '🏛️ Corporate',
        'description': 'Unlimited workers',
        'price_monthly_usd': 350,
        'price_yearly_usd': 3500,
        'worker_limit': None,  # Unlimited
        'support_level': 'Dedicated Account Manager',
        'features': {
            'worker_management': True,
            'task_management': True,
            'attendance_tracking': True,
            'reporting': True,
        },
        'limits': {
            'max_workers': None,  # Unlimited
        }
    }
}

# Stripe Product/Price ID Mapping
# Update these with your actual Stripe Price IDs
STRIPE_PRICE_MAPPING = {
    # Starter tier
    'starter_monthly': {
        'price_id': 'price_1S5BtBF93s78OlJMGU87jzBj',  # From your webhook
        'product_id': 'prod_T1ELaKIPUK85by',
        'tier': 'starter',
        'billing': 'monthly',
        'amount_cents': 4000  # $40.00
    },
    'starter_yearly': {
        'price_id': 'price_starter_yearly_REPLACE_WITH_ACTUAL', 
        'product_id': 'prod_T1ELaKIPUK85by',
        'tier': 'starter',
        'billing': 'yearly',
        'amount_cents': 40000  # $400.00
    },
    
    # Growth tier  
    'growth_monthly': {
        'price_id': 'price_1S5BvVF93s78OlJMSSvb5FZi',
        'product_id': 'prod_T1EOEHvwiG2NHk',
        'tier': 'growth',
        'billing': 'monthly',
        'amount_cents': 12000  # $120.00
    },
    'growth_yearly': {
        'price_id': 'price_growth_yearly_REPLACE_WITH_ACTUAL',
        'product_id': 'prod_T1EOEHvwiG2NHk', 
        'tier': 'growth',
        'billing': 'yearly',
        'amount_cents': 120000  # $1200.00
    },
    
    # Enterprise tier
    'enterprise_monthly': {
        'price_id': 'price_1S5BwPF93s78OlJMrfeJz9fG',
        'product_id': 'prod_T1EPae2dNy79mG',
        'tier': 'enterprise',
        'billing': 'monthly',
        'amount_cents': 22000  # $220.00
    },
    'enterprise_yearly': {
        'price_id': 'price_enterprise_yearly_REPLACE_WITH_ACTUAL',
        'product_id': 'prod_T1EQLnddFuPiqg',
        'tier': 'enterprise', 
        'billing': 'yearly',
        'amount_cents': 220000  # $2200.00
    },
    
    # Corporate tier
    'corporate_monthly': {
        'price_id': 'price_1S5BxIF93s78OlJM8Im1tpEJ',
        'product_id': 'prod_T1EQLnddFuPiqg',
        'tier': 'corporate',
        'billing': 'monthly',
        'amount_cents': 35000  # $350.00
    },
    'corporate_yearly': {
        'price_id': 'price_corporate_yearly_REPLACE_WITH_ACTUAL',
        'product_id': 'prod_T1EQLnddFuPiqg',
        'tier': 'corporate',
        'billing': 'yearly', 
        'amount_cents': 350000  # $3500.00
    }
}

# Helper Functions
def get_tier_spec(tier_name):
    """Get complete tier specification"""
    return TIER_SPECS.get(tier_name.lower(), TIER_SPECS['trial'])

def get_worker_limit(tier_name):
    """Get worker limit for tier (None = unlimited)"""
    tier = get_tier_spec(tier_name)
    return tier.get('worker_limit')

def is_within_worker_limit(tier_name, current_workers):
    """Check if current worker count is within tier limit"""
    limit = get_worker_limit(tier_name)
    if limit is None:  # Unlimited
        return True
    return current_workers <= limit

def has_feature(tier_name, feature_name):
    """Check if tier has a specific feature - simplified for basic features"""
    tier = get_tier_spec(tier_name)
    return tier['features'].get(feature_name, True)  # All tiers have basic features

def get_price_by_product_and_amount(product_id, amount_cents):
    """Get tier based on Stripe product ID and amount"""
    for price_key, price_info in STRIPE_PRICE_MAPPING.items():
        if (price_info['product_id'] == product_id and 
            price_info['amount_cents'] == amount_cents):
            return price_info['tier']
    
    # Fallback - determine by product ID only
    product_to_tier = {
        'prod_T1ELaKIPUK85by': 'starter',
        'prod_T1EOEHvwiG2NHk': 'growth',
        'prod_T1EQLnddFuPiqg': 'enterprise',  # Default for shared product ID
    }
    return product_to_tier.get(product_id, 'trial')

def get_all_tiers():
    """Get list of all available tiers"""
    return list(TIER_SPECS.keys())

def format_price(tier_name, billing='monthly'):
    """Format price for display"""
    tier = get_tier_spec(tier_name)
    if billing == 'yearly':
        price = tier['price_yearly_usd']
        return f"${price}/year"
    else:
        price = tier['price_monthly_usd'] 
        return f"${price}/month"

# Validation Functions
def get_tier_from_price_id(price_id):
    """Get tier name from Stripe price ID"""
    for price_key, price_info in STRIPE_PRICE_MAPPING.items():
        if price_info['price_id'] == price_id:
            return price_info['tier']
    return 'trial'  # Default fallback for trial users

def get_price_id_for_tier(tier_name, billing='monthly'):
    """Get Stripe price ID for a tier and billing period"""
    search_key = f"{tier_name}_{billing}"
    price_info = STRIPE_PRICE_MAPPING.get(search_key)
    return price_info['price_id'] if price_info else None

def validate_tier_access(workspace, worker_count=None):
    """
    Simplified tier validation - primarily focused on worker limits
    Returns: (is_allowed, reason)
    """
    tier = workspace.subscription_tier or 'trial'
    
    # Primary validation: Check worker limit
    if worker_count is not None:
        if not is_within_worker_limit(tier, worker_count):
            limit = get_worker_limit(tier)
            if limit is None:
                return True, "Access granted"  # Unlimited tier
            return False, f"Worker limit exceeded. {tier.title()} tier allows up to {limit} workers."
    
    return True, "Access granted"

def get_next_tier_for_workers(current_worker_count):
    """Get the minimum tier needed for the given worker count"""
    if current_worker_count <= 50:
        return 'starter'
    elif current_worker_count <= 250:
        return 'growth'
    elif current_worker_count <= 1000:
        return 'enterprise'
    else:
        return 'corporate'
