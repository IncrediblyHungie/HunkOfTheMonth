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
        mimetype='image/png'
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
