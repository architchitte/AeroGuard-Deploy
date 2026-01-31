"""
WSGI Entry Point

Production-ready WSGI entry point for Gunicorn.
"""

import os
from app import create_app
from app.config import ProductionConfig, DevelopmentConfig

# Load configuration based on environment
env = os.getenv("FLASK_ENV", "production")
config = ProductionConfig if env == "production" else DevelopmentConfig

# Create Flask app
app = create_app(config)

if __name__ == "__main__":
    app.run()
