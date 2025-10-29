"""
Celery background tasks for async AI generation
For the mock version, we'll keep this simple
"""
import os
from celery import Celery
from app.services.gemini_service import generate_calendar_images_batch

# Configure Celery
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('tasks', broker=redis_url, backend=redis_url)

@celery_app.task(bind=True)
def generate_calendar_task(self, project_id, prompts, reference_image_data_list):
    """
    Background task to generate all calendar images

    Args:
        project_id (int): Calendar project ID
        prompts (dict): Month number to prompt text mapping
        reference_image_data_list (list): Reference image bytes

    Returns:
        dict: Results of generation
    """
    try:
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': 12})

        results = generate_calendar_images_batch(
            project_id,
            prompts,
            reference_image_data_list
        )

        return {
            'status': 'completed',
            'generated_count': len(results)
        }

    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
