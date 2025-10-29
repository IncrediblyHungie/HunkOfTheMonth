"""
Main routes - Landing page, about, etc.
"""
from flask import Blueprint, render_template, session, redirect, url_for
from app import session_storage
from datetime import datetime
import secrets

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@bp.route('/start')
def start():
    """Start creating a calendar - initialize session storage"""
    # Generate session token
    session_token = secrets.token_urlsafe(32)
    session['guest_token'] = session_token
    session['created_at'] = datetime.utcnow().isoformat()

    # Initialize session storage (replaces database)
    session_storage.init_session()
    session_storage.update_project_status('uploading')

    return redirect(url_for('projects.upload'))

def get_current_project():
    """Get the current user's project from session"""
    guest_token = session.get('guest_token')
    if not guest_token:
        return None

    # Return project from session storage
    return session_storage.get_current_project()
