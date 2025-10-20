# KevCal Quick Start Guide

## What We Built

A complete face swap calendar generator that:
1. **Uploads photos** - Takes 1-3 photos of a person
2. **Extracts faces** - Uses OpenCV to detect and extract faces
3. **Creates calendars** - Overlays faces onto 12 themed templates
4. **Generates mockups** - Uploads to Printful and creates professional calendar mockups
5. **Ready to order** - Calendar can be ordered through Printful

## Currently Running

The application is **LIVE** at: `http://localhost:8000`

## How to Use

### Step 1: Upload Photos
1. Open http://localhost:8000 in your browser
2. Click the upload area or drag & drop 1-3 photos
3. Use clear, front-facing photos for best results

### Step 2: Generate Calendar
1. Click "Generate Calendar Images"
2. Watch the progress bar (takes ~10-30 seconds for 12 months)
3. View your 12 calendar images with face overlays

### Step 3: Create Printful Product (Optional)
1. Click "Create Printful Calendar Product"
2. System uploads all 12 images to Printful
3. Waits for professional mockup generation
4. Shows Printful mockup images you can view/download

## What's Included

### 12 Themed Templates
- January: Firefighter (Red/Orange)
- February: Fighter Pilot (Blue)
- March: Astronaut (Navy)
- April: Cowboy (Brown)
- May: Chef (White)
- June: Rock Star (Purple)
- July: Deep Sea Diver (Cyan)
- August: Mountain Climber (Gray)
- September: Race Car Driver (Red)
- October: Samurai (Dark Red)
- November: Viking (Indigo)
- December: Secret Agent (Black)

### Features
- ✅ Face detection and extraction using OpenCV
- ✅ Circular face overlay on themed backgrounds
- ✅ Calendar grid overlay with month/year
- ✅ Individual image downloads
- ✅ Printful API integration
- ✅ Professional mockup generation
- ✅ Background async processing
- ✅ Real-time progress updates

## Architecture

```
User uploads photos
    ↓
SimpleFaceOverlay extracts face
    ↓
For each of 12 months:
    - Load themed template
    - Overlay extracted face (circular mask)
    - Add calendar grid
    - Save final image
    ↓
Display all 12 calendars
    ↓
(Optional) Upload to Printful
    ↓
Generate professional mockup
    ↓
Show mockup images
```

## API Endpoints

### Core Endpoints
- `GET /` - Web interface
- `GET /health` - Health check
- `GET /api/themes` - List calendar themes
- `POST /api/upload` - Upload photo (multipart/form-data)
- `POST /api/generate` - Generate calendar (Form: source_file_id)
- `GET /api/job/{job_id}` - Check generation status

### Printful Endpoints
- `GET /api/printful/verify` - Verify API connection
- `POST /api/printful/create-product` - Create calendar mockup
- `GET /api/printful/mockup-status/{task_key}` - Check mockup status

## File Structure

```
/home/peteylinux/Projects/KevCal/
├── app.py                          # Main FastAPI application
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (API key)
├── Procfile                       # Railway deployment config
├── uploads/                       # User uploaded photos
├── output/                        # Generated calendar images
├── templates/
│   ├── index.html                # Web interface
│   └── themes/                   # 12 template images
│       ├── 01_firefighter.jpg
│       ├── 02_pilot.jpg
│       └── ... (10 more)
├── static/
│   ├── css/style.css            # UI styling
│   └── js/app.js                # Frontend logic
└── utils/
    ├── simple_face_overlay.py   # Face extraction & overlay
    ├── calendar_generator.py    # Calendar grid overlay
    └── printful.py              # Printful API client
```

## Testing the System

### Test 1: Basic Calendar Generation
```bash
# 1. Upload a photo through the UI
# 2. Click "Generate Calendar Images"
# 3. Wait for completion
# 4. Verify you see 12 calendar images
```

### Test 2: Printful Integration
```bash
# 1. Complete Test 1 first
# 2. Click "Create Printful Calendar Product"
# 3. Wait for upload (shows "Uploading to Printful...")
# 4. Wait for mockup (shows "Generating mockup...")
# 5. See professional Printful mockup at the top
```

### Test 3: API Testing
```bash
# Upload
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/photo.jpg"

# Check Printful
curl http://localhost:8000/api/printful/verify

# List themes
curl http://localhost:8000/api/themes
```

## Next Steps to Deploy

### 1. Push to GitHub
```bash
# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/kevcal.git
git push -u origin main
```

### 2. Deploy to Railway
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your kevcal repository
4. Add environment variable: `PRINTFUL_API_KEY`
5. Railway auto-deploys using Procfile

### 3. Get Public URL
Railway gives you a URL like: `https://kevcal-production.up.railway.app`

## Customization

### Change Template Images
Replace the placeholder templates in `templates/themes/` with:
- Stock photos from Unsplash/Pexels
- AI-generated images (Stable Diffusion, Midjourney)
- Professional photography

### Adjust Face Size/Position
In `app.py` line ~194:
```python
overlay.overlay_face_on_template(
    str(source_path),
    str(template_path),
    str(swap_output),
    position="center",    # Change to "top" or (x, y)
    size=(500, 500)       # Change face size
)
```

### Change Calendar Year
In `utils/calendar_generator.py` line ~141:
```python
def __init__(self, year=None):
    self.year = year or 2026  # Change default year
```

## Troubleshooting

### Face Not Detected
- Use clear, front-facing photos
- Ensure good lighting
- Face should be clearly visible
- If fails, system uses template without face overlay

### Printful API Errors
```bash
# Check API key
cat .env | grep PRINTFUL

# Test connection
curl http://localhost:8000/api/printful/verify
```

### Generation Fails
Check server logs in terminal for detailed error messages.

## Performance

- **Face Detection**: ~0.5-1s per image
- **Face Overlay**: ~0.2-0.5s per month
- **Calendar Grid**: ~0.1s per month
- **Total Generation**: ~10-30s for 12 months
- **Printful Upload**: ~20-40s for 12 images
- **Mockup Generation**: ~10-30s (Printful processing)

## Production Improvements

For production deployment:
1. Add user authentication
2. Use Redis for job queue
3. Store files in S3/CDN
4. Add payment processing
5. Better template images
6. Support multiple faces
7. Add image preprocessing

## Support

- **Local Testing**: Currently running at http://localhost:8000
- **GitHub Issues**: Create issues for bugs/features
- **Printful Docs**: https://developers.printful.com
- **FastAPI Docs**: http://localhost:8000/docs (auto-generated)

---

**MVP Status**: ✅ Complete and functional!

The system works end-to-end:
- Uploads photos ✓
- Generates calendars ✓
- Creates Printful mockups ✓
- Ready for deployment ✓
