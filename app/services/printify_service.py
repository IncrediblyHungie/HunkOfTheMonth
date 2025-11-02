"""
Printify API integration for calendar fulfillment
Handles image uploads, product creation, and order submission
"""
import requests
import base64
import time
from flask import current_app

PRINTIFY_API_BASE = "https://api.printify.com/v1"

# Calendar product configurations
CALENDAR_PRODUCTS = {
    'calendar_2026': {
        'blueprint_id': 1253,
        'print_provider_id': 234,
        'variant_id': 94860,
        'name': 'Calendar (2026)',
        'size': '10.8" × 8.4"'
    },
    'desktop': {
        'blueprint_id': 1170,
        'print_provider_id': None,  # TODO: Get from API
        'variant_id': None,
        'name': 'Desktop Calendar',
        'size': '10" × 5"'
    },
    'standard_wall': {
        'blueprint_id': 965,
        'print_provider_id': None,  # TODO: Get from API
        'variant_id': None,
        'name': 'Standard Wall Calendar (2026)',
        'size': 'Various'
    }
}

def get_headers():
    """Get authorization headers for Printify API"""
    token = current_app.config.get('PRINTIFY_API_TOKEN')
    if not token:
        raise ValueError("PRINTIFY_API_TOKEN not configured")

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def upload_image(image_data_bytes, filename="month.jpg"):
    """
    Upload image to Printify Media Library

    Args:
        image_data_bytes: Raw image bytes (JPEG/PNG)
        filename: Filename for the upload

    Returns:
        dict: Upload data with 'id' and 'file_name'
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

    print(f"  ✓ Uploaded {filename}: {upload_data['id']}")
    return upload_data

def create_calendar_product(product_type, month_image_ids, title="Custom Hunk Calendar 2026"):
    """
    Create a calendar product with user's images

    Args:
        product_type: 'calendar_2026', 'desktop', or 'standard_wall'
        month_image_ids: Dict mapping month names to Printify upload IDs
                         {"january": "upload_id_1", "february": "upload_id_2", ...}
        title: Product title

    Returns:
        str: Printify product ID
    """
    if product_type not in CALENDAR_PRODUCTS:
        raise ValueError(f"Invalid product type: {product_type}")

    config = CALENDAR_PRODUCTS[product_type]

    if not config['print_provider_id'] or not config['variant_id']:
        raise ValueError(f"Product type {product_type} not fully configured yet")

    # Construct print_areas
    print_areas = [
        {
            "variant_ids": [config['variant_id']],
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
        if month not in month_image_ids:
            raise ValueError(f"Missing image for {month}")

        print_areas[0]["placeholders"].append({
            "position": month,
            "images": [
                {
                    "id": month_image_ids[month],
                    "x": 0.5,
                    "y": 0.5,
                    "scale": 1.0,
                    "angle": 0
                }
            ]
        })

    payload = {
        "title": title,
        "description": "Personalized calendar with AI-generated hunk images",
        "blueprint_id": config['blueprint_id'],
        "print_provider_id": config['print_provider_id'],
        "variants": [
            {
                "id": config['variant_id'],
                "price": 2499,  # Price in cents - Printify adds their margin
                "is_enabled": True
            }
        ],
        "print_areas": print_areas
    }

    # Get shop ID
    shop_id = get_shop_id()

    response = requests.post(
        f"{PRINTIFY_API_BASE}/shops/{shop_id}/products.json",
        headers=get_headers(),
        json=payload
    )

    response.raise_for_status()
    product_data = response.json()

    print(f"  ✓ Created product: {product_data['id']}")
    return product_data['id']

def publish_product(product_id):
    """
    Publish product to make it available for ordering

    Args:
        product_id: Printify product ID

    Returns:
        bool: Success status
    """
    shop_id = get_shop_id()

    payload = {
        "title": True,
        "description": True,
        "images": True,
        "variants": True,
        "tags": True
    }

    response = requests.post(
        f"{PRINTIFY_API_BASE}/shops/{shop_id}/products/{product_id}/publish.json",
        headers=get_headers(),
        json=payload
    )

    response.raise_for_status()
    print(f"  ✓ Published product: {product_id}")
    return True

def create_order(product_id, variant_id, quantity, shipping_address, customer_email):
    """
    Create Printify order for fulfillment

    Args:
        product_id: Printify product ID
        variant_id: Variant ID
        quantity: Number of calendars (usually 1)
        shipping_address: Dict with address fields
        customer_email: Customer email

    Returns:
        str: Printify order ID
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

    print(f"  ✓ Created order: {order_data['id']}")
    return order_data['id']

def submit_order(order_id):
    """
    Submit order to Printify for production

    Args:
        order_id: Printify order ID

    Returns:
        bool: Success status
    """
    shop_id = get_shop_id()

    response = requests.post(
        f"{PRINTIFY_API_BASE}/shops/{shop_id}/orders/{order_id}/send_to_production.json",
        headers=get_headers()
    )

    response.raise_for_status()
    print(f"  ✓ Submitted order to production: {order_id}")
    return True

def get_shop_id():
    """
    Get first shop ID from Printify account
    Caches the result in app config
    """
    if current_app.config.get('PRINTIFY_SHOP_ID'):
        return current_app.config['PRINTIFY_SHOP_ID']

    response = requests.get(
        f"{PRINTIFY_API_BASE}/shops.json",
        headers=get_headers()
    )
    response.raise_for_status()
    shops = response.json()

    if not shops:
        raise Exception("No Printify shops found. Please create a shop at printify.com first.")

    shop_id = shops[0]['id']
    current_app.config['PRINTIFY_SHOP_ID'] = shop_id
    print(f"  ℹ Using Printify shop: {shop_id}")
    return shop_id
