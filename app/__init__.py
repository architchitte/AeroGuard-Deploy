"""
AeroGuard Flask Application Factory

This module initializes the Flask application with all necessary
configurations, blueprints, and error handlers.
"""

from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.utils.error_handlers import register_error_handlers
from app.routes import health, forecast, model


def create_app(config_class=Config):
    """
    Create and configure the Flask application.

    Args:
        config_class: Configuration class to use (default: Config)

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CORS
    CORS(app)

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    app.register_blueprint(health.bp)
    app.register_blueprint(forecast.bp)
    app.register_blueprint(model.bp)

    return app
