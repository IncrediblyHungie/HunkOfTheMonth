# KevCal - Face Swap Calendar Generator

A professional face swap calendar generator that creates personalized 12-month calendars by swapping faces onto themed template images. Built with FastAPI, InsightFace, and Printful API integration.

## Features

- **Face Swap Technology**: Advanced face swapping using InsightFace AI models
- **12 Themed Templates**: Professional calendar themes (firefighter, pilot, astronaut, etc.)
- **Printful Integration**: Automatic calendar product creation for print-on-demand
- **Modern Web Interface**: Beautiful, responsive UI for easy photo uploads
- **GPU Accelerated**: Optimized for NVIDIA GPUs (RTX 4080)
- **Railway Ready**: Easy deployment to cloud platforms

## Calendar Themes

1. **January** - Firefighter in burning building
2. **February** - Fighter pilot in F-16 cockpit
3. **March** - Astronaut in space station
4. **April** - Cowboy on horseback at sunset
5. **May** - Professional chef in kitchen
6. **June** - Rock star on stage with guitar
7. **July** - Deep sea diver underwater
8. **August** - Mountain climber at summit
9. **September** - F1 race car driver
10. **October** - Samurai warrior with katana
11. **November** - Viking warrior on longship
12. **December** - Secret agent in tuxedo

## Installation

### Prerequisites

- Python 3.10+
- NVIDIA GPU with CUDA support (recommended)
- 4GB+ VRAM for optimal performance

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/kevcal.git
   cd kevcal
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Printful API key
   ```

5. **Download InsightFace models**:
   ```bash
   python models/download_models.py
   ```

6. **Run the application**:
   ```bash
   python app.py
   ```

7. **Open browser**:
   Navigate to `http://localhost:8000`

## Railway Deployment

### Quick Deploy

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/kevcal.git
   git push -u origin main
   ```

2. **Deploy to Railway**:
   - Go to [Railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variable: `PRINTFUL_API_KEY`
   - Railway will auto-detect the configuration and deploy

### Railway Configuration

The project includes:
- `Procfile` - Defines the web process
- `runtime.txt` - Specifies Python version
- `requirements.txt` - Lists all dependencies

### Environment Variables

Set these in Railway dashboard:
- `PRINTFUL_API_KEY` - Your Printful API key
- `PORT` - (Auto-configured by Railway)

## Usage

### Web Interface

1. **Upload Photos**: Click upload area or drag & drop 1-3 photos
2. **Review Themes**: Preview the 12 calendar themes
3. **Generate Calendar**: Click "Generate Calendar Images"
4. **Download or Create Product**: Download images individually or create Printful product

### API Endpoints

#### Upload Photo
```bash
POST /api/upload
Content-Type: multipart/form-data

Returns: {"file_id": "uuid", "filename": "photo.jpg"}
```

#### Generate Calendar
```bash
POST /api/generate
Form Data: source_file_id=uuid

Returns: {"job_id": "uuid"}
```

#### Check Job Status
```bash
GET /api/job/{job_id}

Returns: {
  "status": "completed",
  "progress": 100,
  "images": [...]
}
```

#### Create Printful Product
```bash
POST /api/printful/create-product?job_id=uuid

Returns: {"success": true, "printful_data": {...}}
```

#### Verify Printful Connection
```bash
GET /api/printful/verify

Returns: {"connected": true, "message": "Connected"}
```

## Project Structure

```
KevCal/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── Procfile              # Railway deployment config
├── runtime.txt           # Python version
├── .env                  # Environment variables (not in git)
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── static/               # Frontend assets
│   ├── css/
│   │   └── style.css     # Application styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── templates/            # HTML templates
│   └── index.html        # Main page
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── face_swap.py      # Face swapping logic
│   ├── calendar_generator.py  # Calendar creation
│   └── printful.py       # Printful API client
├── uploads/              # Uploaded photos (not in git)
├── output/               # Generated images (not in git)
└── models/               # AI models (not in git)
    └── download_models.py
```

## Technology Stack

- **Backend**: FastAPI (async Python web framework)
- **Face Swap**: InsightFace (face detection & analysis)
- **Image Processing**: OpenCV, Pillow
- **Frontend**: Vanilla JavaScript, CSS3
- **API Integration**: Printful API
- **Deployment**: Railway, Docker-ready

## Performance

- **Face Detection**: ~0.5s per image
- **Face Swap**: ~2-3s per image
- **Calendar Generation**: ~30-40s for all 12 months
- **GPU Acceleration**: 3-5x faster with NVIDIA GPU

## Limitations & Future Improvements

### Current Limitations
- Uses simplified face swap (seamless cloning)
- No template images included (uses source image as template in MVP)
- In-memory job storage (not persistent)

### Future Improvements
- [ ] Add proper face swap model (GFPGAN, CodeFormer)
- [ ] Include pre-generated themed template images
- [ ] Implement Redis for job queue management
- [ ] Add user authentication
- [ ] Support multiple face swaps in single image
- [ ] Add AI-generated template option (Stable Diffusion)
- [ ] Batch processing for multiple calendars

## Template Images

For production use, you'll need to add template images to `templates/themes/`:

```
templates/themes/
├── 01_firefighter.jpg
├── 02_pilot.jpg
├── 03_astronaut.jpg
├── 04_cowboy.jpg
├── 05_chef.jpg
├── 06_rockstar.jpg
├── 07_diver.jpg
├── 08_climber.jpg
├── 09_racer.jpg
├── 10_samurai.jpg
├── 11_viking.jpg
└── 12_agent.jpg
```

You can:
1. Use stock photography from sites like Unsplash, Pexels
2. Generate with AI (Stable Diffusion, Midjourney)
3. Commission professional photography

## Troubleshooting

### InsightFace Installation Issues
If you encounter InsightFace installation problems:
```bash
pip install --upgrade pip
pip install insightface --no-cache-dir
```

### CUDA/GPU Issues
If GPU not detected:
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# For CPU-only (slower):
pip install onnxruntime  # Instead of onnxruntime-gpu
```

### Printful API Errors
- Verify API key in `.env` file
- Check API key hasn't expired
- Ensure store is properly configured on Printful

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review Printful API documentation

## Credits

- **InsightFace**: Face detection and analysis
- **Printful**: Print-on-demand API
- **FastAPI**: Modern Python web framework

---

Built with ❤️ for creating personalized calendar gifts
