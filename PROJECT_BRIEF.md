# AI-Powered Personalized Calendar Platform - Implementation Brief

## 🎯 Project Overview

You are building a web application that allows users to create personalized calendars with AI-generated images. Users upload selfies, provide creative prompts for 12 months, see a FREE preview of their calendar, and then purchase to have it printed and shipped via Printify.

**Your Mission**: You are the best at what you do. Build this system with excellence, ask questions when needed, research APIs and best practices, and create a production-ready application.

---

## 🌟 Core User Journey

### The Complete Flow:

1. **Landing** → User arrives at the website
2. **Sign Up (FREE)** → User creates account (email + password)
3. **Upload Selfies (FREE)** → User uploads 5-10 photos of themselves
4. **Enter Prompts (FREE)** → User provides creative prompts for each of 12 months
5. **AI Generation (FREE)** → System generates 12 personalized images (5-30 min processing)
6. **Preview Calendar (FREE)** → User sees completed calendar in multiple format options
7. **💰 PAYWALL** → User clicks "Order Calendar" and chooses size/format
8. **Payment** → Stripe checkout for $39.99-49.99
9. **Order Fulfillment** → Printify creates and ships physical calendar
10. **Tracking** → User can track order status

### Critical Business Logic:
- Everything BEFORE payment is FREE (absorb AI/processing costs)
- Users only pay AFTER seeing their completed calendar
- Multiple users must work concurrently without interference
- Each user only sees/accesses their own data

---

## 🏗️ Technology Stack

