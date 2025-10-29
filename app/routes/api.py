"""
API routes for AJAX calls and image serving
"""
from flask import Blueprint, jsonify, send_file, Response
from app.models import UploadedImage, CalendarMonth
from app.routes.main import get_current_project
import io

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/image/thumbnail/<int:image_id>')
def get_thumbnail(image_id):
    """Serve thumbnail image"""
    project = get_current_project()
    if not project:
        return jsonify({'error': 'Unauthorized'}), 401

    image = UploadedImage.query.filter_by(
        id=image_id,
        project_id=project.id
    ).first()

    if not image or not image.thumbnail_data:
        return jsonify({'error': 'Image not found'}), 404

    return send_file(
        io.BytesIO(image.thumbnail_data),
        mimetype='image/jpeg'
    )

@bp.route('/image/month/<int:month_id>')
def get_month_image(month_id):
    """Serve generated month image"""
    project = get_current_project()
    if not project:
        return jsonify({'error': 'Unauthorized'}), 401

    month = CalendarMonth.query.filter_by(
        id=month_id,
        project_id=project.id
    ).first()

    if not month or not month.master_image_data:
        return jsonify({'error': 'Image not found'}), 404

    return send_file(
        io.BytesIO(month.master_image_data),
        mimetype='image/jpeg'
    )

@bp.route('/project/status')
def project_status():
    """Get current project status"""
    project = get_current_project()
    if not project:
        return jsonify({'error': 'No active project'}), 404

    # Get generation status
    months = CalendarMonth.query.filter_by(project_id=project.id).all()
    month_status = []

    for month in months:
        month_status.append({
            'month_number': month.month_number,
            'status': month.generation_status,
            'prompt': month.prompt
        })

    return jsonify({
        'project_id': project.id,
        'status': project.status,
        'months': month_status
    })

@bp.route('/delete/image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    """Delete an uploaded image"""
    project = get_current_project()
    if not project:
        return jsonify({'error': 'Unauthorized'}), 401

    image = UploadedImage.query.filter_by(
        id=image_id,
        project_id=project.id
    ).first()

    if not image:
        return jsonify({'error': 'Image not found'}), 404

    from app import db
    db.session.delete(image)
    db.session.commit()

    return jsonify({'success': True})

@bp.route('/generate/month/<int:month_num>', methods=['POST'])
def generate_month(month_num):
    """Generate a single month's image with AI face-swapping"""
    from app import db
    from app.services.gemini_service import generate_calendar_image
    from app.services.monthly_themes import get_enhanced_prompt
    from PIL import Image as PILImage
    import io

    project = get_current_project()
    if not project:
        return jsonify({'error': 'Unauthorized'}), 401

    if month_num < 1 or month_num > 12:
        return jsonify({'error': 'Invalid month number'}), 400

    try:
        # Get the month record
        month = CalendarMonth.query.filter_by(
            project_id=project.id,
            month_number=month_num
        ).first()

        if not month:
            return jsonify({'error': 'Month not found'}), 404

        # Check if already completed
        if month.generation_status == 'completed':
            return jsonify({
                'success': True,
                'status': 'completed',
                'message': f'Month {month_num} already generated'
            })

        # Mark as processing
        month.generation_status = 'processing'
        db.session.commit()

        # Get enhanced prompt for this month
        enhanced_prompt = get_enhanced_prompt(month_num)

        # Get reference images for face-swapping
        uploaded_images = UploadedImage.query.filter_by(project_id=project.id).all()
        reference_image_data = [img.file_data for img in uploaded_images]

        if not reference_image_data:
            month.generation_status = 'failed'
            month.error_message = 'No reference images found'
            db.session.commit()
            return jsonify({'error': 'No reference images'}), 400

        # Generate the image with AI
        image_data = generate_calendar_image(enhanced_prompt, reference_image_data)

        # Convert PNG to JPEG for smaller file size
        img = PILImage.open(io.BytesIO(image_data))
        img_io = io.BytesIO()
        img.convert('RGB').save(img_io, format='JPEG', quality=95)
        jpeg_data = img_io.getvalue()

        # Save to database
        month.master_image_data = jpeg_data
        month.generation_status = 'completed'
        from datetime import datetime
        month.generated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'status': 'completed',
            'month': month_num,
            'message': f'Month {month_num} generated successfully',
            'image_size': len(jpeg_data)
        })

    except Exception as e:
        # Mark as failed
        if month:
            month.generation_status = 'failed'
            month.error_message = str(e)
            db.session.commit()

        return jsonify({
            'success': False,
            'status': 'failed',
            'month': month_num,
            'error': str(e)
        }), 500
