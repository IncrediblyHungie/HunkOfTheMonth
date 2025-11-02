# Printify + Stripe Integration Architecture

## Overview

Seamless e-commerce integration for **Hunk of the Month** calendar app, allowing users to order physical calendars with their AI-generated images printed via Printify and paid through Stripe.

## Product Offerings

### Three Calendar Products

| Product | Blueprint ID | Print Provider | Variant ID | Price (Suggested) |
|---------|--------------|----------------|------------|-------------------|
| **Calendar (2026)** | 1253 | 234 (Today's Graphics) | 94860 | $24.99 |
| **Desktop Calendar** | 1170 | TBD | TBD | $19.99 |
| **Standard Wall Calendar (2026)** | 965 | TBD | TBD | $29.99 |

### Calendar Structure (Blueprint 1253)

Each calendar has **13 placeholders**:
- `front_cover` (3454x2725px)
- `january` through `december` (3454x2725px each)

Our app generates 12 month images → we'll use them for months + front cover shows Month 1.

---

## User Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Current Flow (Working)                                           │
└─────────────────────────────────────────────────────────────────┘
1. User uploads 3-7 selfie photos
2. AI generates 12 hunk calendar months (Gemini + face-swap)
3. User previews all 12 months
4. ✅ END (currently)

┌─────────────────────────────────────────────────────────────────┐
│ New E-Commerce Flow (Adding)                                     │
└─────────────────────────────────────────────────────────────────┘
5. User clicks "Order Physical Calendar"
6. Product selection page → choose calendar type (wall/desktop)
7. Click "Checkout" → redirected to Stripe hosted checkout
8. User enters shipping address + pays with Stripe
9. Webhook receives payment confirmation
10. Backend uploads images to Printify
11. Backend creates Printify product with user's images
12. Backend submits order to Printify (auto-fulfillment)
13. User receives order confirmation email
14. Printify prints + ships calendar
15. User receives tracking number
```

---

## Technical Architecture

### API Credentials (Environment Variables)

```bash
# .env file
PRINTIFY_API_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
STRIPE_SECRET_KEY=sk_test_51SNiNlGo9YmfNA1ee...
STRIPE_PUBLISHABLE_KEY=pk_test_51SNiNlGo9YmfNA1ev...
STRIPE_WEBHOOK_SECRET=whsec_... (generated after webhook setup)
```

### Database Schema Changes

**New Tables:**

```sql
-- Orders table (track Printify orders)
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_session_id VARCHAR(255),  -- Links to session storage
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_checkout_session_id VARCHAR(255) UNIQUE,
    printify_order_id VARCHAR(255),
    product_type VARCHAR(50),  -- 'calendar_2026', 'desktop', 'standard_wall'
    status VARCHAR(50),  -- 'pending', 'paid', 'printify_created', 'shipped', 'delivered'
    total_amount_cents INTEGER,
    customer_email VARCHAR(255),
    shipping_address JSONB,
    printify_image_ids JSONB,  -- Array of Printify upload IDs
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Track Printify uploads (avoid re-uploading same images)
CREATE TABLE printify_uploads (
    id SERIAL PRIMARY KEY,
    month_image_id INTEGER,  -- References our month images
    printify_upload_id VARCHAR(255),
    printify_image_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Implementation Steps

### Step 1: Environment Setup

**File: `/app/__init__.py`** (add after existing config)

```python
# Printify configuration
app.config['PRINTIFY_API_TOKEN'] = os.getenv('PRINTIFY_API_TOKEN')
app.config['PRINTIFY_SHOP_ID'] = os.getenv('PRINTIFY_SHOP_ID', None)  # Auto-detect from API

# Stripe configuration
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')
app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv('STRIPE_WEBHOOK_SECRET')

# Initialize Stripe
import stripe
stripe.api_key = app.config['STRIPE_SECRET_KEY']
```

### Step 2: Printify Service Module

**File: `/app/services/printify_service.py`**

```python
"""
Printify API integration for calendar fulfillment
"""
import requests
import base64
from flask import current_app

PRINTIFY_API_BASE = "https://api.printify.com/v1"

def get_headers():
    """Get authorization headers for Printify API"""
    return {
        "Authorization": f"Bearer {current_app.config['PRINTIFY_API_TOKEN']}",
        "Content-Type": "application/json"
    }

def upload_image(image_data_bytes, filename="month.jpg"):
    """
    Upload image to Printify Media Library

    Args:
        image_data_bytes: Raw image bytes (JPEG/PNG)
        filename: Filename for the upload

    Returns:
        Printify upload ID
    """
    # Convert image bytes to base64
    image_b64 = base64.b64encode(image_data_bytes).decode('utf-8')

    payload = {
        "file_name": filename,
        "contents": image_b64
    }

    response = requests.post(
        f"{PRINTIFY_API_BASE}/uploads/images.json",
        headers=get_headers(),
        json=payload
    )

    response.raise_for_status()
    upload_data = response.json()

    return upload_data['id']

def create_calendar_product(blueprint_id, variant_id, print_provider_id, month_image_ids):
    """
    Create a calendar product with user's images

    Args:
        blueprint_id: Calendar blueprint (1253, 1170, or 965)
        variant_id: Variant ID for specific calendar type
        print_provider_id: Print provider ID
        month_image_ids: Dict mapping {"january": upload_id, "february": upload_id, ...}

    Returns:
        Product ID
    """
    # Construct print_areas
    print_areas = [
        {
            "variant_ids": [variant_id],
            "placeholders": []
        }
    ]

    # Add front cover (use January image)
    print_areas[0]["placeholders"].append({
        "position": "front_cover",
        "images": [
            {
                "id": month_image_ids.get("january"),
                "x": 0.5,  # Center horizontally
                "y": 0.5,  # Center vertically
                "scale": 1.0,  # Fill entire area
                "angle": 0
            }
        ]
    })

    # Add all 12 months
    months = ["january", "february", "march", "april", "may", "june",
              "july", "august", "september", "october", "november", "december"]

    for month in months:
        print_areas[0]["placeholders"].append({
            "position": month,
            "images": [
                {
                    "id": month_image_ids.get(month),
                    "x": 0.5,
                    "y": 0.5,
                    "scale": 1.0,
                    "angle": 0
                }
            ]
        })

    payload = {
        "title": "Custom Hunk Calendar 2026",
        "description": "Personalized calendar with AI-generated images",
        "blueprint_id": blueprint_id,
        "print_provider_id": print_provider_id,
        "variants": [
            {
                "id": variant_id,
                "price": 2499,  # Price in cents ($24.99)
                "is_enabled": True
            }
        ],
        "print_areas": print_areas
    }

    # Get shop ID (first shop in account)
    shop_id = get_shop_id()

    response = requests.post(
        f"{PRINTIFY_API_BASE}/shops/{shop_id}/products.json",
        headers=get_headers(),
        json=payload
    )

    response.raise_for_status()
    product_data = response.json()

    return product_data['id']

def create_order(product_id, variant_id, quantity, shipping_address, customer_email):
    """
    Create Printify order for fulfillment

    Args:
        product_id: Printify product ID (from create_calendar_product)
        variant_id: Variant ID
        quantity: Number of calendars
        shipping_address: Dict with address fields
        customer_email: Customer email

    Returns:
        Order ID
    """
    shop_id = get_shop_id()

    payload = {
        "external_id": f"hotm_{int(time.time())}",  # Unique order reference
        "label": customer_email,
        "line_items": [
            {
                "product_id": product_id,
                "variant_id": variant_id,
                "quantity": quantity
            }
        ],
        "shipping_method": 1,  # Standard shipping
        "send_shipping_notification": True,
        "address_to": {
            "first_name": shipping_address['first_name'],
            "last_name": shipping_address['last_name'],
            "email": customer_email,
            "phone": shipping_address.get('phone', ''),
            "country": shipping_address['country'],
            "region": shipping_address.get('state', ''),
            "address1": shipping_address['address1'],
            "address2": shipping_address.get('address2', ''),
            "city": shipping_address['city'],
            "zip": shipping_address['zip']
        }
    }

    response = requests.post(
        f"{PRINTIFY_API_BASE}/shops/{shop_id}/orders.json",
        headers=get_headers(),
        json=payload
    )

    response.raise_for_status()
    order_data = response.json()

    return order_data['id']

def get_shop_id():
    """Get first shop ID from Printify account"""
    if current_app.config.get('PRINTIFY_SHOP_ID'):
        return current_app.config['PRINTIFY_SHOP_ID']

    response = requests.get(
        f"{PRINTIFY_API_BASE}/shops.json",
        headers=get_headers()
    )
    response.raise_for_status()
    shops = response.json()

    if not shops:
        raise Exception("No Printify shops found. Please create a shop first.")

    shop_id = shops[0]['id']
    current_app.config['PRINTIFY_SHOP_ID'] = shop_id
    return shop_id
```

### Step 3: Stripe Service Module

**File: `/app/services/stripe_service.py`**

```python
"""
Stripe payment processing integration
"""
import stripe
from flask import current_app, url_for

CALENDAR_PRICES = {
    'calendar_2026': 2499,  # $24.99
    'desktop': 1999,         # $19.99
    'standard_wall': 2999    # $29.99
}

def create_checkout_session(product_type, success_url, cancel_url):
    """
    Create Stripe Checkout session for calendar purchase

    Args:
        product_type: 'calendar_2026', 'desktop', or 'standard_wall'
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if user cancels

    Returns:
        Checkout session ID and URL
    """
    price_cents = CALENDAR_PRICES.get(product_type, 2499)

    product_names = {
        'calendar_2026': 'Custom Hunk Calendar 2026',
        'desktop': 'Custom Desktop Calendar',
        'standard_wall': 'Custom Wall Calendar 2026'
    }

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product_names[product_type],
                    'description': 'Personalized calendar with your AI-generated images',
                    'images': ['https://hunkofthemonth.fly.dev/static/calendar_preview.jpg']
                },
                'unit_amount': price_cents,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=None,  # Stripe will collect
        shipping_address_collection={
            'allowed_countries': ['US', 'CA', 'GB', 'AU']
        },
        metadata={
            'product_type': product_type
        }
    )

    return {
        'session_id': session.id,
        'url': session.url
    }

def verify_webhook_signature(payload, signature):
    """
    Verify Stripe webhook signature for security

    Args:
        payload: Raw webhook payload (bytes)
        signature: Stripe-Signature header value

    Returns:
        Stripe Event object if valid

    Raises:
        ValueError if signature invalid
    """
    webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        return event
    except ValueError as e:
        # Invalid payload
        raise ValueError(f"Invalid payload: {e}")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise ValueError(f"Invalid signature: {e}")
```

### Step 4: Add Product Selection Page

**File: `/app/templates/order.html`** (new file)

```html
{% extends "base.html" %}

{% block title %}Order Your Calendar{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-10">
            <h1 class="text-center mb-4">🎁 Order Your Custom Calendar</h1>
            <p class="lead text-center mb-5">
                Your 12 hunk months are ready! Choose your calendar style and we'll print and ship it to you.
            </p>

            <div class="row g-4">
                <!-- Calendar 2026 -->
                <div class="col-md-4">
                    <div class="card h-100 shadow-sm">
                        <img src="https://images.printify.com/68d29f8ffd6cd3545304b932" class="card-img-top" alt="Calendar 2026">
                        <div class="card-body">
                            <h5 class="card-title">Calendar 2026</h5>
                            <p class="card-text">
                                <small class="text-muted">10.8" × 8.4"</small><br>
                                Premium 270gsm semi-glossy paper<br>
                                Wire binding, centered holes for hanging
                            </p>
                            <h4 class="text-primary">$24.99</h4>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-primary w-100 order-btn"
                                    data-product="calendar_2026">
                                Order Now
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Desktop Calendar -->
                <div class="col-md-4">
                    <div class="card h-100 shadow-sm">
                        <img src="https://images.printify.com/..." class="card-img-top" alt="Desktop Calendar">
                        <div class="card-body">
                            <h5 class="card-title">Desktop Calendar</h5>
                            <p class="card-text">
                                <small class="text-muted">10" × 5"</small><br>
                                250gsm premium paper<br>
                                Spiral bound at top
                            </p>
                            <h4 class="text-primary">$19.99</h4>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-primary w-100 order-btn"
                                    data-product="desktop">
                                Order Now
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Standard Wall Calendar -->
                <div class="col-md-4">
                    <div class="card h-100 shadow-sm">
                        <img src="https://images.printify.com/..." class="card-img-top" alt="Wall Calendar">
                        <div class="card-body">
                            <h5 class="card-title">Wall Calendar 2026</h5>
                            <p class="card-text">
                                <small class="text-muted">Multiple sizes</small><br>
                                250gsm high-quality paper<br>
                                Spiral binding, matte grid area
                            </p>
                            <h4 class="text-primary">$29.99</h4>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-primary w-100 order-btn"
                                    data-product="standard_wall">
                                Order Now
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="text-center mt-5">
                <p class="text-muted">
                    <i class="fas fa-shipping-fast"></i> Ships within 3-5 business days<br>
                    <i class="fas fa-lock"></i> Secure payment via Stripe<br>
                    <i class="fas fa-smile"></i> 100% satisfaction guarantee
                </p>
            </div>
        </div>
    </div>
</div>

<script>
document.querySelectorAll('.order-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
        const productType = this.dataset.product;

        // Show loading
        this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Loading...';
        this.disabled = true;

        try {
            // Create Stripe checkout session
            const response = await fetch('/api/checkout/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({product_type: productType})
            });

            const data = await response.json();

            if (data.success) {
                // Redirect to Stripe checkout
                window.location.href = data.checkout_url;
            } else {
                alert('Error: ' + data.error);
                this.innerHTML = 'Order Now';
                this.disabled = false;
            }
        } catch (error) {
            console.error('Checkout error:', error);
            alert('Failed to start checkout. Please try again.');
            this.innerHTML = 'Order Now';
            this.disabled = false;
        }
    });
});
</script>
{% endblock %}
```

### Step 5: Checkout API Endpoint

**File: `/app/routes/api.py`** (add these routes)

```python
from app.services import stripe_service, printify_service

@bp.route('/checkout/create', methods=['POST'])
def create_checkout():
    """Create Stripe checkout session"""
    project = get_current_project()
    if not project:
        return jsonify({'error': 'No active project'}), 401

    data = request.json
    product_type = data.get('product_type')

    if product_type not in ['calendar_2026', 'desktop', 'standard_wall']:
        return jsonify({'error': 'Invalid product type'}), 400

    try:
        # Create Stripe checkout session
        session_data = stripe_service.create_checkout_session(
            product_type=product_type,
            success_url=url_for('main.order_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('projects.preview', _external=True)
        )

        # Store checkout session ID in session storage for later
        session_storage.save_checkout_session(session_data['session_id'], product_type)

        return jsonify({
            'success': True,
            'checkout_url': session_data['url']
        })

    except Exception as e:
        print(f"Checkout error: {e}")
        return jsonify({'error': str(e)}), 500
```

### Step 6: Stripe Webhook Handler

**File: `/app/routes/webhooks.py`** (new file)

```python
"""
Webhook handlers for Stripe payment events
"""
from flask import Blueprint, request, jsonify
import stripe
from app.services import stripe_service, printify_service
from app import session_storage

bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')

@bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verify webhook signature
        event = stripe_service.verify_webhook_signature(payload, sig_header)
    except ValueError as e:
        print(f"Webhook verification failed: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']

        # Retrieve full checkout session with line items
        checkout_session = stripe.checkout.Session.retrieve(
            session_obj['id'],
            expand=['line_items', 'shipping_details']
        )

        # Extract data
        payment_intent_id = checkout_session.payment_intent
        customer_email = checkout_session.customer_details.email
        shipping = checkout_session.shipping_details.address
        product_type = checkout_session.metadata.get('product_type')

        print(f"✅ Payment successful: {customer_email}, Product: {product_type}")

        # Trigger Printify order creation (async task recommended)
        try:
            create_printify_order(
                session_id=checkout_session.id,
                payment_intent_id=payment_intent_id,
                product_type=product_type,
                customer_email=customer_email,
                shipping_address={
                    'first_name': checkout_session.customer_details.name.split()[0],
                    'last_name': ' '.join(checkout_session.customer_details.name.split()[1:]),
                    'address1': shipping.line1,
                    'address2': shipping.line2 or '',
                    'city': shipping.city,
                    'state': shipping.state,
                    'zip': shipping.postal_code,
                    'country': shipping.country,
                    'phone': checkout_session.customer_details.phone or ''
                }
            )
        except Exception as e:
            print(f"❌ Printify order creation failed: {e}")
            # TODO: Store in failed_orders table for manual retry

    return jsonify({'success': True})

def create_printify_order(session_id, payment_intent_id, product_type, customer_email, shipping_address):
    """
    Create Printify order after successful payment

    This should ideally be an async background task (Celery/RQ)
    """
    # Get user's generated month images from session storage
    months = session_storage.get_all_months()

    # Upload all 12 month images to Printify
    print("📤 Uploading images to Printify...")
    month_names = ["january", "february", "march", "april", "may", "june",
                   "july", "august", "september", "october", "november", "december"]

    printify_image_ids = {}
    for i, month_name in enumerate(month_names):
        month_num = i + 1
        month_data = next((m for m in months if m['month_number'] == month_num), None)

        if not month_data or not month_data.get('image_data'):
            raise Exception(f"Missing image data for month {month_num}")

        # Upload to Printify
        upload_id = printify_service.upload_image(
            month_data['image_data'],
            filename=f"{month_name}.jpg"
        )

        printify_image_ids[month_name] = upload_id
        print(f"  ✓ {month_name}: {upload_id}")

    # Determine blueprint/variant based on product type
    product_config = {
        'calendar_2026': {'blueprint_id': 1253, 'variant_id': 94860, 'provider_id': 234},
        'desktop': {'blueprint_id': 1170, 'variant_id': None, 'provider_id': None},  # TODO
        'standard_wall': {'blueprint_id': 965, 'variant_id': None, 'provider_id': None}  # TODO
    }

    config = product_config[product_type]

    # Create Printify product with uploaded images
    print("🎨 Creating Printify product...")
    product_id = printify_service.create_calendar_product(
        blueprint_id=config['blueprint_id'],
        variant_id=config['variant_id'],
        print_provider_id=config['provider_id'],
        month_image_ids=printify_image_ids
    )
    print(f"  ✓ Product created: {product_id}")

    # Submit order to Printify for fulfillment
    print("📦 Submitting order to Printify...")
    order_id = printify_service.create_order(
        product_id=product_id,
        variant_id=config['variant_id'],
        quantity=1,
        shipping_address=shipping_address,
        customer_email=customer_email
    )
    print(f"  ✓ Order submitted: {order_id}")

    # TODO: Save order to database
    # db.session.add(Order(...))
    # db.session.commit()

    return order_id
```

Register webhook blueprint in `/app/__init__.py`:

```python
from app.routes import main, projects, api, webhooks
app.register_blueprint(main.bp)
app.register_blueprint(projects.bp)
app.register_blueprint(api.bp)
app.register_blueprint(webhooks.bp)  # NEW
```

---

## Deployment Steps

### 1. Set Environment Variables on Fly.io

```bash
flyctl secrets set \
  PRINTIFY_API_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..." \
  STRIPE_SECRET_KEY="sk_test_51SNiNlGo9YmfNA1ee..." \
  STRIPE_PUBLISHABLE_KEY="pk_test_51SNiNlGo9YmfNA1ev..." \
  -a hunkofthemonth
```

### 2. Configure Stripe Webhook

1. Go to https://dashboard.stripe.com/test/webhooks
2. Click "+ Add endpoint"
3. URL: `https://hunkofthemonth.fly.dev/webhooks/stripe`
4. Select event: `checkout.session.completed`
5. Copy webhook signing secret
6. Add to Fly.io: `flyctl secrets set STRIPE_WEBHOOK_SECRET="whsec_..." -a hunkofthemonth`

### 3. Test Payment Flow

1. Use Stripe test card: `4242 4242 4242 4242`, any future date, any CVV
2. Complete checkout flow
3. Verify webhook received in Stripe dashboard
4. Check Printify account for order

---

## Testing Checklist

- [ ] Printify API connection successful
- [ ] Image upload to Printify works
- [ ] Calendar product creation with 12 months works
- [ ] Stripe checkout session creates successfully
- [ ] Redirect to Stripe checkout page works
- [ ] Test payment completes successfully
- [ ] Webhook receives payment confirmation
- [ ] Printify order submits automatically
- [ ] Order tracking displays to user

---

## Future Enhancements

1. **Order Tracking Page**: Show order status, tracking number
2. **Email Notifications**: Send confirmation emails via SendGrid
3. **Bulk Orders**: Allow ordering multiple calendars at once
4. **Discount Codes**: Stripe checkout supports promo codes
5. **Subscription Model**: Monthly calendar subscription service
6. **Wishlist**: Save favorite calendar designs for later

---

*Last Updated: 2025-10-30*
*Status: Architecture designed, ready for implementation*
