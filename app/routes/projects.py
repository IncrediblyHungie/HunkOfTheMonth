"""
Project routes - Upload, prompts, preview, checkout
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from app import session_storage
from app.routes.main import get_current_project
from app.services.monthly_themes import get_all_themes, get_theme, get_enhanced_prompt
from PIL import Image
import io

bp = Blueprint('projects', __name__, url_prefix='/project')

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload selfies page"""
    project = get_current_project()
    if not project:
        return redirect(url_for('main.start'))

    if request.method == 'POST':
        # Handle file uploads
        if 'photos' in request.files:
            files = request.files.getlist('photos')

            for file in files:
                if file and file.filename:
                    # Read image data
                    img_data = file.read()

                    # Create thumbnail
                    img = Image.open(io.BytesIO(img_data))
                    img.thumbnail((200, 200))
                    thumb_io = io.BytesIO()
                    img.save(thumb_io, format='JPEG')
                    thumb_data = thumb_io.getvalue()

                    # Save to session storage
                    session_storage.add_uploaded_image(
                        secure_filename(file.filename),
                        img_data,
                        thumb_data
                    )

            flash(f'{len(files)} photos uploaded successfully!', 'success')

        # Check if enough photos
        images = session_storage.get_uploaded_images()
        if len(images) >= 3:  # Minimum 3 photos
            return redirect(url_for('projects.themes'))

    # Get uploaded images
    images = session_storage.get_uploaded_images()

    return render_template('upload.html', project=project, images=images)

@bp.route('/themes', methods=['GET', 'POST'])
def themes():
    """Review pre-defined monthly hunk themes"""
    project = get_current_project()
    if not project:
        return redirect(url_for('main.start'))

    # Check if user uploaded photos
    images = session_storage.get_uploaded_images()
    if len(images) < 3:
        flash('Please upload at least 3 photos first!', 'warning')
        return redirect(url_for('projects.upload'))

    if request.method == 'POST':
        try:
            # Auto-create months with pre-defined themes
            all_themes = get_all_themes()
            session_storage.create_months_with_themes(all_themes)

            session_storage.update_project_status('prompts')

            flash('Themes confirmed! Ready to make you a hunk!', 'success')
            return redirect(url_for('projects.generate'))

        except Exception as e:
            flash(f'Error setting up themes: {str(e)}', 'danger')
            return redirect(url_for('projects.themes'))

    # Get all pre-defined themes
    all_themes = get_all_themes()

    return render_template('themes.html', project=project, themes=all_themes)

@bp.route('/generate')
def generate():
    """Start AI generation - redirect immediately to avoid timeout"""
    project = get_current_project()
    if not project:
        return redirect(url_for('main.start'))

    # Check if themes are confirmed
    months = session_storage.get_all_months()
    if len(months) < 12:
        flash('Please review the monthly themes first!', 'warning')
        return redirect(url_for('projects.themes'))

    # Check if we have reference images
    images = session_storage.get_uploaded_images()
    if len(images) < 3:
        flash('Please upload at least 3 photos first!', 'warning')
        return redirect(url_for('projects.upload'))

    try:
        # Mark project as processing
        session_storage.update_project_status('processing')

        flash('Starting AI generation with face-swapping... This will take 5-10 minutes.', 'info')

        # Redirect immediately to preview page (AJAX will handle actual generation)
        return redirect(url_for('projects.preview'))

    except Exception as e:
        flash(f'Error starting generation: {str(e)}', 'danger')
        return redirect(url_for('projects.themes'))

@bp.route('/preview')
def preview():
    """Preview generated calendar"""
    project = get_current_project()
    if not project:
        return redirect(url_for('main.start'))

    # Get all months from session storage
    months = session_storage.get_all_months()

    # Check if generation is complete
    if not all(m['generation_status'] == 'completed' for m in months):
        flash('Calendar generation in progress...', 'info')
        return render_template('generating.html', project=project, months=months)

    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    return render_template('preview.html', project=project, months=months, month_names=month_names)

@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page (mock)"""
    project = get_current_project()
    if not project:
        return redirect(url_for('main.start'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if email:
            # Store email in session (mock order)
            session['order_email'] = email
            session_storage.update_project_status('checkout')

            flash('Thanks for your interest! Payment integration coming soon.', 'info')
            return redirect(url_for('projects.success'))

    return render_template('checkout.html', project=project)

@bp.route('/success')
def success():
    """Success page"""
    project = get_current_project()
    return render_template('success.html', project=project)
