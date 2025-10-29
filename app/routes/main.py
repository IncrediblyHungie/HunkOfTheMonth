"""
Main routes - Landing page, about, etc.
"""
from flask import Blueprint, render_template, session, redirect, url_for
from app.models import CalendarProject, GuestSession
from datetime import datetime, timedelta
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
    """Start creating a calendar - create guest session"""
    # Generate session token
    session_token = secrets.token_urlsafe(32)
    session['guest_token'] = session_token
    session['created_at'] = datetime.utcnow().isoformat()

    # Create guest session in database
    from app import db
    guest_session = GuestSession(
        session_token=session_token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.session.add(guest_session)

    # Create new calendar project
    project = CalendarProject(
        session_token=session_token,
        status='uploading'
    )
    db.session.add(project)
    db.session.commit()

    # Store project ID in session
    session['project_id'] = project.id

    return redirect(url_for('projects.upload'))

def get_current_project():
    """Get the current user's project"""
    project_id = session.get('project_id')
    if not project_id:
        return None

    guest_token = session.get('guest_token')
    if not guest_token:
        return None

    project = CalendarProject.query.filter_by(
        id=project_id,
        session_token=guest_token
    ).first()

    return project
