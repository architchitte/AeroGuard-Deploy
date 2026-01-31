"""
Application Configuration

Centralized configuration for different environments.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration."""

    # Flask settings
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", False)
    TESTING = False

    # API settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    # CORS settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # Model settings
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "saved")
    MODEL_CACHE_TIMEOUT = int(os.getenv("MODEL_CACHE_TIMEOUT", 3600))  # 1 hour

    # Data settings
    MAX_FORECAST_DAYS = 30
    MIN_FORECAST_DAYS = 1
    DEFAULT_FORECAST_DAYS = 7

    # Request settings
    MAX_REQUEST_SIZE = 1024 * 1024  # 1 MB
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration."""

    ENV = "development"
    DEBUG = True
    JSONIFY_PRETTYPRINT_REGULAR = True


class TestingConfig(Config):
    """Testing configuration."""

    ENV = "testing"
    TESTING = True
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    ENV = "production"
    DEBUG = False
