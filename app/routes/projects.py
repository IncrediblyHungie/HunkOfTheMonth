"""
Project routes - Upload, prompts, preview, checkout
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from app import session_storage
from app.routes.main import get_current_project
from app.services.monthly_themes import get_all_themes, get_theme, get_enhanced_prompt
from PIL import Image, ImageOps
import io

# Register HEIC support for iPhone photos
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # HEIC support not available

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

            processed_count = 0
            for file in files:
                if file and file.filename:
                    try:
                        # Read image data
                        original_data = file.read()

                        # Open image (supports JPEG, PNG, HEIC, etc.)
                        img = Image.open(io.BytesIO(original_data))

                        # Auto-rotate based on EXIF orientation (iPhone photos)
                        img = ImageOps.exif_transpose(img)

                        # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
                        if img.mode != 'RGB':
                            img = img.convert('RGB')

                        # Optimize: Resize if too large (face detection doesn't need 4000px)
                        # Target max dimension: 1920px (plenty for AI face analysis)
                        max_dimension = 1920
                        if max(img.size) > max_dimension:
                            # Resize maintaining aspect ratio
                            ratio = max_dimension / max(img.size)
                            new_size = tuple(int(dim * ratio) for dim in img.size)
                            img = img.resize(new_size, Image.Resampling.LANCZOS)

                        # Save optimized version (strips EXIF for privacy + size reduction)
                        optimized_io = io.BytesIO()
                        img.save(optimized_io, format='JPEG', quality=90, optimize=True)
                        img_data = optimized_io.getvalue()

                        # Create thumbnail for preview
                        img.thumbnail((200, 200))
                        thumb_io = io.BytesIO()
                        img.save(thumb_io, format='JPEG', quality=85)
                        thumb_data = thumb_io.getvalue()

                        # Save to session storage
                        session_storage.add_uploaded_image(
                            secure_filename(file.filename),
                            img_data,
                            thumb_data
                        )
                        processed_count += 1

                    except Exception as e:
                        flash(f'Error processing {file.filename}: {str(e)}', 'warning')
                        continue

            flash(f'{len(files)} photos uploaded successfully!', 'success')

        # Check if enough photos
        images = session_storage.get_uploaded_images()
        if len(images) >= 3:  # Minimum 3 photos
            return redirect(url_for('projects.customize'))

    # Get uploaded images
    images = session_storage.get_uploaded_images()

    return render_template('upload.html', project=project, images=images)

@bp.route('/customize', methods=['GET', 'POST'])
def customize():
    """Customize calendar preferences (gender, body type, style, tone)"""
    project = get_current_project()
    if not project:
        return redirect(url_for('main.start'))

    # Check if user uploaded photos
    images = session_storage.get_uploaded_images()
    if len(images) < 3:
        flash('Please upload at least 3 photos first!', 'warning')
        return redirect(url_for('projects.upload'))

    if request.method == 'POST':
        # Get customization preferences from form
        preferences = {
            'gender': request.form.get('gender', 'male'),
            'body_type': request.form.get('body_type', 'athletic'),
            'style': request.form.get('style', 'sexy'),
            'tone': request.form.get('tone', 'funny')
        }

        # Save preferences to session
        session_storage.set_preferences(preferences)

        flash('Preferences saved! Check out your custom themes.', 'success')
        return redirect(url_for('projects.themes'))

    # Get customization options
    from app.services.customization_options import get_customization_options, get_default_preferences
    options = get_customization_options()
    current_preferences = session_storage.get_preferences() or get_default_preferences()

    return render_template('customize.html', project=project, options=options, preferences=current_preferences)

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
