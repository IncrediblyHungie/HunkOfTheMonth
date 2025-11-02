# Stripe + Printify Integration Plan
## Complete Order Fulfillment Flow

### Overview
This document outlines the complete integration between Stripe (payment processing) and Printify (calendar fulfillment) for the Hunk of the Month calendar platform.

---

## Flow Architecture

```
User Completes Calendar
        ↓
Clicks "Order Calendar"
        ↓
Stripe Checkout Session Created
        ↓
User Enters Payment + Shipping Info
        ↓
Payment Successful
        ↓
Stripe Webhook Fires (checkout.session.completed)
        ↓
Extract Shipping Address & Customer Info
        ↓
Upload 12 Month Images to Printify
        ↓
Create Calendar Product in Printify
        ↓
Submit Order to Printify
        ↓
Redirect User to Success Page
        ↓
Printify Fulfills & Ships Calendar
```

---

## Phase 1: Fix Stripe Initialization Issue

### Problem
- Error: `'NoneType' object has no attribute 'Session'`
- Root Cause: Stripe module not properly initialized when creating checkout session

### Solution
- Ensure `stripe.api_key` is set in `app/__init__.py` (already done)
- Import stripe at service level in `stripe_service.py`
- Add proper error handling if API key missing

### Files to Modify
- `app/services/stripe_service.py` - Add import and validation

---

## Phase 2: Stripe Checkout Session Enhancement

### Current Implementation
- Already collects: payment info, shipping address, phone, email
- Supports 10 countries: US, CA, GB, AU, DE, FR, ES, IT, NL, BE

### Enhancements Needed
1. **Add Metadata to Checkout Session**
   - `session_id` (our internal session ID)
   - `project_id`
   - `product_type` (calendar_2026, desktop, standard_wall)

2. **Store Checkout Session ID**
   - Save Stripe session ID to session storage
   - Link to our internal project

### Implementation
```python
stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[...],
    mode='payment',
    success_url=success_url,
    cancel_url=cancel_url,
    shipping_address_collection={
        'allowed_countries': ['US', 'CA', 'GB', 'AU', 'DE', 'FR', 'ES', 'IT', 'NL', 'BE']
    },
    phone_number_collection={'enabled': True},
    metadata={
        'internal_session_id': session_id,
        'project_id': project_id,
        'product_type': product_type
    }
)
```

---

## Phase 3: Stripe Webhook Handler

### Endpoint
`POST /webhooks/stripe`

### Webhook Events to Handle
1. **`checkout.session.completed`** - Payment successful, trigger fulfillment
2. **`checkout.session.async_payment_succeeded`** - Async payment succeeded
3. **`checkout.session.async_payment_failed`** - Async payment failed

### Webhook Verification
```python
import stripe

def verify_webhook(payload, sig_header, webhook_secret):
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        return event
    except ValueError:
        # Invalid payload
        return None
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return None
```

### Extract Shipping Address
```python
session = event['data']['object']  # Checkout Session object

# Shipping address
shipping = session.get('shipping_details')
address = shipping['address']
{
    'line1': address['line1'],
    'line2': address.get('line2', ''),
    'city': address['city'],
    'state': address.get('state', ''),
    'zip': address['postal_code'],
    'country': address['country']
}

# Customer info
customer_name = shipping['name']
customer_email = session.get('customer_details', {}).get('email')
customer_phone = session.get('customer_details', {}).get('phone')

# Our metadata
metadata = session.get('metadata', {})
internal_session_id = metadata.get('internal_session_id')
product_type = metadata.get('product_type')
```

---

## Phase 4: Printify Service Module

### File Structure
`app/services/printify_service.py`

### Core Functions

#### 1. Get Shop ID
```python
def get_shop_id():
    """Get the first shop ID from Printify account"""
    response = requests.get(
        'https://api.printify.com/v1/shops.json',
        headers={'Authorization': f'Bearer {PRINTIFY_API_TOKEN}'}
    )
    shops = response.json()
    return shops[0]['id'] if shops else None
```

#### 2. Upload Images
```python
def upload_images_to_printify(month_images):
    """Upload 12 month images to Printify

    Args:
        month_images: List of 12 tuples (month_number, image_binary_data)

    Returns:
        Dict mapping month_number to printify_image_id
    """
    image_ids = {}

    for month_num, image_data in month_images:
        # Convert binary to base64
        import base64
        b64_data = base64.b64encode(image_data).decode('utf-8')

        response = requests.post(
            'https://api.printify.com/v1/uploads/images.json',
            headers={
                'Authorization': f'Bearer {PRINTIFY_API_TOKEN}',
                'Content-Type': 'application/json'
            },
            json={
                'file_name': f'month_{month_num}.jpg',
                'contents': b64_data
            }
        )

        result = response.json()
        image_ids[month_num] = result['id']

    return image_ids
```

