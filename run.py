"""
Hunk of the Month - Application Entry Point
"""
import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get host and port from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))

    # Run the application
    app.run(
        host=host,
        port=port,
        debug=os.getenv('FLASK_ENV') == 'development'
    )
