"""
Google Gemini AI Service (Nano Banana)
Handles image generation using Google's Gemini 2.5 Flash Image API
with face-swapping and character consistency
"""
import os
import io
import time
from google import genai
from google.genai import types
from PIL import Image

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyAXdQlDioxbG3wr9jHEaFJiIt6AB5Bdals')

def generate_calendar_image(prompt, reference_image_data_list=None):
    """
    Generate a calendar image using Google Gemini 2.5 Flash Image
    with face-swapping from reference images

    Args:
        prompt (str): Text description of desired hunky scene
        reference_image_data_list (list): List of image data bytes for face reference

    Returns:
        bytes: Generated image data as PNG bytes
    """
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)

        # Build content array with reference images first
        content = []

        # Add reference images if provided (for face consistency)
        if reference_image_data_list:
            # Add instruction about reference images
            ref_instruction = """
CRITICAL: Use the person's face from the reference images below.
Maintain their exact facial features, skin tone, eye color, facial structure, and identity.
Put THIS PERSON'S FACE on the hunky body in the scene.
"""
            content.append(ref_instruction)

            # Add up to 3 reference images for best face consistency
            for img_data in reference_image_data_list[:3]:
                try:
                    # Load image and add to content
                    img = Image.open(io.BytesIO(img_data))
                    # Resize if too large (max 4MP for Gemini)
                    max_pixels = 4_000_000
                    if img.width * img.height > max_pixels:
                        ratio = (max_pixels / (img.width * img.height)) ** 0.5
                        new_size = (int(img.width * ratio), int(img.height * ratio))
                        img = img.resize(new_size, Image.LANCZOS)
                    content.append(img)
                except Exception as e:
                    print(f"Error loading reference image: {e}")

        # Enhanced prompt with face-swapping instructions
        enhanced_prompt = f"""
{prompt}

CRITICAL REQUIREMENTS:
- Take the FACE from the reference images above and put it on the hunky body
- Maintain the person's facial identity, features, and likeness EXACTLY
- Keep their eye color, skin tone, facial structure identical to reference
- Professional photography quality, suitable for calendar printing
- Photorealistic, high resolution, vibrant colors
- Center the subject prominently in the frame
- Dramatic lighting that highlights muscular physique
- Make the scene ridiculously sexy and over-the-top hilarious

Style: Professional fitness photography meets comedy photoshoot
"""

        content.append(enhanced_prompt)

        # Generate the image using Gemini 2.5 Flash Image (Nano Banana)
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=content,
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                temperature=0.8,  # Higher for creative hunky scenes
            )
        )

        # Extract PNG image data from response
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        return part.inline_data.data

        raise Exception("No image generated in response")

    except Exception as e:
        print(f"Error generating image with Gemini: {str(e)}")
        raise


def generate_calendar_images_batch(project_id, prompts, reference_image_data_list):
    """
    Generate all 12 calendar images for a project using face-swapping

    Args:
        project_id (int): Calendar project ID
        prompts (dict): Dictionary mapping month number (1-12) to enhanced prompt text
        reference_image_data_list (list): List of image data bytes for face reference

    Returns:
        dict: Dictionary mapping month number to generated image data
    """
    from app import db
    from app.models import CalendarMonth, CalendarProject

    results = {}

    # Update project status
    project = CalendarProject.query.get(project_id)
    if project:
        project.status = 'processing'
        db.session.commit()

    print(f"Starting batch generation for project {project_id}")
    print(f"Using {len(reference_image_data_list)} reference images for face-swapping")

    # Generate each month
    for month_num in range(1, 13):
        try:
            print(f"\n{'='*60}")
            print(f"Generating Month {month_num}/12...")
            print(f"{'='*60}")

            # Get month record
            month = CalendarMonth.query.filter_by(
                project_id=project_id,
                month_number=month_num
            ).first()

            if not month:
                print(f"Warning: Month {month_num} record not found, skipping...")
                continue

            # Update status to processing
            month.generation_status = 'processing'
            db.session.commit()

            # Get the enhanced prompt for this month
            prompt = prompts.get(month_num, f"Month {month_num}")
            print(f"Prompt: {prompt[:100]}...")

            # Generate image with face-swapping
            image_data = generate_calendar_image(prompt, reference_image_data_list)

            # Convert PNG to JPEG for smaller file size
            img = Image.open(io.BytesIO(image_data))
            img_io = io.BytesIO()
            img.convert('RGB').save(img_io, format='JPEG', quality=95)
            jpeg_data = img_io.getvalue()

            # Save to database
            month.master_image_data = jpeg_data
            month.generation_status = 'completed'
            from datetime import datetime
            month.generated_at = datetime.utcnow()
            db.session.commit()

            results[month_num] = jpeg_data
            print(f"✅ Month {month_num} completed! Image size: {len(jpeg_data)} bytes")

            # Rate limiting - wait 3 seconds between requests to avoid quota issues
            if month_num < 12:
                print(f"Waiting 3 seconds before next generation...")
                time.sleep(3)

        except Exception as e:
            print(f"❌ Error generating month {month_num}: {e}")
            if month:
                month.generation_status = 'failed'
                month.error_message = str(e)
                db.session.commit()

    # Update project status to preview if all completed
    if project:
        completed_count = sum(
            1 for m in project.calendar_months
            if m.generation_status == 'completed'
        )
        print(f"\nGeneration complete: {completed_count}/12 months succeeded")

        if completed_count == 12:
            project.status = 'preview'
            print("✅ All months completed! Project ready for preview.")
        else:
            project.status = 'partial'
            print(f"⚠️  Partial completion: {completed_count}/12 months")

        db.session.commit()

    return results


def test_api_connection():
    """Test if Gemini API is configured and working"""
    try:
        if not GOOGLE_API_KEY:
            return False, "Google API key not configured"

        client = genai.Client(api_key=GOOGLE_API_KEY)

        # Simple test generation
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=['A simple red circle on white background'],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
            )
        )

        if response.candidates:
            return True, "API connection successful"
        else:
            return False, "API returned no candidates"

    except Exception as e:
        return False, f"API connection failed: {str(e)}"
