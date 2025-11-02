"""
Hunk of the Month - AI Calendar Platform
Flask application factory
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

    # TEMPORARY: Database disabled - using session storage only for testing
    # This allows us to focus on AI image generation without database setup
    print("=" * 60)
    print("DATABASE DISABLED - Using session storage for testing")
    print("=" * 60)

    # Minimal config - no database needed
    app.config['SQLALCHEMY_DATABASE_URI'] = None
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Upload limits optimized for mobile/iPhone users
    # Per image: 8MB (after client-side compression, original can be larger)
    # Total request: 40MB (allows 5 high-quality photos)
    app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024  # 40MB max total request

    # Session configuration (stores everything in browser session temporarily)
    app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('PERMANENT_SESSION_LIFETIME', 86400))
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Printify configuration
    app.config['PRINTIFY_API_TOKEN'] = os.getenv('PRINTIFY_API_TOKEN')
    app.config['PRINTIFY_SHOP_ID'] = os.getenv('PRINTIFY_SHOP_ID', None)  # Auto-detect from API

    # Stripe configuration
    app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
    app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')
    app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv('STRIPE_WEBHOOK_SECRET')

    # Initialize Stripe - MUST import at app level before any services use it
    import stripe
    if app.config.get('STRIPE_SECRET_KEY'):
        stripe.api_key = app.config['STRIPE_SECRET_KEY']
        print("✓ Stripe initialized")
    else:
        print("⚠ STRIPE_SECRET_KEY not configured - payment features disabled")

    # Skip database initialization
    # db.init_app(app)
    # migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    from app.routes import main, projects, api, webhooks
    app.register_blueprint(main.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(webhooks.bp)

    return app
