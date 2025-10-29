"""
Session-based storage system (temporary replacement for database)
Stores everything in Flask session for testing AI image generation
"""
from flask import session
import base64
from datetime import datetime

def init_session():
    """Initialize session storage if needed"""
    if 'project' not in session:
        session['project'] = {
            'id': 1,
            'status': 'new',
            'created_at': datetime.utcnow().isoformat()
        }
    if 'images' not in session:
        session['images'] = []
    if 'months' not in session:
        session['months'] = []

def get_current_project():
    """Get or create current project"""
    init_session()
    return session['project']

def get_uploaded_images():
    """Get list of uploaded images"""
    init_session()
    return session['images']

def add_uploaded_image(filename, file_data, thumbnail_data):
    """Add an uploaded image"""
    init_session()

    # Convert binary data to base64 for session storage
    image_id = len(session['images']) + 1
    session['images'].append({
        'id': image_id,
        'filename': filename,
        'file_data': base64.b64encode(file_data).decode('utf-8'),
        'thumbnail_data': base64.b64encode(thumbnail_data).decode('utf-8'),
        'uploaded_at': datetime.utcnow().isoformat()
    })
    session.modified = True
    return image_id

def get_image_by_id(image_id):
    """Get image by ID"""
    init_session()
    for img in session['images']:
        if img['id'] == image_id:
            # Decode base64 back to binary
            return {
                'id': img['id'],
                'filename': img['filename'],
                'file_data': base64.b64decode(img['file_data']),
                'thumbnail_data': base64.b64decode(img['thumbnail_data'])
            }
    return None

def delete_image(image_id):
    """Delete an image"""
    init_session()
    session['images'] = [img for img in session['images'] if img['id'] != image_id]
    session.modified = True

def get_all_months():
    """Get all calendar months"""
    init_session()
    return session['months']

def create_months_with_themes(themes):
    """Create 12 months with themes"""
    init_session()
    session['months'] = []

    for month_num in range(1, 13):
        theme = themes[month_num]
        session['months'].append({
            'id': month_num,
            'month_number': month_num,
            'prompt': theme['title'],
            'generation_status': 'pending',
            'master_image_data': None,
            'error_message': None,
            'generated_at': None
        })

    session.modified = True

def get_month_by_number(month_num):
    """Get month by number"""
    init_session()
    for month in session['months']:
        if month['month_number'] == month_num:
            return month
    return None

def update_month_status(month_num, status, image_data=None, error=None):
    """Update month generation status"""
    init_session()

    for month in session['months']:
        if month['month_number'] == month_num:
            month['generation_status'] = status

            if image_data:
                # Store as base64
                month['master_image_data'] = base64.b64encode(image_data).decode('utf-8')
                month['generated_at'] = datetime.utcnow().isoformat()

            if error:
                month['error_message'] = str(error)

            session.modified = True
            return month

    return None

def get_month_image_data(month_num):
    """Get binary image data for a month"""
    month = get_month_by_number(month_num)
    if month and month.get('master_image_data'):
        # Decode base64 to binary
        return base64.b64decode(month['master_image_data'])
    return None

def update_project_status(status):
    """Update project status"""
    init_session()
    session['project']['status'] = status
    session.modified = True

def get_completion_count():
    """Get number of completed months"""
    init_session()
    return sum(1 for m in session['months'] if m['generation_status'] == 'completed')

def clear_session():
    """Clear all session data (for testing)"""
    session.clear()
