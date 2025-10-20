# KevCal Deployment Guide

## Quick Start - Local Development

### 1. Start the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the app
python app.py
```

The application will be available at `http://localhost:8000`

### 2. Download InsightFace Models (First Run Only)

```bash
# In a separate terminal
source venv/bin/activate
python models/download_models.py
```

Models will be cached in `~/.insightface/models/` and automatically used.

## Railway Deployment

### Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)
- Printful API key

### Step 1: Push to GitHub

```bash
# Create a new repository on GitHub first
# Then push your code:

git remote add origin https://github.com/yourusername/kevcal.git
git push -u origin main
```

### Step 2: Deploy to Railway

1. **Go to Railway Dashboard**
   - Visit https://railway.app/dashboard
   - Click "New Project"

2. **Deploy from GitHub**
   - Select "Deploy from GitHub repo"
   - Choose your `kevcal` repository
   - Railway will auto-detect the configuration

3. **Set Environment Variables**
   - Go to project settings
   - Click "Variables" tab
   - Add the following:
     ```
     PRINTFUL_API_KEY=dn8ChPBdbe0QMZERdFeHltvlWNojVqomgmMELFtc
     ```

4. **Deploy**
   - Railway will automatically build and deploy
   - You'll get a public URL like `https://kevcal-production.up.railway.app`

### Step 3: Verify Deployment

1. Visit your Railway URL
2. Check the Printful connection status at the top
3. Upload a test photo
4. Generate a calendar

## Alternative: Render Deployment

### Prerequisites
- GitHub account
- Render account (sign up at https://render.com)
- Printful API key

### Deploy to Render

1. **Create New Web Service**
   - Go to https://dashboard.render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build**
   - **Name**: `kevcal`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**
   - Add `PRINTFUL_API_KEY` with your API key

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

## Docker Deployment (Optional)

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p uploads output models

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# Build image
docker build -t kevcal .

# Run container
docker run -p 8000:8000 \
  -e PRINTFUL_API_KEY=your_api_key \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/output:/app/output \
  kevcal
```

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `PRINTFUL_API_KEY` | Printful API key | Yes | - |
| `HOST` | Server host | No | `0.0.0.0` |
| `PORT` | Server port | No | `8000` |

## Troubleshooting

### InsightFace Model Download Fails

If models don't download automatically:

```bash
# Manual download
wget https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip
unzip buffalo_l.zip -d ~/.insightface/models/buffalo_l
```

### Memory Issues on Railway

If you encounter memory issues:

1. Railway free tier has memory limits
2. Consider upgrading to hobby plan
3. Or reduce model size in code

### Slow Face Swapping

- Face swapping is CPU-intensive
- On Railway/Render, expect 5-10 seconds per image
- For production, consider GPU-enabled hosting

### Printful API Errors

Check:
1. API key is correct in environment variables
2. Printful store is properly configured
3. API key hasn't expired

## Production Considerations

### For Production Deployment:

1. **Add Authentication**
   - Implement user login
   - Rate limiting
   - API key management

2. **Use Database**
   - Replace in-memory job storage with Redis/PostgreSQL
   - Store user data persistently

3. **Add Queue System**
   - Use Celery or RQ for background tasks
   - Handle concurrent requests better

4. **File Storage**
   - Use S3 or similar for uploads/outputs
   - Don't store files locally on serverless platforms

5. **Monitoring**
   - Add Sentry for error tracking
   - Use logging service (LogDNA, Papertrail)
   - Monitor API usage

6. **Template Images**
   - Add actual themed template images
   - Store in CDN for faster loading
   - Consider AI generation pipeline

## Next Steps

1. **Add Template Images**
   - Create/download 12 themed images
   - Place in `templates/themes/` directory
   - Update face swap logic to use them

2. **Improve Face Swap Quality**
   - Integrate better face swap model
   - Add preprocessing for better results
   - Support multiple faces in image

3. **Enhance UI**
   - Add progress indicators
   - Show preview of themes
   - Allow theme customization

4. **Integrate Payment**
   - Add Stripe/PayPal
   - Allow direct purchase of calendars
   - Handle order fulfillment

## Support

For issues:
- Check GitHub issues
- Review logs in Railway/Render dashboard
- Test locally first

---

Built with FastAPI, InsightFace, and Printful API
