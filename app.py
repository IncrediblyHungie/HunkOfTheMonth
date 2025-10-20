"""
KevCal - Face Swap Calendar Generator
FastAPI application for creating personalized calendar products
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pathlib import Path
import shutil
import uuid
import os
from typing import List
from dotenv import load_dotenv

from utils.face_swap import FaceSwapper
from utils.calendar_generator import CalendarGenerator, CALENDAR_THEMES
from utils.printful import PrintfulAPI

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="KevCal - Face Swap Calendar Generator",
    description="Generate personalized calendar products using face swap technology",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize services
face_swapper = None  # Lazy load to avoid startup issues
printful_api = None

# Storage directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
TEMPLATE_DIR = Path("templates/themes")

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# In-memory job storage (use Redis/DB for production)
jobs = {}


def get_face_swapper():
    """Lazy load face swapper"""
    global face_swapper
    if face_swapper is None:
        face_swapper = FaceSwapper()
    return face_swapper


def get_printful_api():
    """Lazy load Printful API"""
    global printful_api
    if printful_api is None:
        printful_api = PrintfulAPI()
    return printful_api


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "themes": CALENDAR_THEMES
    })


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "KevCal"}


@app.post("/api/upload")
async def upload_photo(file: UploadFile = File(...)):
    """
    Upload a source photo for face swapping

    Returns:
        file_id: Unique identifier for uploaded file
        filename: Original filename
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate unique ID for this upload
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    save_path = UPLOAD_DIR / f"{file_id}{file_extension}"

    # Save uploaded file
    with save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "file_id": file_id,
        "filename": file.filename,
        "path": str(save_path)
    }


@app.post("/api/generate")
async def generate_calendar(
    background_tasks: BackgroundTasks,
    source_file_id: str
):
    """
    Generate calendar images with face swaps

    Args:
        source_file_id: ID of uploaded source photo

    Returns:
        job_id: Job identifier to check progress
    """
    # Find source file
    source_files = list(UPLOAD_DIR.glob(f"{source_file_id}.*"))
    if not source_files:
        raise HTTPException(status_code=404, detail="Source file not found")

    source_path = source_files[0]

    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "images": [],
        "error": None
    }

    # Start background task
    background_tasks.add_task(process_calendar_generation, job_id, source_path)

    return {"job_id": job_id}


async def process_calendar_generation(job_id: str, source_path: Path):
    """
    Background task to process calendar generation

    Args:
        job_id: Job identifier
        source_path: Path to source photo
    """
    try:
        jobs[job_id]["status"] = "processing"

        # Initialize face swapper
        swapper = get_face_swapper()
        calendar_gen = CalendarGenerator()

        # For MVP, we'll use placeholder template images
        # In production, you'd have actual themed template images
        output_images = []

        for i, theme in enumerate(CALENDAR_THEMES, 1):
            month = theme['month']

            # Update progress
            jobs[job_id]["progress"] = int((i / 12) * 100)

            # For MVP: Create a simple template or use source image
            # In production: Use actual themed template images
            template_path = source_path  # Placeholder

            # Generate output filename
            output_filename = f"{job_id}_month_{month:02d}_{theme['theme'].replace(' ', '_').lower()}.jpg"
            swap_output = OUTPUT_DIR / f"swap_{output_filename}"
            final_output = OUTPUT_DIR / output_filename

            try:
                # Perform face swap (in MVP, this will just be identity for testing)
                # In production with real templates, this swaps face onto template
                swapper.swap_face(source_path, template_path, str(swap_output))

                # Add calendar overlay
                calendar_gen.add_calendar_overlay(str(swap_output), str(final_output), month)

                output_images.append({
                    "month": month,
                    "theme": theme['theme'],
                    "url": f"/output/{output_filename}",
                    "path": str(final_output)
                })

                # Clean up intermediate file
                if swap_output.exists():
                    swap_output.unlink()

            except Exception as e:
                print(f"Error processing month {month}: {e}")
                continue

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["images"] = output_images

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        print(f"Calendar generation failed: {e}")


@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """
    Get status of a calendar generation job

    Args:
        job_id: Job identifier

    Returns:
        Job status and progress
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]


@app.post("/api/printful/create-product")
async def create_printful_product(job_id: str):
    """
    Create Printful calendar product from generated images

    Args:
        job_id: Job ID of completed calendar generation

    Returns:
        Printful product information
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    if len(job["images"]) != 12:
        raise HTTPException(status_code=400, detail="Need 12 images for calendar")

    try:
        api = get_printful_api()

        # Get image paths in month order
        image_paths = []
        for month in range(1, 13):
            month_image = next((img for img in job["images"] if img["month"] == month), None)
            if not month_image:
                raise HTTPException(status_code=400, detail=f"Missing image for month {month}")
            image_paths.append(month_image["path"])

        # Create calendar product
        result = api.create_calendar_product(image_paths)

        return {
            "success": True,
            "printful_data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Printful product: {e}")


@app.get("/api/printful/verify")
async def verify_printful():
    """
    Verify Printful API connection

    Returns:
        Connection status
    """
    try:
        api = get_printful_api()
        success, message = api.verify_connection()

        return {
            "connected": success,
            "message": message
        }
    except Exception as e:
        return {
            "connected": False,
            "message": str(e)
        }


@app.get("/api/themes")
async def get_themes():
    """
    Get list of calendar themes

    Returns:
        List of all 12 calendar themes
    """
    return {"themes": CALENDAR_THEMES}


@app.delete("/api/cleanup/{job_id}")
async def cleanup_job(job_id: str):
    """
    Clean up job files

    Args:
        job_id: Job identifier
    """
    if job_id in jobs:
        # Delete generated images
        if jobs[job_id].get("images"):
            for image in jobs[job_id]["images"]:
                try:
                    Path(image["path"]).unlink()
                except:
                    pass

        # Remove job from memory
        del jobs[job_id]

    return {"success": True}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(app, host=host, port=port)
