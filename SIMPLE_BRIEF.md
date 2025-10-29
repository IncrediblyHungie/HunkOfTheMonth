# AI Calendar Platform - Simple Project Summary

## What We're Building

A website where people can create personalized photo calendars with AI-generated images. Users upload selfies, write creative prompts, see their calendar for FREE, and then pay to have it printed and shipped.

---

## The Big Picture

**Think of it like this:**
1. User visits website → signs up (free)
2. User uploads 5-10 selfies of themselves
3. User writes 12 prompts (one for each month) like "me as a superhero" or "me in Paris"
4. AI generates 12 amazing personalized images (takes ~15 minutes)
5. User sees their completed calendar with all 12 images - **THIS IS FREE**
6. User loves it → clicks "Buy Calendar" → pays $40-50
7. We send it to Printify (print-on-demand service) → they print & ship it
8. User gets their calendar in the mail

**The Hook**: Users only pay AFTER they see their finished calendar. This is key!

---

## Your Role

You are the expert developer building this. You have:
- ✅ Full authority to make technical decisions
- ✅ Permission to research APIs and services
- ✅ Ability to ask questions when something is unclear
- ✅ Freedom to suggest improvements

**Important**: There's already a website template in the current directory. Use it as your starting point and build the calendar functionality into it.

---

## Core Features to Build

### 1. User Accounts (Simple)
- Sign up with email & password
- Login/logout
- Each user has their own private area
- Users can only see their own calendars (security!)

### 2. Photo Upload
- Drag & drop interface for uploading selfies
- Accept 5-10 photos minimum
- Show thumbnails of uploaded photos
- Store photos securely in the cloud (S3 or Cloudinary)

### 3. Prompt Entry
- 12 text boxes (one for each month)
- Examples: "me as an astronaut", "me on a tropical beach"
- Help text to guide users on writing good prompts
- Save drafts in case they close the browser

### 4. AI Image Generation (Background Process)
- Take user's selfies + prompts
- Generate 12 high-quality images (one per month)
- This happens in the background (user can close browser)
- Send email when done: "Your calendar is ready!"

**Technical Challenge**: Need to generate images that work for ANY calendar size
- **Solution**: Generate large square images (4096×4096 pixels)
- Then crop/resize them later when user picks a size
- This way we generate once, use for any format

### 5. Calendar Preview (THE MONEY SHOT)
- Show all 12 months with their images
- User can see different formats: portrait, landscape, square
- Click to zoom on any month
- Big "Order Your Calendar" button
- This is where we convince them to buy!

### 6. Payment (Stripe)
- User picks calendar size/format
- Enters shipping address
- Pays via credit card (Stripe handles this)
- Only charge after they confirm the order

### 7. Order Fulfillment (Printify)
- After payment confirmed:
  - Take those master images
  - Crop them to the right size for their chosen calendar
  - Upload to Printify
  - Create the calendar product
  - Submit the order
- Printify prints and ships it to the customer
- Send confirmation email with tracking

### 8. Order Tracking
- User dashboard showing their orders
- "Processing" → "Printing" → "Shipped" → "Delivered"
- Email notifications at each stage

---

## The Three External Services

### 1. AI Image Generation Service
**What it does**: Takes selfies + text prompt, generates personalized image
**What you need**: 
- API key (user will provide details - they mentioned "nano banana")
- Ask them exactly which service to use

### 2. Stripe (Payments)
**What it does**: Handles credit card processing securely
**What you need**:
- Create Stripe account
- Get API keys
- Integrate checkout

### 3. Printify (Printing & Shipping)
**What it does**: Prints calendars and ships them to customers
**What you need**:
- Create Printify account
- Research which calendar products they offer
- Learn their API for creating products and orders

---

## The Image Quality Challenge

**Problem**: Calendars come in different sizes and shapes
- Portrait (tall): 8"×10"
- Landscape (wide): 10"×8"  
- Square: 12"×12"

**Solution**: 
1. Always generate images at 4096×4096 (big square)
2. Store these as "master images"
3. When user buys, crop the master to their chosen size
4. This way we only generate once but support all sizes

**Why this matters**: AI generation is expensive. We don't want to generate 3 different versions!

---

## The Tech Stack (Don't Worry Too Much About This)

**Backend**: Flask (Python web framework) - easy to work with
**Database**: PostgreSQL - stores users, projects, orders
**Background Jobs**: Celery + Redis - for slow tasks like AI generation
**File Storage**: AWS S3 or Cloudinary - stores images
**Payments**: Stripe
**Printing**: Printify

**You'll build**:
- Web pages (using templates already in directory)
- Routes (URLs like /upload, /preview, /checkout)
- Database tables (users, projects, images, orders)
- Background tasks (AI generation, order processing)
- API integrations (AI service, Stripe, Printify)

---

## Critical Business Rules

