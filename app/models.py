"""
Database models for the calendar platform
"""
from datetime import datetime
from app import db

class GuestSession(db.Model):
    """Guest sessions for users who don't create accounts"""
    __tablename__ = 'guest_sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), nullable=True)  # Optional email for notifications
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    # Relationships
    projects = db.relationship('CalendarProject', backref='guest_session', lazy=True, cascade='all, delete-orphan')

class User(db.Model):
    """Registered users (optional - for returning customers)"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    projects = db.relationship('CalendarProject', backref='user', lazy=True)

class CalendarProject(db.Model):
    """A calendar creation project"""
    __tablename__ = 'calendar_projects'

    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(64), db.ForeignKey('guest_sessions.session_token'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    status = db.Column(db.String(50), default='uploading', index=True)
    # Status values: uploading, prompts, processing, preview, checkout, completed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    calendar_format = db.Column(db.String(50))  # portrait, landscape, square

    # Relationships
    uploaded_images = db.relationship('UploadedImage', backref='project', lazy=True, cascade='all, delete-orphan')
    calendar_months = db.relationship('CalendarMonth', backref='project', lazy=True, cascade='all, delete-orphan')
    order = db.relationship('Order', backref='project', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<CalendarProject {self.id} - {self.status}>'

class UploadedImage(db.Model):
    """User-uploaded selfies for reference"""
    __tablename__ = 'uploaded_images'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('calendar_projects.id'), nullable=False, index=True)

    filename = db.Column(db.String(255), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False)  # Store image data directly
    thumbnail_data = db.Column(db.LargeBinary)  # Small thumbnail for preview

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UploadedImage {self.id} - {self.filename}>'

class CalendarMonth(db.Model):
    """Individual calendar month with AI-generated image"""
    __tablename__ = 'calendar_months'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('calendar_projects.id'), nullable=False, index=True)

    month_number = db.Column(db.Integer, nullable=False)  # 1-12
    prompt = db.Column(db.Text, nullable=False)

    # AI Generation
    master_image_data = db.Column(db.LargeBinary)  # Generated image data
    generation_status = db.Column(db.String(50), default='pending')
    # Status: pending, processing, completed, failed

    generated_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)

    def __repr__(self):
        return f'<CalendarMonth {self.month_number} - {self.generation_status}>'

class Order(db.Model):
    """Order information (mock for now)"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('calendar_projects.id'), nullable=False, unique=True, index=True)

    email = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending')
    # Status: pending, coming_soon (mock status)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'
