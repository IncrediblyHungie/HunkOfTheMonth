# AI Image Generation Setup

## Overview

KevCal now supports AI-generated themed images using Stable Diffusion! Instead of using placeholder templates, the system generates professional muscular/hunk-style images for each calendar theme.

## How It Works

### Without AI (Default)
1. Upload photo → Extract face → Overlay on placeholder templates → Add calendar grid

### With AI (Enhanced)
1. Upload photo → **Generate AI themed images** → Extract face → Overlay on AI images → Add calendar grid

## Setup Replicate API

### Step 1: Get Replicate API Token

1. Visit https://replicate.com
2. Sign up for a free account
3. Go to https://replicate.com/account/api-tokens
4. Copy your API token

### Step 2: Add Token to Environment

```bash
# Edit .env file
echo 'REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx' >> .env
```

Or manually edit `.env`:
```
PRINTFUL_API_KEY=dn8ChPBdbe0QMZERdFeHltvlWNojVqomgmMELFtc
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HOST=0.0.0.0
PORT=8000
```

### Step 3: Install replicate Package

```bash
source venv/bin/activate
pip install replicate==1.5.3
```

### Step 4: Restart Server

```bash
# Stop current server (Ctrl+C)
python app.py
```

## AI-Generated Themes

The system generates **12 muscular/hunk-style themed images**:

### January - Shirtless Firefighter
> "Shirtless muscular firefighter with defined abs, wearing firefighter pants and suspenders, holding axe, standing heroically in front of burning building with flames and smoke"

### February - Fighter Pilot
> "Handsome muscular fighter pilot in open flight suit showing muscular chest, sitting in F-16 cockpit, wearing aviator sunglasses"

### March - Astronaut
> "Athletic astronaut in fitted white NASA space suit unzipped to show muscular chest, floating in international space station, Earth visible through window"

### April - Cowboy
> "Shirtless muscular cowboy with six-pack abs wearing worn jeans and cowboy hat, on horseback at golden sunset"

### May - Chef
> "Handsome shirtless chef with muscular torso wearing white chef's hat and apron, cooking with flames in gourmet kitchen"

### June - Rock Star
> "Shirtless muscular rock star guitarist with defined abs and tattoos, playing electric guitar on stage, dramatic purple and red concert lighting"

### July - Deep Sea Diver
> "Athletic diver in partially unzipped wetsuit showing muscular chest, underwater surrounded by colorful coral reef"

### August - Mountain Climber
> "Shirtless muscular mountain climber with climbing harness and ropes, standing at snowy mountain summit, defined muscles glistening"

### September - Race Car Driver
> "Handsome muscular Formula 1 driver with racing suit unzipped to waist showing six-pack abs, sitting in red F1 car"

### October - Samurai Warrior
> "Shirtless muscular samurai warrior showing defined chest and abs, wearing traditional hakama pants, holding katana sword, cherry blossoms falling"

### November - Viking Warrior
> "Muscular shirtless viking warrior with long beard and battle scars, wearing fur cape and leather armor, holding shield and battle axe, on viking longship"

### December - Secret Agent
> "Handsome muscular secret agent in unbuttoned black tuxedo showing muscular chest, holding silenced pistol, elegant casino background, james bond style"

## Performance

### With AI Generation:
- **AI Image Generation**: ~10-15 seconds per image (120-180 seconds total for 12)
- **Face Overlay**: ~0.5 seconds per image
- **Calendar Grid**: ~0.1 seconds per image
- **Total Time**: ~3-4 minutes for complete calendar with AI

### Without AI (Placeholder):
- **Face Overlay**: ~0.5 seconds per image
- **Calendar Grid**: ~0.1 seconds per image
- **Total Time**: ~10-20 seconds for complete calendar

## Cost

Replicate charges per generation:

- **Stable Diffusion XL**: ~$0.003-0.005 per image
- **12 calendar images**: ~$0.04-0.06 per calendar
- **Free tier**: Includes $5 credit (100+ calendars)

## Testing AI Generation

### Check if AI is Enabled
```bash
curl http://localhost:8000/api/ai-status
```

Should return:
```json
{
  "ai_enabled": true,
  "message": "AI image generation is enabled"
}
```

### Generate Calendar with AI

1. Open http://localhost:8000
2. Upload photos
3. Click "Generate Calendar Images"
4. Watch progress: "Generating AI image for Firefighter..."
5. Each month will show: AI generation → Face overlay → Calendar grid
6. Total time: 3-4 minutes with AI

## Fallback Behavior

If AI generation fails or is disabled:
- System automatically falls back to placeholder templates
- No error shown to user
- Calendar still generates successfully
- Faster generation (10-20 seconds)

## Customizing AI Prompts

Edit `utils/ai_image_generator.py` to modify prompts:

```python
ENHANCED_CALENDAR_THEMES = [
    {
        "month": 1,
        "name": "January",
        "theme": "Firefighter",
        "ai_prompt": "Your custom prompt here..."
    },
    # ... more themes
]
```

## Troubleshooting

### AI Not Working
```bash
# Check token is set
cat .env | grep REPLICATE

# Test connection
python -c "import replicate; print('Replicate OK')"
```

### Slow Generation
- AI generation takes 10-15 seconds per image
- This is normal for Stable Diffusion
- Total: 3-4 minutes for 12 images
- Consider showing progress to users

### Rate Limiting
- Replicate has rate limits
- System waits 2 seconds between generations
- If rate limited, will fall back to placeholders

## Deployment with AI

### Railway / Render

Add environment variable:
```
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Cost Management

For production:
- Cache AI-generated images
- Offer AI generation as premium feature
- Use cheaper models for lower quality

## Alternative: Local Stable Diffusion

For unlimited free generation (requires GPU):

1. Install local Stable Diffusion
2. Run API server locally
3. Update `ai_image_generator.py` to use local endpoint
4. No per-image costs!

## Next Steps

1. ✅ Get Replicate API token
2. ✅ Add to `.env` file
3. ✅ Restart server
4. ✅ Test calendar generation
5. ✅ See AI-generated muscular/hunk themed images!

---

**With AI enabled, each calendar is unique and professionally generated!**