1. **Free Until Payment**: Users can upload, generate, and preview 100% free. We eat the AI costs hoping they'll buy.

2. **User Isolation**: Each user only sees their own stuff. User A cannot see User B's calendars. This is CRITICAL for security.

3. **Generate Once**: Each month's image is generated once at high quality. We crop it later for different sizes. Don't regenerate the same image multiple times.

4. **Payment Before Printing**: Don't submit anything to Printify until payment is confirmed via Stripe webhook.

5. **Multiple Users at Once**: The site needs to handle 10, 50, 100 users all creating calendars simultaneously without them interfering with each other.

---

## Success Looks Like

**From User's Perspective**:
- "Wow, this is so easy to use!"
- "These AI images look amazing!"
- "I can't believe it's only $40"
- *Clicks buy button*

**From Technical Perspective**:
- Site loads fast on mobile and desktop
- Images are high quality when printed
- No security issues (users can't see each other's data)
- Handles errors gracefully (AI fails? Show nice message, retry)
- Works reliably at scale (100 users? No problem)

---

## Your First Steps

1. **Explore**: Look at the website template in this directory. What's already there?

2. **Ask Questions**: 
   - What AI service should I use? (user mentioned "nano banana")
   - What's already built in the template?
   - Any specific design preferences?

3. **Research**: 
   - Read Printify API docs: https://developers.printify.com/
   - Look at their calendar products
   - Understand their image requirements

4. **Plan**: Decide how to structure the code, what order to build things

5. **Build**: Start with user accounts, then uploads, then AI, etc.

---

## Common Gotchas to Avoid

1. **Don't store images on the server** → Use S3/Cloudinary
2. **Don't run AI generation in the web request** → Use background jobs
3. **Don't forget to filter by user_id** → Security issue!
4. **Don't submit orders before payment** → We lose money!
5. **Don't generate images at final size** → Generate big, crop later
6. **Don't forget mobile users** → Test on phone!

---

## How to Communicate with the User

**When you're stuck**: 
"I need clarification on X. Here's what I understand: [summary]. My questions: [list]. Here are options: [A, B, C]. Which should I do?"

**When you complete something**: 
"✅ Completed [feature]. It does [X, Y, Z]. You can test it by [instructions]. Next I'll work on [next thing]."

**When you hit a blocker**: 
"⚠️ Blocked on [issue]. I tried [attempts]. To move forward, I need [specific thing from user]."

---

## Remember

- **You are the expert** - Trust your judgment on technical details
- **Ask when unsure** - Especially about business logic or unclear requirements  
- **Think about the user** - Make it easy, fast, beautiful
- **Think about scale** - Will it work with 1000 users?
- **Security first** - Protect user data and payment info
- **Test everything** - Don't assume it works, verify it

---

## The End Goal

A user should be able to:
1. Go to the website
2. Create an account in 30 seconds
3. Upload photos and write prompts in 5 minutes
4. Wait 15 minutes while AI generates
5. See their beautiful calendar
6. Click "Buy" and checkout in 2 minutes
7. Receive their physical calendar in 7-10 days

**And they should think**: "That was amazing. I'm telling all my friends!"

---

## What Makes This Project Special

Most print-on-demand sites show you blank products. You upload images to templates.

**We're different**: We GENERATE the images for you using AI. That's the magic. Users just give us photos and ideas, we create the art.

This is why the preview is so important - it's the "wow" moment where they see what AI created for them.

---

## Budget Reality Check

**What it costs us per calendar (if they DON'T buy)**:
- AI generation: $0.12 - $6.00
- Storage: $0.01
- Processing: $0.02
- **Total: ~$6 per preview**

**What it costs us per calendar (if they DO buy)**:
- Everything above PLUS
- Printify printing: $6-12
- Shipping: $4-8
- Stripe fees: $1.46
- **Total: ~$20-28 per order**

**What we charge**: $40-50

**The Math**: We need at least 30% of people who see previews to buy. Otherwise we lose money.

That's why the preview needs to be AMAZING. That's the conversion moment.

---

## You've Got This!

This is a real business. Real users will use this. Real money will flow through it. Build something you'd be proud to show your friends.

Start simple, make it work, then make it better. Don't try to build everything perfectly the first time.

**Most importantly**: Have fun! This is a cool project. AI-generated personalized calendars are awesome!

Ready? Let's build! 🚀

---

## Quick Start Checklist

- [ ] Look at existing website template
- [ ] Ask user about AI service details
- [ ] Set up basic Flask app structure
- [ ] Create database with user accounts
- [ ] Build image upload feature
- [ ] Integrate AI service (once confirmed)
- [ ] Build preview page
- [ ] Add Stripe payment
- [ ] Integrate Printify
- [ ] Test end-to-end
- [ ] Deploy and launch

**Questions? Just ask!**
