"""
AeroGuard Flask Application Factory

This module initializes the Flask application with all necessary
configurations, blueprints, error handlers, and middleware.

Architecture:
    - Application Factory Pattern: Enables multiple app instances with different configs
    - Blueprint Pattern: Modular route organization (health, forecast, model, comparison)
    - Middleware Pattern: Request logging, CORS, error handling
    - Service Layer: Decoupled business logic from routes

Usage:
    >>> from app import create_app
    >>> app = create_app()
    >>> app.run()

Example with custom config:
    >>> from app.config import DevelopmentConfig
    >>> app = create_app(DevelopmentConfig)
"""

import logging
from flask import Flask, app
from flask_cors import CORS

from app.config import Config
from app.database import init_db
from app.utils.error_handlers import register_error_handlers
from app.routes import health, forecast, model
from app.routes.model_comparison import model_comparison_bp
from flask_jwt_extended import JWTManager

logger = logging.getLogger(__name__)


def create_app(config_class=None):
    """
    Application factory function.

    Creates and configures the Flask application with all necessary:
    - Configuration settings
    - CORS middleware
    - Blueprint routes
    - Error handlers
    - Request/response middleware

    Args:
        config_class (class, optional): Configuration class to use.
            Defaults to Config. Common options:
            - Config: Base configuration
            - DevelopmentConfig: Development with debug enabled
            - ProductionConfig: Production with security hardening
            - TestingConfig: Testing with in-memory database

    Returns:
        Flask: Configured Flask application instance ready to serve requests

    Raises:
        ImportError: If configuration class cannot be imported
        ValueError: If required settings are missing in production

    Example:
        >>> from app import create_app
        >>> from app.config import DevelopmentConfig
        >>> app = create_app(DevelopmentConfig)
        >>> app.run(debug=True)
    """
    if config_class is None:
        config_class = Config

    # Create Flask app instance
    app = Flask(__name__)
    logger.debug(f"Creating Flask app with config: {config_class.__name__}")

    try:
        # Load configuration
        app.config.from_object(config_class)
        logger.info(f"✓ Configuration loaded: {config_class.__name__}")

        # Initialize JWT
        jwt = JWTManager()
        jwt.init_app(app)

        # Initialize database
        init_db(app)

        # Initialize CORS (Cross-Origin Resource Sharing)
        _setup_cors(app)

        # Register error handlers (400, 401, 403, 404, 405, 500, 503, etc.)
        _register_error_handlers(app)

        # Register route blueprints
        _register_blueprints(app)

        # Register request/response hooks
        _register_hooks(app)

        logger.info("✓ Application factory complete - all components initialized")

    except Exception as e:
        logger.error(f"✗ Failed to create application: {e}", exc_info=True)
        raise

    return app


def _setup_cors(app):
    """
    Configure CORS (Cross-Origin Resource Sharing).

    Allows:
    - All origins (configurable via CORS_ORIGINS setting)
    - Common methods (GET, POST, PUT, DELETE, OPTIONS)
    - Common headers (Content-Type, Authorization, etc.)
    - Credentials (cookies, authorization headers)

    Args:
        app (Flask): Flask application instance
    """
    try:
        CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
        logger.info("✓ CORS initialized")
    except Exception as e:
        logger.error(f"✗ CORS initialization failed: {e}")
        raise


def _register_error_handlers(app):
    """
    Register global error handlers.

    Handles:
    - 400: Bad Request (validation errors)
    - 401: Unauthorized (authentication errors)
    - 403: Forbidden (authorization errors)
    - 404: Not Found (missing endpoints)
    - 405: Method Not Allowed
    - 500: Internal Server Error
    - 503: Service Unavailable

    Args:
        app (Flask): Flask application instance
    """
    try:
        register_error_handlers(app)
        logger.info("✓ Error handlers registered")
    except Exception as e:
        logger.error(f"✗ Error handler registration failed: {e}")
        raise


def _register_blueprints(app):
    """
    Register all route blueprints.

    Blueprints:
    - health.bp: Health check and status endpoints (/)
    - forecast.bp: Air quality forecasting (/api/v1/forecast)
    - model.bp: Model management (/api/v1/model)
    - model_comparison_bp: Model comparison (/api/v1/model/compare)
    - realtime_aqi.bp: Real-time AQI data (/api/v1/realtime-aqi)

    Args:
        app (Flask): Flask application instance
    """
    from app.routes import user as user_routes
    from app.routes import realtime_aqi as realtime_aqi_routes
    from app.routes import generative_ai as generative_ai_routes
    from app.routes import analytics_route as analytics_bp



    blueprints = [
        (health.bp, "Health Check"),
        (forecast.bp, "Forecast"),
        (model.bp, "Model Management"),
        (model_comparison_bp, "Model Comparison"),
        (user_routes.bp, "User API"),
        (realtime_aqi_routes.bp, "Real-time AQI"),
        (generative_ai_routes.bp, "Generative AI"),
        (analytics_bp.bp, "Analytics")
    ]

    try:
        for blueprint, name in blueprints:
            app.register_blueprint(blueprint)
            prefix = getattr(blueprint, "url_prefix", "/")
            logger.info(f"  ✓ {name:25} -> {prefix}")
        logger.info("✓ All blueprints registered")
    except Exception as e:
        logger.error(f"✗ Blueprint registration failed: {e}")
        raise


def _register_hooks(app):
    """
    Register request/response middleware hooks.

    Hooks:
    - before_request: Log incoming requests and generate request ID
    - after_request: Add response headers, log response times

    Args:
        app (Flask): Flask application instance
    """
    import time
    import uuid
    from flask import request, g

    @app.before_request
    def before_request():
        """Log incoming request details and generate request ID."""
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())
        logger.debug(f"→ {request.method:6} {request.path} [ID: {g.request_id}]")

    @app.after_request
    def after_request(response):
        """Log response details and add headers."""
        # Calculate response time
        duration = time.time() - getattr(g, "start_time", 0)

        # Add response headers
        response.headers["X-Request-ID"] = getattr(g, "request_id", str(uuid.uuid4()))
        response.headers["X-Response-Time"] = f"{duration:.6f}"
        response.headers["X-Powered-By"] = "AeroGuard/1.0"
        response.headers["Server"] = "AeroGuard/1.0"

        logger.debug(f"← {response.status_code:3} {request.path} ({duration:.3f}s)")
        return response

    logger.info("✓ Request/response hooks registered")
