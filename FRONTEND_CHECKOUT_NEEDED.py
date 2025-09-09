"""
Frontend Checkout Integration Needed
===================================

Create these endpoints and frontend components:
"""

# 1. Workspace Code Validation API
@app.route('/api/validate-workspace', methods=['POST'])
def validate_workspace():
    """Validate workspace code before checkout"""
    data = request.get_json()
    workspace_code = data.get('workspace_code')
    
    if not workspace_code:
        return jsonify({'error': 'Workspace code required'}), 400
    
    workspace = Workspace.query.filter_by(workspace_code=workspace_code).first()
    
    if workspace:
        return jsonify({
            'valid': True,
            'workspace_name': workspace.name,
            'current_tier': workspace.subscription_tier
        })
    else:
        return jsonify({'valid': False, 'error': 'Invalid workspace code'}), 404

# 2. Create Checkout Session API  
@app.route('/api/create-checkout', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session with workspace code"""
    try:
        data = request.get_json()
        workspace_code = data.get('workspace_code')
        price_id = data.get('price_id')  # Stripe price ID for selected tier
        
        # Validate workspace exists
        workspace = Workspace.query.filter_by(workspace_code=workspace_code).first()
        if not workspace:
            return jsonify({'error': 'Invalid workspace code'}), 400
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            success_url=f"{request.host_url}success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url}cancel",
            custom_fields=[
                {
                    'key': 'workspacecode',
                    'label': {'type': 'custom', 'custom': 'Workspace Code'},
                    'type': 'text',
                    'optional': False,
                    'text': {'default_value': workspace_code}  # Pre-fill the code
                }
            ],
            allow_promotion_codes=True,
            metadata={
                'workspace_code': workspace_code,
                'workspace_id': workspace.id
            }
        )
        
        return jsonify({'checkout_url': checkout_session.url})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 3. Success/Cancel Pages
@app.route('/success')
def checkout_success():
    """Checkout success page"""
    session_id = request.args.get('session_id')
    return render_template('checkout_success.html', session_id=session_id)

@app.route('/cancel')  
def checkout_cancel():
    """Checkout cancelled page"""
    return render_template('checkout_cancel.html')
