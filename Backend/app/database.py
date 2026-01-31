"""
Database initialization and connection management

Configures SQLAlchemy with Flask and provides database session management.
Supports NeonDB (PostgreSQL) for production and SQLite for development.
"""

from flask_sqlalchemy import SQLAlchemy
import logging

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy with Flask-SQLAlchemy integration
# This uses Flask-SQLAlchemy's default model class configuration
db = SQLAlchemy()


def init_db(app):
    """
    Initialize database with Flask app.
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            logger.info("✓ Database tables created successfully")
        except Exception as e:
            logger.error(f"✗ Database initialization error: {e}")
            raise


def get_db():
    """Get current database session"""
    return db.session
