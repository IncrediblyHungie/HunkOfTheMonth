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

    # Skip database initialization
    # db.init_app(app)
    # migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    from app.routes import main, projects, api
    app.register_blueprint(main.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(api.bp)

    return app
