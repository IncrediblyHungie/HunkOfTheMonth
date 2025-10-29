# Hunk of the Month - AI Calendar Platform

Transform yourself into 12 ridiculously sexy hunks with AI face-swapping! Using Google's Gemini 2.5 Flash (Nano Banana) API.

## Features

- **Your Face, Hunky Bodies**: AI puts YOUR face on 12 muscular, sexy characters
- **Hilarious Pre-Defined Themes**: From sexy firefighters to shirtless Santas
- **Guest Sessions**: No account required - 24-hour browser sessions
- **Free Preview**: See all 12 transformations before paying
- **Perfect for Gifts**: Bachelor parties, gag gifts, or just for laughs
- **Mock Payment**: Coming soon - Stripe integration planned

## Tech Stack

- **Backend**: Flask 3.0, Python 3.9+
- **Database**: PostgreSQL (Railway) / SQLite (local development)
- **AI**: Google Gemini 2.5 Flash Image API (Nano Banana)
- **Task Queue**: Celery + Redis (for background image generation)
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Deployment**: Railway

## Local Development

### Prerequisites

- Python 3.9+
- PostgreSQL (optional - SQLite used by default)
- Redis (for Celery tasks)
- Google API key for Gemini

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/IncrediblyHungie/HunkOfTheMonth.git
cd HunkOfTheMonth
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

5. **Initialize database**
```bash
flask db init
flask db migrate
flask db upgrade
```

6. **Run the application**
```bash
python run.py
```

Visit `http://localhost:5000` in your browser.

### Running with Celery (Optional)

For background image generation:

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A app.services.celery_tasks worker --loglevel=info

# Terminal 3: Start Flask
python run.py
```

## Deployment to Railway

### Prerequisites

- GitHub account
- Railway account (https://railway.app)
- Google API key

### Steps

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/HunkOfTheMonth.git
git push -u origin main
```

2. **Deploy on Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your HunkOfTheMonth repository
   - Railway will auto-detect the Flask app

3. **Add Services**
   - Add PostgreSQL database
   - Add Redis (for Celery)
   - Railway will automatically provide connection URLs

4. **Configure Environment Variables**
   In Railway dashboard, add:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   FLASK_ENV=production
   FLASK_SECRET_KEY=generate_random_secret_key
   ```

5. **Deploy**
   - Railway will automatically deploy on each push to main branch
   - Access your app at the provided Railway URL

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Auto (Railway) |
| `REDIS_URL` | Redis connection string | Auto (Railway) |
| `FLASK_SECRET_KEY` | Flask session secret | Yes |
| `FLASK_ENV` | development/production | Yes |

## Project Structure

```
HunkOfTheMonth/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # Database models
│   ├── routes/               # Route blueprints
│   │   ├── main.py          # Landing, about pages
│   │   ├── projects.py      # Upload, prompts, preview
│   │   └── api.py           # API endpoints
│   ├── services/            # External services
│   │   ├── gemini_service.py    # Google Gemini AI
│   │   └── celery_tasks.py      # Background tasks
│   ├── templates/           # HTML templates
│   └── static/              # CSS, JS, images
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway/Heroku config
├── railway.toml            # Railway specific config
└── README.md               # This file
```

## User Flow

1. **Landing Page** → Click "Make Me A Hunk!"
2. **Upload Photos** → Upload 3-10 selfies (for face recognition)
3. **Review Themes** → See 12 pre-defined ridiculous hunk scenarios
4. **AI Generation** → Wait 5-10 minutes for face-swapping magic
5. **Preview** → See YOUR FACE on 12 hunky bodies (FREE!)
6. **Checkout** → Coming soon (Stripe integration)

## Monthly Themes

Each month features you as a different sexy hunk in a hilarious scenario:

- **January**: New Year's Firefighter (putting out fireworks with champagne)
- **February**: Valentine's Cupid Cop (arresting with love arrows)
- **March**: St. Patrick's Day Brawler (wrestling leprechauns)
- **April**: Easter Bunny Lifeguard (rescuing chocolate eggs)
- **May**: Savage Gardener (battling giant flowers)
- **June**: Beach Whale Rescuer (saving inflatable whales)
- **July**: Patriotic BBQ Master (grilling in flag shorts)
- **August**: Sandcastle Construction Hunk (building epic sandcastles)
- **September**: Hunky Teacher (taming wild school supplies)
- **October**: Vampire Hunter (fighting inflatable decorations)
- **November**: Turkey Wrangling Pilgrim (chasing escaped turkeys)
- **December**: Sexy Santa (stuck in chimney, shirtless)

## API Costs

- **Google Gemini 2.5 Flash Image**: ~$0.02-0.04 per image
- **Cost per calendar preview**: ~$0.24-0.48 (12 images)
- **Note**: User sees preview FREE before any payment

## Future Features

- [ ] Stripe payment integration
- [ ] Printify order fulfillment
- [ ] Email notifications
- [ ] User accounts (optional)
- [ ] Calendar format options (portrait, landscape, square)
- [ ] Image regeneration for specific months
- [ ] Order history and tracking

## Development

### Database Migrations

```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### Testing

```bash
# Run tests (when added)
pytest

# Check code style
flake8 app/
```

## Contributing

This is a personal project, but suggestions and bug reports are welcome!

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- GitHub Issues: https://github.com/IncrediblyHungie/HunkOfTheMonth/issues
- Email: support@hunkofthemonth.com (placeholder)

## Credits

- **AI**: Google Gemini 2.5 Flash Image (Nano Banana)
- **Framework**: Flask
- **Deployment**: Railway
- **UI**: Bootstrap 5

---

Built with ❤️ and AI