#### 3. Find Calendar Blueprint
```python
def find_calendar_blueprint():
    """Find 2026 calendar blueprint in Printify catalog

    Returns:
        (blueprint_id, print_provider_id, variant_id)
    """
    response = requests.get(
        'https://api.printify.com/v1/catalog/blueprints.json',
        headers={'Authorization': f'Bearer {PRINTIFY_API_TOKEN}'}
    )

    blueprints = response.json()

    # Search for calendar blueprint
    for blueprint in blueprints:
        if 'calendar' in blueprint['title'].lower() and '2026' in blueprint['title']:
            blueprint_id = blueprint['id']

            # Get blueprint details for variants
            details_response = requests.get(
                f'https://api.printify.com/v1/catalog/blueprints/{blueprint_id}/print_providers.json',
                headers={'Authorization': f'Bearer {PRINTIFY_API_TOKEN}'}
            )

            providers = details_response.json()
            provider = providers[0]  # Use first provider
            variant = provider['variants'][0]  # Use first variant

            return (blueprint_id, provider['id'], variant['id'])

    raise ValueError("Calendar 2026 blueprint not found in Printify catalog")
```

#### 4. Create Calendar Product
```python
def create_calendar_product(shop_id, blueprint_id, provider_id, variant_id, image_ids):
    """Create calendar product with 12 month images

    Args:
        shop_id: Printify shop ID
        blueprint_id: Calendar blueprint ID
        provider_id: Print provider ID
        variant_id: Calendar variant ID
        image_ids: Dict mapping month_number to printify_image_id

    Returns:
        product_id
    """
    # Build print areas with images for each month
    print_areas = []

    for month_num in range(1, 13):
        print_areas.append({
            'variant_ids': [variant_id],
            'placeholders': [{
                'position': 'front',
                'images': [{
                    'id': image_ids[month_num],
                    'x': 0.5,
                    'y': 0.5,
                    'scale': 1.0,
                    'angle': 0
                }]
            }]
        })

    response = requests.post(
        f'https://api.printify.com/v1/shops/{shop_id}/products.json',
        headers={
            'Authorization': f'Bearer {PRINTIFY_API_TOKEN}',
            'Content-Type': 'application/json'
        },
        json={
            'title': 'Hunk of the Month Calendar 2026',
            'description': 'Custom AI-generated calendar featuring personalized hunky transformations',
            'blueprint_id': blueprint_id,
            'print_provider_id': provider_id,
            'variants': [{
                'id': variant_id,
                'price': 3999  # $39.99 in cents
            }],
            'print_areas': print_areas
        }
    )

    product = response.json()
    return product['id']
```

#### 5. Submit Order
```python
def submit_printify_order(shop_id, product_id, variant_id, shipping_address, customer_info):
    """Submit order to Printify for fulfillment

    Args:
        shop_id: Printify shop ID
        product_id: Created product ID
        variant_id: Calendar variant ID
        shipping_address: Dict with address fields
        customer_info: Dict with name, email, phone

    Returns:
        order_id
    """
    response = requests.post(
        f'https://api.printify.com/v1/shops/{shop_id}/orders.json',
        headers={
            'Authorization': f'Bearer {PRINTIFY_API_TOKEN}',
            'Content-Type': 'application/json'
        },
        json={
            'external_id': f'stripe_{customer_info["email"]}_{int(time.time())}',
            'label': 'Hunk of the Month Order',
            'line_items': [{
                'product_id': product_id,
                'variant_id': variant_id,
                'quantity': 1
            }],
            'shipping_method': 1,  # Standard shipping
            'send_shipping_notification': True,
            'address_to': {
                'first_name': customer_info['name'].split()[0],
                'last_name': ' '.join(customer_info['name'].split()[1:]) if len(customer_info['name'].split()) > 1 else '',
                'email': customer_info['email'],
                'phone': customer_info.get('phone', ''),
                'country': shipping_address['country'],
                'region': shipping_address.get('state', ''),
                'address1': shipping_address['line1'],
                'address2': shipping_address.get('line2', ''),
                'city': shipping_address['city'],
                'zip': shipping_address['zip']
            }
        }
    )

    order = response.json()
    return order['id']
```

---

## Phase 5: Webhook Processing Flow

### File: `app/routes/webhooks.py`

