"""
Server-side in-memory storage system (temporary replacement for database)
Stores data in server memory, NOT in cookies (avoids size limits)
"""
from flask import session
from datetime import datetime
import secrets

# SERVER-SIDE storage (not in cookies!)
# Key: session_id, Value: project data
_storage = {}

def _get_session_id():
    """Get or create session ID (only ID stored in cookie, not data)"""
    if 'storage_id' not in session:
        session['storage_id'] = secrets.token_urlsafe(32)
    return session['storage_id']

def _get_storage():
    """Get storage for current session"""
    session_id = _get_session_id()
    if session_id not in _storage:
        _storage[session_id] = {
            'project': {
                'id': 1,
                'status': 'new',
                'created_at': datetime.utcnow().isoformat()
            },
            'images': [],
            'months': []
        }
    return _storage[session_id]

def init_session():
    """Initialize session storage if needed"""
    _get_storage()  # Creates storage if doesn't exist

def get_current_project():
    """Get or create current project"""
    storage = _get_storage()
    return storage['project']

def get_uploaded_images():
    """Get list of uploaded images"""
    storage = _get_storage()
    return storage['images']

def add_uploaded_image(filename, file_data, thumbnail_data):
    """Add an uploaded image"""
    storage = _get_storage()

    # Store binary data directly in server memory (no base64 needed!)
    image_id = len(storage['images']) + 1
    storage['images'].append({
        'id': image_id,
        'filename': filename,
        'file_data': file_data,  # Raw binary data
        'thumbnail_data': thumbnail_data,  # Raw binary data
        'uploaded_at': datetime.utcnow().isoformat()
    })
    return image_id

def get_image_by_id(image_id):
    """Get image by ID"""
    storage = _get_storage()
    for img in storage['images']:
        if img['id'] == image_id:
            return img
    return None

def delete_image(image_id):
    """Delete an image"""
    storage = _get_storage()
    storage['images'] = [img for img in storage['images'] if img['id'] != image_id]

def get_all_months():
    """Get all calendar months"""
    storage = _get_storage()
    return storage['months']

def create_months_with_themes(themes):
    """Create 12 months with themes"""
    storage = _get_storage()
    storage['months'] = []

    for month_num in range(1, 13):
        theme = themes[month_num]
        storage['months'].append({
            'id': month_num,
            'month_number': month_num,
            'prompt': theme['title'],
            'generation_status': 'pending',
            'master_image_data': None,  # Raw binary data
            'error_message': None,
            'generated_at': None
        })

def get_month_by_number(month_num):
    """Get month by number"""
    storage = _get_storage()
    for month in storage['months']:
        if month['month_number'] == month_num:
            return month
    return None

def update_month_status(month_num, status, image_data=None, error=None):
    """Update month generation status"""
    storage = _get_storage()

    for month in storage['months']:
        if month['month_number'] == month_num:
            month['generation_status'] = status

            if image_data:
                # Store as raw binary (no base64 needed in server memory!)
                month['master_image_data'] = image_data
                month['generated_at'] = datetime.utcnow().isoformat()

            if error:
                month['error_message'] = str(error)

            return month

    return None

def get_month_image_data(month_num):
    """Get binary image data for a month"""
    month = get_month_by_number(month_num)
    if month and month.get('master_image_data'):
        return month['master_image_data']
    return None

def update_project_status(status):
    """Update project status"""
    storage = _get_storage()
    storage['project']['status'] = status

def get_completion_count():
    """Get number of completed months"""
    storage = _get_storage()
    return sum(1 for m in storage['months'] if m['generation_status'] == 'completed')

def clear_session():
    """Clear all session data (for testing)"""
    session_id = _get_session_id()
    if session_id in _storage:
        del _storage[session_id]
    session.clear()