### Frontend
- **Base**: Website template already exists in `/home/claude` (use what's there)
- **Framework**: Flask + Jinja2 templates (or enhance with React if needed)
- **CSS**: Bootstrap 5 or Tailwind CSS (mobile-first, responsive)
- **JavaScript**: Dropzone.js for image uploads, fetch API for async operations
- **Responsive**: MUST work perfectly on mobile, tablet, and desktop

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL
- **Task Queue**: Celery + Redis (for async AI generation)
- **File Storage**: AWS S3 or Cloudinary (NOT local filesystem)
- **Session Management**: Flask-Login + Flask-Session

### Third-Party Services
- **AI Image Generation**: [USER WILL CLARIFY - placeholder as "nano banana" or similar service]
- **Payment Processing**: Stripe
- **Print Fulfillment**: Printify API
- **Hosting**: Railway, Render, or DigitalOcean App Platform

### Key Python Packages
```
Flask==3.0.0
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
celery==5.3.4
redis==5.0.1
psycopg2-binary==2.9.9
stripe==7.8.0
requests==2.31.0
Pillow==10.1.0
opencv-python==4.8.1.78
boto3==1.34.0  # for S3
python-dotenv==1.0.0
```

---

## 📊 Database Schema

Create these tables in PostgreSQL:

```sql
-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Calendar Projects
CREATE TABLE calendar_projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'uploading',
    -- Status: uploading, processing, preview, paid, ordered, shipped, delivered
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    paid_at TIMESTAMP,
    total_cost DECIMAL(10,2),
    calendar_format VARCHAR(50)  -- portrait, landscape, square
);

-- Uploaded Selfies
CREATE TABLE uploaded_images (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES calendar_projects(id),
    s3_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Calendar Months (Master Images)
CREATE TABLE calendar_months (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES calendar_projects(id),
    month_number INTEGER NOT NULL, -- 1-12
    prompt TEXT NOT NULL,
    master_image_url VARCHAR(500),  -- 4096x4096 master on S3
    ai_generation_status VARCHAR(50) DEFAULT 'pending',
    -- Status: pending, processing, completed, failed
    generated_at TIMESTAMP,
    regeneration_count INTEGER DEFAULT 0
);

-- Printify Products
CREATE TABLE printify_products (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES calendar_projects(id) UNIQUE,
    printify_product_id VARCHAR(100) NOT NULL,
    blueprint_id INTEGER NOT NULL,
    print_provider_id INTEGER NOT NULL,
    variant_id INTEGER NOT NULL,
    mockup_urls JSONB,  -- Array of preview image URLs
    created_at TIMESTAMP DEFAULT NOW()
);

-- Orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES calendar_projects(id) UNIQUE,
    stripe_payment_intent_id VARCHAR(255),
    stripe_session_id VARCHAR(255),
    printify_order_id VARCHAR(255),
    shipping_address JSONB,
    amount_paid DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'pending',
    -- Status: pending, paid, printify_submitted, printing, shipped, delivered
    created_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP,
    shipped_at TIMESTAMP,
    tracking_number VARCHAR(255)
);

-- Payments
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    stripe_charge_id VARCHAR(255),
    amount DECIMAL(10,2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_projects_user ON calendar_projects(user_id);
CREATE INDEX idx_projects_status ON calendar_projects(status);
CREATE INDEX idx_months_project ON calendar_months(project_id);
CREATE INDEX idx_orders_project ON orders(project_id);
```

---

## 🖼️ Image Processing Strategy

### Critical Technical Requirement: One Master Image Set for All Calendar Sizes

**Problem**: Different calendars have different sizes, aspect ratios, and resolutions.
**Solution**: Generate ONE high-quality master set, then crop/scale dynamically.

### Master Image Specifications
```
Resolution: 4096×4096 pixels (square)
Format: PNG (lossless)
DPI: 300 (for print quality)
Color Space: RGB
Composition: Center-focused (important content in center 75%)
```

### Why 4096×4096?
- Large enough to crop to ANY calendar size without quality loss
- Square allows cropping to portrait, landscape, or square
- Common AI model output size
- Professional print quality (~13.65 inches at 300 DPI)

### Processing Pipeline

```python
# STAGE 1: Generate Master Images (FREE - during preview)
for month in range(1, 13):
    # Generate 4096×4096 square image with AI
    master_image = ai_service.generate({
        "prompt": user_prompts[month],
        "reference_images": user_selfies,
        "width": 4096,
        "height": 4096,
        "quality": "high"
    })
    
    # Save to S3 as master
    s3_url = upload_to_s3(master_image, f"user_{id}/masters/month_{month}_master.png")
    
    # Store in database
    save_master_to_db(project_id, month, s3_url)

# STAGE 2: Create Preview Variants (FREE - for web display)
for each calendar format (portrait, landscape, square):
    preview_image = smart_crop(
        master_image,
        target_aspect=format_aspect_ratio,
        target_width=800,  # Small for web preview
        target_height=calculated_height
    )
    
    save_preview_for_user()

# STAGE 3: Create Print-Ready Variants (AFTER PAYMENT)
for month in range(1, 13):
    # User selected "Portrait 8x10 Calendar"
    print_ready = smart_crop(
        master_image,
        target_aspect="2:3",
        target_width=2400,  # 8" at 300 DPI
        target_height=3600  # 10" at 300 DPI
    )
    
    # Upload to Printify
    printify_image_id = printify_api.upload_image(print_ready)
    
    store_printify_image_id(month, printify_image_id)
```

### Smart Cropping Algorithm

You must implement intelligent cropping that:
1. **Center-crops** from 4096×4096 to target aspect ratio
2. **Detects faces** (optional but recommended) using OpenCV
3. **Preserves important content** in the center
4. **Scales to exact print resolution** using high-quality interpolation

```python
from PIL import Image
import cv2

def smart_crop_with_face_detection(master_path, aspect_ratio, target_w, target_h):
    """
    Intelligently crop master image to target size, preserving faces
    
    Args:
        master_path: Path to 4096×4096 master image
        aspect_ratio: "2:3" (portrait), "3:2" (landscape), "1:1" (square)
        target_w: Final width in pixels
        target_h: Final height in pixels
    
    Returns:
        PIL Image ready for upload to Printify
    """
    
    # Load master
    img = Image.open(master_path)
    master_w, master_h = img.size
    
    # Parse aspect ratio
    aspect_w, aspect_h = map(int, aspect_ratio.split(':'))
    target_ratio = aspect_w / aspect_h
    
    # Calculate crop dimensions
    if target_ratio > 1:  # Landscape
        crop_w = master_w
        crop_h = int(master_w / target_ratio)
    elif target_ratio < 1:  # Portrait
        crop_h = master_h
        crop_w = int(master_h * target_ratio)
    else:  # Square
        crop_w = crop_h = min(master_w, master_h)
    
    # Detect faces for smart centering (optional enhancement)
    try:
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(img_cv, 1.3, 5)
        
        if len(faces) > 0:
            # Center on detected faces
            avg_face_x = np.mean([x + w//2 for (x, y, w, h) in faces])
            avg_face_y = np.mean([y + h//2 for (x, y, w, h) in faces])
            
            left = max(0, int(avg_face_x - crop_w // 2))
            left = min(left, master_w - crop_w)
            top = max(0, int(avg_face_y - crop_h // 2))
            top = min(top, master_h - crop_h)
        else:
            # No faces, center crop
            left = (master_w - crop_w) // 2
            top = (master_h - crop_h) // 2
    except:
        # Fallback to center crop
        left = (master_w - crop_w) // 2
        top = (master_h - crop_h) // 2
    
    # Crop
    cropped = img.crop((left, top, left + crop_w, top + crop_h))
    
    # Scale to target resolution with high-quality interpolation
    final = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    return final
```

---

## 🔌 Printify API Integration

### Key Information

**Base URL**: `https://api.printify.com/v1/`

**Authentication**: Bearer token in header
```python
headers = {
    "Authorization": f"Bearer {PRINTIFY_API_KEY}",
    "Content-Type": "application/json"
}
```

**Rate Limits**:
- 600 requests per minute
- Product publishing: 200 per 30 minutes

### Calendar Products Available

Research these calendar blueprints (IDs may vary):
- Wall Calendar 2025 Portrait: Blueprint ID ~525
- Wall Calendar 2025 Landscape: Blueprint ID ~965  
- Desk Calendar 2025: Blueprint ID ~1352
- Custom Calendar 2025: Blueprint ID ~1253

### Critical API Workflow

```python
# STEP 1: Research Available Calendars
GET /v1/catalog/blueprints.json
# Filter for calendars, note blueprint_id

# STEP 2: Get Print Providers for Calendar
GET /v1/catalog/blueprints/{blueprint_id}/print_providers.json
# Choose provider based on location, cost, reviews

# STEP 3: Get Variant Details (CRITICAL - tells you image specs)
GET /v1/catalog/blueprints/{blueprint_id}/print_providers/{provider_id}/variants.json
# Response includes placeholders array with:
# - position: "month_1", "month_2", etc. (or "january", "february")
# - width: required pixel width
# - height: required pixel height

# STEP 4: Upload 12 Images to Printify
for month in range(1, 13):
    POST /v1/uploads/images.json
    {
        "file_name": f"month_{month}.png",
        "url": "https://your-s3-bucket.com/path/to/image.png"
    }
    # Returns: {"id": "printify_image_id_12345"}

# STEP 5: Create Calendar Product
POST /v1/shops/{shop_id}/products.json
{
    "title": "Custom Calendar for User XYZ",
    "description": "AI-generated personalized calendar",
    "blueprint_id": 525,
    "print_provider_id": chosen_provider_id,
    "variants": [{
        "id": variant_id,
        "price": 3999,  # $39.99 in cents
        "is_enabled": true
    }],
    "print_areas": [{
        "variant_ids": [variant_id],
        "placeholders": [
            {
                "position": "month_1",  # Or "january"
                "images": [{
                    "id": "printify_image_id_12345",
                    "x": 0.5,  # Center position
                    "y": 0.5,
                    "scale": 1.0,
                    "angle": 0
                }]
            },
            {
                "position": "month_2",
                "images": [{"id": "printify_image_id_67890", ...}]
            },
            # ... repeat for all 12 months
        ]
    }]
}
# Returns: {"id": "product_id_abc123"}

# STEP 6: Get Product Details (for mockups)
GET /v1/shops/{shop_id}/products/{product_id}.json
# Response includes mockup image URLs in "images" array

# STEP 7: Submit Order (AFTER PAYMENT)
POST /v1/shops/{shop_id}/orders.json
{
    "external_id": stripe_payment_intent_id,
    "line_items": [{
        "product_id": "product_id_abc123",
        "variant_id": variant_id,
        "quantity": 1
    }],
    "shipping_method": 1,  # 1=standard, 2=express
    "address_to": {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@example.com",
        "phone": "+1234567890",
        "address1": "123 Main St",
        "city": "San Diego",
        "region": "CA",
        "country": "US",
        "zip": "92101"
    }
}
# Returns: {"id": "order_id_xyz789"}
```

### Important Printify Notes

1. **Research placeholder names**: You MUST call the variants endpoint to see exact placeholder position names (e.g., "january" vs "month_1")

2. **Image positioning**: The x/y coordinates use a 0.0-1.0 scale where (0.5, 0.5) is center

3. **Product vs Order creation**: You can either:
   - Create product first, then order it (recommended for preview)
   - Create product WITH order in one call (faster but no preview)

4. **Webhooks**: Set up webhooks for order status updates

---

## 💳 Stripe Payment Integration

### Setup
1. Create Stripe account at https://stripe.com
2. Get API keys (test mode first)
3. Install Stripe Python SDK

### Payment Flow

```python
from stripe import checkout

# When user clicks "Order Calendar"
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    project_id = request.json['project_id']
    calendar_format = request.json['calendar_format']  # portrait, landscape, square
    
    # Calculate price (base + shipping)
    base_price = 3999  # $39.99
    shipping = calculate_shipping(calendar_format)
    total = base_price + shipping
    
    # Create Stripe checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'AI Personalized Calendar ({calendar_format})',
                    'images': [preview_image_url],
                },
                'unit_amount': total,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='https://yourdomain.com/cancel',
        metadata={
            'project_id': project_id,
            'calendar_format': calendar_format,
            'user_id': current_user.id
        }
    )
    
    return jsonify({'checkout_url': session.url})

# Webhook handler (Stripe will call this after payment)
@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    # Handle successful payment
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Extract metadata
        project_id = session['metadata']['project_id']
        calendar_format = session['metadata']['calendar_format']
        
        # Trigger order fulfillment (Celery task)
        fulfill_order.delay(
            project_id=project_id,
            payment_intent_id=session['payment_intent'],
            calendar_format=calendar_format,
            amount_paid=session['amount_total']
        )
    
    return 'Success', 200
```

---

## ⚙️ Celery Background Tasks

### Task 1: Generate Master Images

```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task(bind=True)
def generate_calendar_images(self, project_id, prompts, selfie_urls):
    """
    Generate 12 master images using AI
    This runs in the background (takes 5-30 minutes)
    """
    
    # Update project status
    update_project_status(project_id, 'processing')
    
    for month in range(1, 13):
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': month, 'total': 12, 'status': f'Generating {month_name(month)}...'}
        )
        
        # Generate 4096×4096 master image
        try:
            master_image = ai_service.generate({
                "prompt": enhance_prompt(prompts[month]),
                "reference_images": selfie_urls,
                "width": 4096,
                "height": 4096,
                "quality": "high"
            })
            
            # Save to S3
            s3_url = upload_to_s3(
                master_image,
                f"user_{get_user_id(project_id)}/masters/month_{month:02d}_master.png"
            )
            
            # Update database
            save_master_image(project_id, month, s3_url, status='completed')
            
        except Exception as e:
            # Handle AI generation failure
            save_master_image(project_id, month, None, status='failed')
            log_error(f"Failed to generate month {month}: {str(e)}")
    
    # Generate preview variants for all formats
    generate_preview_variants(project_id)
    
    # Update project status
    update_project_status(project_id, 'preview')
    
    # Send email notification
    send_email(
        user_email=get_user_email(project_id),
        subject="Your calendar is ready!",
        template="calendar_ready.html",
        project_id=project_id
    )
    
    return {'status': 'completed', 'project_id': project_id}
```

### Task 2: Fulfill Order After Payment

```python
@celery.task
def fulfill_order(project_id, payment_intent_id, calendar_format, amount_paid):
    """
    After payment confirmed:
    1. Crop/scale masters to chosen format
    2. Upload to Printify
    3. Create calendar product
    4. Submit order
    """
    
    # Update order record
    order = create_order_record(
        project_id=project_id,
        payment_intent_id=payment_intent_id,
        amount_paid=amount_paid,
        status='processing'
    )
    
    # Get master images
    masters = get_master_images(project_id)
    
    # Get calendar specifications
    calendar_specs = get_calendar_specs(calendar_format)
    
    # Process images for this specific calendar
    printify_image_ids = []
    for month in range(1, 13):
        master_path = download_from_s3(masters[month]['s3_url'])
        
        # Crop/scale to calendar format
        print_ready = smart_crop_with_face_detection(
            master_path,
            calendar_specs['aspect_ratio'],
            calendar_specs['width_px'],
            calendar_specs['height_px']
        )
        
        # Upload to Printify
        printify_image = upload_to_printify(print_ready, f"month_{month}.png")
        printify_image_ids.append(printify_image['id'])
    
    # Create Printify product
    product = create_printify_product(
        project_id=project_id,
        image_ids=printify_image_ids,
        blueprint_id=calendar_specs['blueprint_id'],
        print_provider_id=calendar_specs['print_provider_id'],
        variant_id=calendar_specs['variant_id']
    )
    
    # Get shipping address from order
    shipping_address = get_shipping_address(order.id)
    
    # Submit order to Printify
    printify_order = submit_printify_order(
        product_id=product['id'],
        variant_id=calendar_specs['variant_id'],
        shipping_address=shipping_address,
        external_id=payment_intent_id
    )
    
    # Update order record
    update_order(
        order.id,
        printify_order_id=printify_order['id'],
        status='ordered'
    )
    
    # Send confirmation email
    send_order_confirmation_email(order.id)
    
    return {'status': 'fulfilled', 'order_id': order.id}
```

---

## 🗂️ File Structure

Your project should be organized like this:

```
/home/claude/
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── config.py                   # Configuration
│   ├── models.py                   # SQLAlchemy models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Login, signup, logout
│   │   ├── projects.py             # Calendar creation flow
│   │   ├── payments.py             # Stripe integration
│   │   └── webhooks.py             # Stripe & Printify webhooks
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py           # AI image generation
│   │   ├── printify_service.py     # Printify API client
│   │   ├── storage_service.py      # S3/Cloudinary
│   │   └── image_processing.py     # Crop/scale functions
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── celery_tasks.py         # Background jobs
│   ├── templates/                  # Jinja2 templates (use existing)
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── signup.html
│   │   ├── upload.html
│   │   ├── prompts.html
│   │   ├── progress.html
│   │   ├── preview.html            # CRITICAL: Show calendar before payment
│   │   ├── checkout.html
│   │   └── success.html
│   └── static/                     # CSS, JS, images (use existing)
│       ├── css/
│       ├── js/
│       └── img/
├── migrations/                     # Database migrations (Alembic)
├── tests/                          # Unit and integration tests
├── .env                            # Environment variables (DO NOT COMMIT)
├── requirements.txt                # Python dependencies
├── celery_worker.py                # Celery worker entry point
├── run.py                          # Flask app entry point
└── README.md                       # Documentation
```

---

## 🔐 Environment Variables

Create a `.env` file with these variables:

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=development
FLASK_SECRET_KEY=generate-strong-random-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/calendar_db

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS S3 (or use Cloudinary)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-west-2

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Printify
PRINTIFY_API_KEY=your-printify-token
PRINTIFY_SHOP_ID=your-shop-id

# AI Service (USER WILL PROVIDE)
AI_API_KEY=your-ai-service-key
AI_API_URL=https://api.ai-service.com/v1/generate

# Email (SendGrid or similar)
SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@yourdomain.com

# Security
RECAPTCHA_SITE_KEY=your-recaptcha-site-key
RECAPTCHA_SECRET_KEY=your-recaptcha-secret

# Monitoring
SENTRY_DSN=your-sentry-dsn  # Optional but recommended
```

---

## 🎨 User Interface Requirements

### Key Pages

**1. Landing Page** (`index.html`)
- Hero section with example calendar
- "Create Your Calendar - See Preview FREE" CTA
- Show 3-step process: Upload → Generate → Order
- Testimonials, FAQ
- Mobile responsive

**2. Upload Page** (`upload.html`)
- Dropzone.js drag-and-drop interface
- "Upload 5-10 selfies for best results"
- Image preview grid
- Progress indicator
- "Continue" button when minimum uploaded

**3. Prompts Page** (`prompts.html`)
- 12 input fields (one per month)
- Prompt suggestions/examples
- Character limit (100-200 chars)
- "Generate My Calendar" button
- Save draft functionality

**4. Progress Page** (`progress.html`)
- Real-time progress bar (0-100%)
- "Generating January..." status updates
- Estimated time remaining (10-15 min)
- Can close browser and return later
- Email when complete

**5. Preview Page** (`preview.html`) - CRITICAL
- Show completed calendar in chosen format
- Tabs for different formats: Portrait | Landscape | Square
- Click to zoom each month
- "Regenerate this month" option (optional)
- **Prominent "Order Your Calendar - $39.99" CTA button**
- "Edit Prompts" option

**6. Checkout Page** (`checkout.html`)
- Calendar format selection (if not chosen)
- Pricing breakdown:
  * Calendar: $39.99
  * Shipping: $X.XX
  * Total: $XX.XX
- Shipping address form
- Stripe payment element
- Order summary with preview
- "Place Order" button

**7. Success Page** (`success.html`)
- Order confirmation
- Order number
- Email sent confirmation
- Timeline: Printing (2-3 days) → Shipping (5-7 days)
- "Track Your Order" link

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up Flask app structure
- [ ] Configure PostgreSQL database
- [ ] Set up Redis and Celery
- [ ] Implement user authentication (signup, login, logout)
- [ ] Email verification (optional but recommended)
- [ ] Basic templates from existing website

### Phase 2: Image Upload & Storage (Week 1-2)
- [ ] S3 or Cloudinary integration
- [ ] Image upload with Dropzone.js
- [ ] Thumbnail generation
- [ ] File validation and security
- [ ] Store uploaded images with user association

### Phase 3: AI Integration (Week 2)
- [ ] Research AI service API (user will provide details)
- [ ] Create AI service client
- [ ] Implement prompt enhancement
- [ ] Generate 4096×4096 master images
- [ ] Handle AI errors and retries
- [ ] Celery task for async generation

### Phase 4: Image Processing (Week 2-3)
- [ ] Implement smart cropping algorithm
- [ ] Add face detection (OpenCV)
- [ ] Generate preview variants
- [ ] Generate print-ready variants
- [ ] Quality validation (DPI check)

### Phase 5: Printify Integration (Week 3)
- [ ] Research Printify calendar blueprints
- [ ] Implement Printify API client
- [ ] Upload images to Printify
- [ ] Create calendar products
- [ ] Get mockup images
- [ ] Calculate shipping costs

### Phase 6: Preview & Payment (Week 3-4)
- [ ] Build preview interface
- [ ] Format selection (portrait/landscape/square)
- [ ] Stripe checkout integration
- [ ] Payment webhook handler
- [ ] Order record creation

### Phase 7: Order Fulfillment (Week 4)
- [ ] Celery task for order processing
- [ ] Crop/scale images to chosen format
- [ ] Create Printify product for specific variant
- [ ] Submit order to Printify
- [ ] Printify webhook handler
- [ ] Order status tracking

### Phase 8: User Dashboard (Week 4-5)
- [ ] View all user projects
- [ ] Project status indicators
- [ ] Order history
- [ ] Tracking information
- [ ] Re-order functionality

### Phase 9: Polish & Testing (Week 5-6)
- [ ] Responsive design testing
- [ ] Error handling and logging
- [ ] Email notifications
- [ ] Performance optimization
- [ ] Security audit
- [ ] Load testing

### Phase 10: Deployment (Week 6)
- [ ] Set up hosting (Railway/Render/DO)
- [ ] Configure production database
- [ ] Set up Redis instance
- [ ] Deploy Celery workers
- [ ] SSL certificate
- [ ] Domain configuration
- [ ] Monitoring (Sentry)

---

## 🔍 Research Tasks

You should research and clarify:

1. **AI Service Details**
   - What is "nano banana"? (Banana.dev? Or different service?)
   - API documentation URL
   - Pricing per image
   - Rate limits
   - Supported resolutions

2. **Printify Calendar Specifics**
   - Exact blueprint IDs for 2025 calendars
   - Placeholder position names (month_1? january?)
   - Print area dimensions for each variant
   - Best print providers by location

3. **Optimal Calendar Specs**
   - Which calendar size sells best?
   - Price points for different sizes
   - Shipping costs by provider

---

## 📈 Success Metrics

Track these KPIs:

- **Conversion Rate**: % of previews that convert to paid orders
- **Target**: >30% conversion rate
- **Average Processing Time**: Time from prompt to preview
- **Target**: <15 minutes
- **Order Fulfillment Time**: Time from payment to shipped
- **Target**: <5 days
- **AI Generation Success Rate**: % of successful generations
- **Target**: >95%
- **Customer Satisfaction**: Review ratings
- **Target**: >4.5 stars

---

## 💰 Cost Analysis

### Per Calendar (Before Payment)
- AI Generation (12 images): $0.12 - $6.00
- S3 Storage: ~$0.01
- Processing (compute): ~$0.02
- **Total Upfront Cost**: ~$0.15 - $6.03

### Per Calendar (After Payment)
- Printify Base Cost: $6.41 - $12.00
- Shipping: $4.00 - $8.00
- Stripe Fees: ~$1.46 (2.9% + $0.30 on $49.99)
- **Total Fulfillment Cost**: ~$11.87 - $21.46

### Profit Analysis
```
Sell Price: $49.99
Total Cost (30% convert): $6.03/0.30 + $21.46 = $41.56
Profit: $49.99 - $41.56 = $8.43 per sale ✅

Sell Price: $39.99
Total Cost (30% convert): $6.03/0.30 + $21.46 = $41.56
Profit: $39.99 - $41.56 = -$1.57 per sale ❌

Sell Price: $39.99
Total Cost (50% convert): $6.03/0.50 + $21.46 = $33.52
Profit: $39.99 - $33.52 = $6.47 per sale ✅
```

**Recommendation**: Price at $49.99 or ensure >40% conversion at $39.99

---

## 🛡️ Security Considerations

**Critical Security Requirements:**

1. **User Data Isolation**
   - Every query MUST filter by user_id
   - No user can access another user's data
   - Test with multiple simultaneous users

2. **File Upload Security**
   - Validate file types (only JPG, PNG)
   - Limit file sizes (10MB max)
   - Scan for malicious content
   - Use signed URLs for S3 access

3. **API Key Security**
   - NEVER commit .env to git
   - Use environment variables only
   - Rotate keys regularly
   - Monitor API usage for abuse

4. **Payment Security**
   - PCI compliance (Stripe handles)
   - Verify webhook signatures
   - Prevent double charging
   - Handle payment failures gracefully

5. **Rate Limiting**
   - Limit signup attempts
   - Limit generation requests per user
   - Prevent API abuse
   - Use Flask-Limiter

6. **CSRF Protection**
   - Use Flask-WTF for forms
   - Validate all POST requests
   - Secure session cookies

---

## 🐛 Error Handling

**Implement graceful error handling for:**

- AI generation failures → Retry 3 times, then notify user
- Printify API errors → Retry with exponential backoff
- Payment failures → Clear error messages, offer retry
- Image upload errors → Validate before upload, clear feedback
- Webhook failures → Log and alert, ensure idempotency

**Logging Strategy:**
- Use Python logging module
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Store logs centrally (CloudWatch, Papertrail, etc.)
- Set up error alerts (Sentry)

---

## 📧 Email Notifications

**Required Email Templates:**

1. **Welcome Email** (on signup)
2. **Email Verification** (if enabled)
3. **Generation Started** (calendar processing begun)
4. **Generation Complete** (preview ready)
5. **Payment Confirmation** (order received)
6. **Order Shipped** (tracking info)
7. **Delivery Confirmed** (order delivered)

Use SendGrid or AWS SES for reliable delivery.

---

## 🎯 Your Mission

You are implementing a production-ready, scalable platform. Your goals:

1. ✅ **Build it right**: Follow best practices, write clean code
2. ✅ **Make it work**: Test thoroughly, handle edge cases
3. ✅ **Make it fast**: Optimize performance, use caching
4. ✅ **Make it secure**: Protect user data, validate inputs
5. ✅ **Make it reliable**: Error handling, monitoring, logging

**You are empowered to:**
- Research APIs and services as needed
- Ask clarifying questions before implementing
- Suggest improvements to the architecture
- Make technical decisions that improve the product
- Use your judgment on implementation details

**Key Principle**: Users pay ONLY after seeing their calendar. The preview must be perfect, the payment flow must be seamless, and the fulfillment must be reliable.

---

## 🤝 Communication Protocol

**When you need clarification:**
1. State what you understand
2. List your specific questions
3. Propose potential solutions
4. Wait for confirmation before proceeding

**When you complete a phase:**
1. Summarize what was built
2. List any blockers or issues
3. Provide test instructions
4. Suggest next steps

**When you encounter an issue:**
1. Describe the problem clearly
2. Show what you've tried
3. Propose 2-3 potential solutions
4. Request guidance on the best approach

---

## 🏁 Getting Started

**Your first tasks:**

1. Review the existing website template in `/home/claude`
2. Set up the Python virtual environment
3. Install required packages from requirements.txt (create it)
4. Initialize PostgreSQL database
5. Set up Redis for Celery
6. Create basic Flask app structure
7. Implement user authentication
8. Build image upload functionality

**Start with these questions:**
- What template/framework is the existing website using?
- Should I use the existing styling or create new?
- Do we have a preferred AI service, or should I make it pluggable?
- What's the target deployment platform?

---

## 📚 Resources

**Documentation to reference:**
- Flask: https://flask.palletsprojects.com/
- Celery: https://docs.celeryq.dev/
- Printify API: https://developers.printify.com/
- Stripe API: https://stripe.com/docs/api
- SQLAlchemy: https://docs.sqlalchemy.org/

**You are the expert. Build something amazing!** 🚀
