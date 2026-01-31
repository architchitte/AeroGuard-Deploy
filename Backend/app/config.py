"""
Application Configuration Management

Centralized configuration for different environments with clear settings
organized by category. Supports development, testing, and production.

Environment Variables (optional):
    FLASK_ENV              : development | production | testing
    FLASK_DEBUG            : true | false
    FLASK_HOST             : Server hostname (default: 0.0.0.0)
    FLASK_PORT             : Server port (default: 5000)
    CORS_ORIGINS           : Comma-separated list of allowed origins
    MODEL_CACHE_TIMEOUT    : Model cache duration in seconds (default: 3600)
    REQUEST_TIMEOUT        : Request timeout in seconds (default: 30)
    LOG_LEVEL              : Logging level (DEBUG, INFO, WARNING, ERROR)

Configuration Classes:
    Config              : Base configuration (production-like)
    DevelopmentConfig   : Development with debug enabled
    TestingConfig       : Testing configuration
    ProductionConfig    : Production hardened configuration

Example Usage:
    from app import create_app
    from app.config import DevelopmentConfig
    
    app = create_app(DevelopmentConfig)
    app.run()
"""

import os
from datetime import timedelta


class Config:
    """
    Base configuration class.

    Contains default settings suitable for production.
    All specific configs should inherit from this.
    """

    # ========================================================================
    # Flask Settings
    # ========================================================================
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    TESTING = False
    SECRET_KEY = os.getenv(
        "SECRET_KEY", "dev-key-change-in-production"
    )

    # ========================================================================
    # API Settings
    # ========================================================================
    # JSON response formatting
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    # ========================================================================
    # CORS Settings (Cross-Origin Resource Sharing)
    # ========================================================================
    # Allowed origins (comma-separated in env var)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # ========================================================================
    # Model Settings
    # ========================================================================
    # Directory for saved models
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "saved")
    
    # Cache timeout for loaded models (in seconds)
    MODEL_CACHE_TIMEOUT = int(os.getenv("MODEL_CACHE_TIMEOUT", 3600))  # 1 hour

    # ========================================================================
    # Data Processing Settings
    # ========================================================================
    # Forecast horizon limits (in days)
    MAX_FORECAST_DAYS = 30
    MIN_FORECAST_DAYS = 1
    DEFAULT_FORECAST_DAYS = 7

    # ========================================================================
    # Request Settings
    # ========================================================================
    # Maximum request size (bytes) - 1 MB
    MAX_REQUEST_SIZE = 1024 * 1024
    
    # Request timeout (seconds)
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

    # ========================================================================
    # Logging Settings
    # ========================================================================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """
    Development configuration.

    Enables:
    - Debug mode with auto-reload
    - Pretty-printed JSON responses
    - Verbose logging
    - Relaxed CORS (allows all origins)

    Use this for local development.
    """

    ENV = "development"
    DEBUG = True
    JSONIFY_PRETTYPRINT_REGULAR = True
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")


class TestingConfig(Config):
    """
    Testing configuration.

    Enables:
    - Testing mode
    - Debug mode
    - In-memory operations

    Use this for running tests.
    """

    ENV = "testing"
    TESTING = True
    DEBUG = True
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")


class ProductionConfig(Config):
    """
    Production configuration.

    Enforces:
    - Debug mode disabled
    - No pretty-printing (saves bandwidth)
    - Secure headers
    - Limited CORS origins

    Use this for production deployment.
    """

    ENV = "production"
    DEBUG = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")

    # Production must specify origins
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv(
        "CORS_ORIGINS"
    ) else ["https://yourdomain.com"]