```python
from flask import Blueprint, request, jsonify
from app.services import printify_service
from app import session_storage
import stripe
import os

bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')

@bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle checkout.session.completed
    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']

        # Extract data
        shipping = session_obj.get('shipping_details', {})
        customer_details = session_obj.get('customer_details', {})
        metadata = session_obj.get('metadata', {})

        internal_session_id = metadata.get('internal_session_id')
        product_type = metadata.get('product_type')

        # Get month images from session storage
        # (need to implement session lookup by internal_session_id)
        months = session_storage.get_all_months_by_session_id(internal_session_id)
        month_images = [(m['month_number'], m['master_image_data']) for m in months]

        try:
            # Upload images to Printify
            image_ids = printify_service.upload_images_to_printify(month_images)

            # Get shop and blueprint info
            shop_id = printify_service.get_shop_id()
            blueprint_id, provider_id, variant_id = printify_service.find_calendar_blueprint()

            # Create product
            product_id = printify_service.create_calendar_product(
                shop_id, blueprint_id, provider_id, variant_id, image_ids
            )

            # Submit order
            shipping_address = {
                'line1': shipping['address']['line1'],
                'line2': shipping['address'].get('line2', ''),
                'city': shipping['address']['city'],
                'state': shipping['address'].get('state', ''),
                'zip': shipping['address']['postal_code'],
                'country': shipping['address']['country']
            }

            customer_info = {
                'name': shipping['name'],
                'email': customer_details.get('email'),
                'phone': customer_details.get('phone')
            }

            order_id = printify_service.submit_printify_order(
                shop_id, product_id, variant_id,
                shipping_address, customer_info
            )

            # Save order info to session storage
            session_storage.save_order_info(internal_session_id, {
                'stripe_session_id': session_obj['id'],
                'printify_order_id': order_id,
                'printify_product_id': product_id,
                'customer_email': customer_info['email'],
                'order_status': 'submitted',
                'created_at': datetime.utcnow().isoformat()
            })

            print(f"✅ Order {order_id} submitted to Printify")

        except Exception as e:
            print(f"❌ Order fulfillment error: {e}")
            # TODO: Send error notification to admin
            return jsonify({'error': str(e)}), 500

    return jsonify({'status': 'success'}), 200
```

---

## Phase 6: Session Storage Updates

### Add Order Tracking

```python
# app/session_storage.py

def save_order_info(session_id, order_data):
    """Save order information to session"""
    storage = _get_storage_by_id(session_id)
    storage['order'] = order_data
    _save_session(session_id)

def get_order_info(session_id):
    """Get order information"""
    storage = _get_storage_by_id(session_id)
    return storage.get('order')

def _get_storage_by_id(session_id):
    """Get storage by internal session ID"""
    _load_storage()
    return _storage.get(session_id, {})
```

---

## Phase 7: Environment Variables

### Add to `.env`

```bash
# Stripe Webhook Secret (from Stripe Dashboard)
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Printify Shop ID (optional, auto-detected)
PRINTIFY_SHOP_ID=12345
```

---

## Phase 8: Testing Strategy

### 1. Stripe Test Mode
- Use Stripe test API keys
- Test card: `4242 4242 4242 4242`
- Use Stripe CLI to forward webhooks locally:
  ```bash
  stripe listen --forward-to localhost:5000/webhooks/stripe
  ```

### 2. Printify Sandbox/Test Orders
- Check if Printify has test mode
- If not, use real API with test product

### 3. End-to-End Test Flow
1. Upload test photos
2. Generate calendar
3. Click "Order Calendar"
4. Complete Stripe checkout with test card
5. Verify webhook fires
6. Check Printify order created
7. Verify success page shows order ID

---

## Phase 9: Production Deployment Checklist

- [ ] Add `STRIPE_WEBHOOK_SECRET` to production environment
- [ ] Configure Stripe webhook endpoint in Stripe Dashboard
- [ ] Set webhook URL: `https://yourdomain.com/webhooks/stripe`
- [ ] Select event: `checkout.session.completed`
- [ ] Test webhook with Stripe CLI
- [ ] Monitor webhook logs for errors
- [ ] Set up error notifications (email/Slack)
- [ ] Add order tracking page for users
- [ ] Document customer support flow

---

## Error Handling & Edge Cases

### 1. Stripe Payment Fails
- User sees error on Stripe page
- No webhook fires
- No Printify order created
- No action needed

### 2. Webhook Receives but Printify Fails
- Log error with full details
- Send admin notification
- Store failed order in DB for manual retry
- Email customer about delay

### 3. Image Upload to Printify Fails
- Retry up to 3 times with exponential backoff
- If all fail, log error and notify admin

### 4. Duplicate Webhook Events
- Stripe can send duplicate events
- Use idempotency: check if order already created
- Store `stripe_session_id` and check before creating order

---

## Success Criteria

✅ User completes checkout and sees success page
✅ Stripe webhook fires and processes successfully
✅ All 12 images uploaded to Printify
✅ Calendar product created in Printify
✅ Order submitted to Printify with correct address
✅ User receives order confirmation email from Printify
✅ Order visible in Printify dashboard
✅ Calendar ships to customer

---

## Monitoring & Observability

### Logs to Track
- Stripe checkout session created
- Stripe webhook received
- Printify image uploads (12 total)
- Printify product created
- Printify order submitted
- Order ID saved to session storage

### Metrics to Monitor
- Checkout completion rate
- Webhook processing time
- Printify API success rate
- Order fulfillment time
- Customer support tickets

---

## Next Steps

1. ✅ Research Stripe + Printify integration
2. ⏳ Fix Stripe initialization error
3. ⏳ Create Printify service module
4. ⏳ Implement webhook handler
5. ⏳ Add order tracking to session storage
6. ⏳ Test with Stripe test mode
7. ⏳ Deploy and test end-to-end
8. ⏳ Go live with real orders!
