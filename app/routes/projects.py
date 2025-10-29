"""
Project routes - Upload, prompts, preview, checkout
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from app import db
from app.models import CalendarProject, UploadedImage, CalendarMonth, Order
from app.routes.main import get_current_project
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

                    # Save to database
                    uploaded_img = UploadedImage(
                        project_id=project.id,
                        filename=secure_filename(file.filename),
                        file_data=img_data,
                        thumbnail_data=thumb_data
                    )
                    db.session.add(uploaded_img)

            db.session.commit()
            flash(f'{len(files)} photos uploaded successfully!', 'success')

        # Check if enough photos
        photo_count = UploadedImage.query.filter_by(project_id=project.id).count()
        if photo_count >= 3:  # Minimum 3 photos
            return redirect(url_for('projects.prompts'))

    # Get uploaded images
    images = UploadedImage.query.filter_by(project_id=project.id).all()

    return render_template('upload.html', project=project, images=images)

@bp.route('/prompts', methods=['GET', 'POST'])
def prompts():
    """Enter prompts for 12 months"""
    project = get_current_project()
    if not project:
        return redirect(url_for('main.start'))

    # Check if user uploaded photos
    photo_count = UploadedImage.query.filter_by(project_id=project.id).count()
    if photo_count < 3:
        flash('Please upload at least 3 photos first!', 'warning')
        return redirect(url_for('projects.upload'))

    if request.method == 'POST':
        # Save prompts
        for month_num in range(1, 13):
            prompt_text = request.form.get(f'prompt_{month_num}', '').strip()

            if prompt_text:
                # Create or update month record
                month = CalendarMonth.query.filter_by(
                    project_id=project.id,
                    month_number=month_num
                ).first()

                if not month:
                    month = CalendarMonth(
                        project_id=project.id,
                        month_number=month_num,
                        prompt=prompt_text
                    )
                    db.session.add(month)
                else:
                    month.prompt = prompt_text

        project.status = 'prompts'
        db.session.commit()

        flash('Prompts saved! Ready to generate your calendar.', 'success')
        return redirect(url_for('projects.generate'))

    # Get existing prompts
    months = {}
    for month_num in range(1, 13):
        month = CalendarMonth.query.filter_by(
            project_id=project.id,
            month_number=month_num
        ).first()
        months[month_num] = month

    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    return render_template('prompts.html', project=project, months=months, month_names=month_names)

@bp.route('/generate')
def generate():
    """Start AI generation"""
    project = get_current_project()
    if not project:
        return redirect(url_for('main.start'))

    # Check if prompts are complete
    month_count = CalendarMonth.query.filter_by(project_id=project.id).count()
    if month_count < 12:
        flash('Please complete all 12 prompts!', 'warning')
        return redirect(url_for('projects.prompts'))

    # Start generation (synchronous for mock version)
    try:
        from app.services.gemini_service import generate_calendar_images_batch

        # Get prompts
        months = CalendarMonth.query.filter_by(project_id=project.id).order_by(CalendarMonth.month_number).all()
        prompts = {m.month_number: m.prompt for m in months}

        # Get reference images
        uploaded_images = UploadedImage.query.filter_by(project_id=project.id).all()
        reference_image_data = [img.file_data for img in uploaded_images]

        # Generate images (this will take 5-10 minutes)
        flash('Starting AI generation... This will take 5-10 minutes.', 'info')

        # For production, use Celery: generate_calendar_task.delay(...)
        # For mock, do it synchronously
        generate_calendar_images_batch(project.id, prompts, reference_image_data)

        return redirect(url_for('projects.preview'))

    except Exception as e:
        flash(f'Error starting generation: {str(e)}', 'danger')
        return redirect(url_for('projects.prompts'))

@bp.route('/preview')
def preview():
    """Preview generated calendar"""
    project = get_current_project()
    if not project:
        return redirect(url_for('main.start'))

    # Get all months
    months = CalendarMonth.query.filter_by(
        project_id=project.id
    ).order_by(CalendarMonth.month_number).all()

    # Check if generation is complete
    if not all(m.generation_status == 'completed' for m in months):
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
            # Create mock order
            order = Order(
                project_id=project.id,
                email=email,
                status='coming_soon'
            )
            db.session.add(order)
            project.status = 'checkout'
            db.session.commit()

            flash('Thanks for your interest! Payment integration coming soon.', 'info')
            return redirect(url_for('projects.success'))

    return render_template('checkout.html', project=project)

@bp.route('/success')
def success():
    """Success page"""
    project = get_current_project()
    return render_template('success.html', project=project)
