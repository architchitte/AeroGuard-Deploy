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
    
    # SECRET_KEY must be set in production
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        if ENV == "production":
            raise ValueError(
                "SECRET_KEY environment variable must be set in production. "
                "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        else:
            # Development fallback only
            SECRET_KEY = "dev-key-for-development-only-change-in-production"

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
    # Database Settings (NeonDB PostgreSQL or SQLite)
    # ========================================================================
    # NeonDB PostgreSQL connection (production)
    # Format: postgresql://user:password@host.neon.tech/database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///aeroguard.db"  # Default to SQLite for development
    )
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Connection pool settings
    # Use different engine options depending on the backend. Some
    # DB-API drivers (e.g. SQLite's) don't accept `connect_timeout`.
    if DATABASE_URL.startswith("sqlite:"):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {"check_same_thread": False}
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": 10,
            "pool_recycle": 3600,
            "pool_pre_ping": True,
            "connect_args": {"connect_timeout": 10},
        }

    # ========================================================================
    # Application Metadata
    # ========================================================================
    APP_NAME = "AeroGuard"
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    APP_DESCRIPTION = "Air Quality Forecasting and Health Advisory System"

    # ========================================================================
    # Session & Security
    # ========================================================================
    SESSION_COOKIE_SECURE = True  # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
    SESSION_COOKIE_SAMESITE = "Strict"  # Prevent CSRF
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)  # Shorter sessions

    # ========================================================================
    # JWT Configuration
    # ========================================================================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    if not JWT_SECRET_KEY:
        if ENV == "production":
            raise ValueError("JWT_SECRET_KEY must be set in production")
        else:
            JWT_SECRET_KEY = SECRET_KEY
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = "HS256"
    JWT_BLACKLIST_ENABLED = False  # Enable when implementing token revocation

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
    
    # Allow HTTP cookies in development
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """
    Testing configuration.

    Enables:
    - Testing mode
    - Debug disabled (for test stability)
    - In-memory operations

    Use this for running tests.
    """

    ENV = "testing"
    TESTING = True
    DEBUG = False
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
    SESSION_COOKIE_SECURE = True  # Require HTTPS in production

    # Production must specify origins - no defaults
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    if not CORS_ORIGINS:
        raise ValueError(
            "CORS_ORIGINS environment variable must be explicitly set in production. "
            "Example: CORS_ORIGINS=https://aero-guard-deploy.vercel.app,http://localhost:5173"
        )
