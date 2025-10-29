# 👋 START HERE - Claude Code

## Welcome!

You're building an **AI-powered personalized calendar platform**. This is going to be awesome!

---

## 📁 Important Files in This Directory

1. **SIMPLE_BRIEF.md** ← **READ THIS FIRST!**
   - Non-technical overview of what we're building
   - Explains the business model and user journey
   - Easy to understand, no jargon

2. **PROJECT_BRIEF.md** ← Read this second
   - Detailed technical specifications
   - Database schemas, API details, code examples
   - Your reference guide for implementation

3. **CHECKLIST.md** ← Use this to track progress
   - Step-by-step implementation checklist
   - Mark off tasks as you complete them

4. **TECHNICAL_REFERENCE.md** ← Use when coding
   - Code snippets and patterns
   - Quick copy-paste examples

---

## 🎯 What We're Building (1-Minute Version)

A website where:
1. Users upload selfies
2. Write creative prompts for 12 months
3. AI generates 12 personalized images (FREE)
4. User sees completed calendar (FREE)
5. User pays $40-50 to buy it
6. Printify prints and ships it

**Your job**: Build the whole system end-to-end.

---

## 🚦 Your First Actions

### Step 1: Explore What's Already Here
```bash
# Look around the current directory
ls -la

# Check if there's already a website template
find . -name "*.html" -o -name "*.css"

# Check for any existing Python files
find . -name "*.py"
```

**Then report back**: "Here's what I found: [list]. Should I use this as the base or start fresh?"

### Step 2: Clarify the AI Service
Ask the user:
> "You mentioned 'nano banana' for AI image generation. Can you clarify:
> - Is this Banana.dev?
> - Or a different service?
> - Do you have API credentials already?
> - What's the API documentation URL?"

### Step 3: Research Printify
Visit: https://developers.printify.com/

Find out:
- What calendar blueprint IDs are available?
- What are the placeholder position names for months?
- What image dimensions are required?

### Step 4: Make a Plan
Based on what you find, write:
> "Here's my implementation plan:
> - Start with [X]
> - Then build [Y]
> - Then add [Z]
> - Does this approach make sense?"

---

## 🎨 Design Philosophy

**Keep it simple**:
- Mobile-first (most users will be on phones)
- Big buttons, clear text
- Fast loading (users are impatient)
- Beautiful images (this is a visual product!)

**Make it reliable**:
- Handle errors gracefully
- Give good feedback ("Generating month 3 of 12...")
- Work offline when possible (save drafts)
- Never lose user data

**Make it secure**:
- Users can't see each other's calendars
- Payment info is protected (Stripe handles this)
- Images are private
- No SQL injection, XSS, etc.

---

## 🎪 The Three Main Moments

### Moment 1: Upload & Prompts (5 minutes)
This should be fun and easy. Make it feel creative!

### Moment 2: Generation (15 minutes)  
This is passive waiting. Keep them updated, maybe show examples of other calendars.

### Moment 3: Preview (THE BIG MOMENT!)
This is where they decide to buy. Make it stunning!
- Show all 12 images beautifully
- Easy to zoom and inspect
- Clear "Buy" button
- Show different calendar format options

---

## 🔥 Critical Success Factors

1. **Image Quality**: Must look amazing when printed
2. **Preview Experience**: Must wow the user
3. **Speed**: Each step should feel fast
4. **Reliability**: Must work every time
5. **Security**: Protect user data and payments

---

## 💡 Pro Tips

**Do's**:
- ✅ Test on mobile constantly
- ✅ Use the existing template as a base
- ✅ Ask questions early and often
- ✅ Build in small increments (test each piece)
- ✅ Think about what happens when things fail

**Don'ts**:
- ❌ Don't store images locally (use S3)
- ❌ Don't block the web request with AI generation (use background jobs)
- ❌ Don't forget to filter by user_id (security!)
- ❌ Don't submit to Printify before payment
- ❌ Don't guess - ask when unsure

---

## 🗺️ The Big Picture Flow

```
User arrives → Sign up → Upload selfies → Enter prompts → AI generates
→ See preview → Choose format → Pay via Stripe → Send to Printify
→ Printify prints → Ships to user → Everyone's happy! 🎉
```

**Your job**: Build every step of this flow.

---

## 📞 How to Get Help

**Need clarification?** Ask specific questions:
- "Should users be able to edit prompts after generation?"
- "What should happen if AI generation fails?"
- "Which calendar size should be the default?"

**Hit a blocker?** Explain what you tried:
- "I tried X, Y, and Z. None worked because [reason]."
- "To proceed, I need [specific thing]."

**Want feedback?** Show your work:
- "I built [feature]. Here's how it works: [demo]."
- "Does this match the vision?"

---

## 🏆 Definition of Done

The project is done when:
- [ ] A user can go from landing page to purchased calendar in 25 minutes
- [ ] The preview looks professional and impressive
- [ ] Payment works smoothly via Stripe
- [ ] Orders successfully go to Printify
- [ ] Multiple users can use the site simultaneously
- [ ] It works perfectly on iPhone, Android, and desktop
- [ ] All user data is secure and isolated
- [ ] Error handling is graceful (no crashes)

---

## 🎬 Ready to Start?

1. Read **SIMPLE_BRIEF.md** (10 min)
2. Skim **PROJECT_BRIEF.md** (20 min)
3. Explore the existing template (10 min)
4. Ask your clarifying questions
5. Make your implementation plan
6. Start building! 🚀

---

## 📊 Expected Timeline

- **Week 1-2**: User accounts, uploads, AI integration
- **Week 3-4**: Preview page, Stripe, Printify
- **Week 5-6**: Polish, testing, deployment

But honestly? Just focus on building one piece at a time. Don't think about the whole timeline.

---

## 💪 You've Got This!

You're working on a real product that real people will use and love. 

Build something you'd be proud of. Build something that works. Build something beautiful.

And remember: **Start simple. Make it work. Then make it better.**

Let's go! 🚀

---

## 🔄 First Task

After reading this, do:

```bash
# 1. Check what's in the current directory
ls -la

# 2. Report what you found
# Then ask: "What should I focus on first?"
```

We'll take it from there!
