"""
Google Gemini AI Service (Nano Banana)
Handles image generation using Google's Gemini 2.5 Flash Image API
"""
import os
import io
import time
import google.generativeai as genai
from PIL import Image

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_calendar_image(prompt, reference_images=None):
    """
    Generate a calendar image using Google Gemini 2.5 Flash Image

    Args:
        prompt (str): Text description of desired image
        reference_images (list): List of PIL Image objects for face consistency

    Returns:
        bytes: Generated image data as bytes
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Build the content array
        content_parts = []

        # Add reference images if provided
        if reference_images:
            content_parts.append("Using these reference images of the person:")
            for img in reference_images[:5]:  # Limit to 5 images
                content_parts.append(img)

        # Enhanced prompt for better results
        enhanced_prompt = f"""Create a photorealistic, high-quality image:

{prompt}

Requirements:
- High resolution and detailed
- Professional photography quality
- Suitable for calendar printing
- Center-focused composition
- Vibrant colors
- If person reference images provided, maintain their facial features and likeness
"""

        content_parts.append(enhanced_prompt)

        # Generate the image
        response = model.generate_content(
            content_parts,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 8192,
            }
        )

        # Extract image from response
        if response.candidates and len(response.candidates) > 0:
            parts = response.candidates[0].content.parts
            for part in parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Return the image data as bytes
                    return part.inline_data.data

        raise Exception("No image generated in response")

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        raise

def generate_calendar_images_batch(project_id, prompts, reference_image_data_list):
    """
    Generate all 12 calendar images for a project

    Args:
        project_id (int): Calendar project ID
        prompts (dict): Dictionary mapping month number (1-12) to prompt text
        reference_image_data_list (list): List of image data bytes for reference

    Returns:
        dict: Dictionary mapping month number to generated image data
    """
    from app import db
    from app.models import CalendarMonth, CalendarProject

    # Load reference images
    reference_images = []
    for img_data in reference_image_data_list:
        try:
            img = Image.open(io.BytesIO(img_data))
            reference_images.append(img)
        except Exception as e:
            print(f"Error loading reference image: {e}")

    results = {}

    # Update project status
    project = CalendarProject.query.get(project_id)
    if project:
        project.status = 'processing'
        db.session.commit()

    # Generate each month
    for month_num in range(1, 13):
        try:
            print(f"Generating month {month_num}/12...")

            # Get or create month record
            month = CalendarMonth.query.filter_by(
                project_id=project_id,
                month_number=month_num
            ).first()

            if month:
                month.generation_status = 'processing'
                db.session.commit()

                # Generate image
                prompt = prompts.get(month_num, f"Month {month_num}")
                image_data = generate_calendar_image(prompt, reference_images)

                # Save to database
                month.master_image_data = image_data
                month.generation_status = 'completed'
                month.generated_at = db.func.now()
                db.session.commit()

                results[month_num] = image_data
                print(f"Month {month_num} completed!")

                # Rate limiting - wait 2 seconds between requests
                if month_num < 12:
                    time.sleep(2)

        except Exception as e:
            print(f"Error generating month {month_num}: {e}")
            if month:
                month.generation_status = 'failed'
                month.error_message = str(e)
                db.session.commit()

    # Update project status
    if project:
        all_completed = all(
            m.generation_status == 'completed'
            for m in project.calendar_months
        )
        if all_completed:
            project.status = 'preview'
        db.session.commit()

    return results

def test_api_connection():
    """Test if Gemini API is configured and working"""
    try:
        if not GOOGLE_API_KEY:
            return False, "Google API key not configured"

        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("test")
        return True, "API connection successful"
    except Exception as e:
        return False, f"API connection failed: {str(e)}"
