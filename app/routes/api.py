"""
API routes for AJAX calls and image serving
"""
from flask import Blueprint, jsonify, send_file, Response, request, url_for
from app import session_storage
from app.routes.main import get_current_project
from app.services import stripe_service
import io

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/image/thumbnail/<int:image_id>')
def get_thumbnail(image_id):
    """Serve thumbnail image"""
    project = get_current_project()
    if not project:
        return jsonify({'error': 'Unauthorized'}), 401

    image = session_storage.get_image_by_id(image_id)

    if not image or not image.get('thumbnail_data'):
        return jsonify({'error': 'Image not found'}), 404

    return send_file(
        io.BytesIO(image['thumbnail_data']),
        mimetype='image/jpeg'
    )

@bp.route('/image/month/<int:month_id>')
def get_month_image(month_id):
    """Serve generated month image"""
    project = get_current_project()
    if not project:
        return jsonify({'error': 'Unauthorized'}), 401

    image_data = session_storage.get_month_image_data(month_id)

    if not image_data:
        return jsonify({'error': 'Image not found'}), 404

    return send_file(
        io.BytesIO(image_data),
        mimetype='image/jpeg'
    )

@bp.route('/project/status')
def project_status():
    """Get current project status"""
    project = get_current_project()
    if not project:
        return jsonify({'error': 'No active project'}), 404

    # Get generation status from session
    months = session_storage.get_all_months()

    return jsonify({
        'project_id': project['id'],
        'status': project['status'],
        'months': months
    })

@bp.route('/delete/image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    """Delete an uploaded image"""
    project = get_current_project()
    if not project:
        return jsonify({'error': 'Unauthorized'}), 401

    session_storage.delete_image(image_id)

    return jsonify({'success': True})

@bp.route('/generate/month/<int:month_num>', methods=['POST'])
def generate_month(month_num):
    """Generate a single month's image with AI face-swapping"""
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
        # Get the month record from session
        month = session_storage.get_month_by_number(month_num)

        if not month:
            return jsonify({'error': 'Month not found'}), 404

        # Check if already completed
        if month['generation_status'] == 'completed':
            return jsonify({
                'success': True,
                'status': 'completed',
                'message': f'Month {month_num} already generated'
            })

        # Mark as processing
        session_storage.update_month_status(month_num, 'processing')

        # Get reference images for face-swapping (already raw binary data!)
        uploaded_images = session_storage.get_uploaded_images()
        reference_image_data = [img['file_data'] for img in uploaded_images]

        if not reference_image_data:
            session_storage.update_month_status(month_num, 'failed', error='No reference images found')
            return jsonify({'error': 'No reference images'}), 400

        # Generate image with simple working prompts
        print(f"📸 Month {month_num}: Generating with classic prompts...")
        enhanced_prompt = get_enhanced_prompt(month_num)
        image_data = generate_calendar_image(enhanced_prompt, reference_image_data)
        print(f"✅ Month {month_num}: Generation succeeded!")

        # Convert PNG to JPEG for smaller file size
        # Quality 85 is sweet spot: great visual quality, 40-50% smaller files
        img = PILImage.open(io.BytesIO(image_data))
        img_io = io.BytesIO()
        img.convert('RGB').save(img_io, format='JPEG', quality=85, optimize=True)
        jpeg_data = img_io.getvalue()

        # Save to session storage
        session_storage.update_month_status(month_num, 'completed', image_data=jpeg_data)

        print(f"💾 Month {month_num}: Saved {len(jpeg_data)} bytes")

        return jsonify({
            'success': True,
            'status': 'completed',
            'month': month_num,
            'message': f'Month {month_num} generated successfully',
            'image_size': len(jpeg_data)
        })

    except Exception as e:
        # Mark as failed
        session_storage.update_month_status(month_num, 'failed', error=str(e))

        return jsonify({
            'success': False,
            'status': 'failed',
            'month': month_num,
            'error': str(e)
        }), 500

@bp.route('/test/gemini', methods=['GET'])
def test_gemini():
    """Test Gemini API connection and generation"""
    import os
    from app.services.gemini_service import GOOGLE_API_KEY, generate_calendar_image
    from app.services.monthly_themes import get_enhanced_prompt

    result = {
        'api_key_set': bool(GOOGLE_API_KEY),
        'api_key_prefix': GOOGLE_API_KEY[:20] if GOOGLE_API_KEY else None,
    }

    try:
        # Test simple generation
        simple_prompt = "A muscular shirtless firefighter with a helmet"
        image_data = generate_calendar_image(simple_prompt, reference_image_data_list=None)

        result['test_passed'] = True
        result['image_size'] = len(image_data) if image_data else 0
        result['message'] = 'Gemini API working correctly'

    except Exception as e:
        result['test_passed'] = False
        result['error'] = str(e)
        result['error_type'] = type(e).__name__

    return jsonify(result)

@bp.route('/checkout/create', methods=['POST'])
def create_checkout():
    """Create Stripe checkout session for calendar purchase"""
    project = get_current_project()
    if not project:
        return jsonify({'error': 'No active project'}), 401

    data = request.json
    product_type = data.get('product_type')

    if product_type not in ['calendar_2026', 'desktop', 'standard_wall']:
        return jsonify({'error': 'Invalid product type'}), 400

    try:
        # Create Stripe checkout session
        session_data = stripe_service.create_checkout_session(
            product_type=product_type,
            success_url=url_for('main.order_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('projects.preview', _external=True)
        )

        # Store checkout session ID in session storage for tracking
        # session_storage.save_checkout_session(session_data['session_id'], product_type)

        return jsonify({
            'success': True,
            'checkout_url': session_data['url'],
            'session_id': session_data['session_id']
        })

    except Exception as e:
        print(f"❌ Checkout creation error: {e}")
        return jsonify({'error': str(e)}), 500
