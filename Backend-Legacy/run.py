#!/usr/bin/env python
"""
AeroGuard Application Entry Point

Starts the Flask development server with environment-based configuration.

Usage:
    python run.py                    # Start with default (development) config
    FLASK_ENV=production python run.py  # Start with production config
    FLASK_HOST=localhost python run.py  # Custom host

Environment Variables:
    FLASK_ENV           : development | production (default: development)
    FLASK_HOST          : Server host (default: 0.0.0.0)
    FLASK_PORT          : Server port (default: 5000)
    FLASK_DEBUG         : Enable debug mode (default: True in development)
    CORS_ORIGINS        : Comma-separated CORS origins (default: *)

Examples:
    # Development with auto-reload and debug
    python run.py

    # Production server
    FLASK_ENV=production python run.py

    # Custom port
    FLASK_PORT=8080 python run.py

    # Localhost only
    FLASK_HOST=localhost python run.py
"""

import os
import sys
import logging

# Load environment variables from .env file BEFORE importing Flask
from dotenv import load_dotenv
import pathlib
env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging before importing Flask
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from app import create_app
from app.config import DevelopmentConfig, ProductionConfig, Config
from app.utils.startup import validate_setup, diagnose_issues


def validate_environment():
    """
    Validate that the environment is ready to run the application.

    Checks:
    - Required packages are installed
    - Configuration is valid
    - Data directories exist

    Returns:
        bool: True if environment is valid, False otherwise
    """
    try:
        logger.info("Validating environment...")

        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8+ required")
            return False

        logger.info(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

        # Run comprehensive startup validation
        if not validate_setup():
            logger.error("  ✗ Setup validation failed")
            diagnose_issues()
            return False

        return True

    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        diagnose_issues()
        return False


def main():
    """
    Main entry point for the application.

    - Validates environment
    - Loads configuration
    - Creates Flask app
    - Starts development server
    """
    try:
        # Validate environment
        if not validate_environment():
            logger.error("Environment validation failed. Cannot start application.")
            return 1

        # Get configuration
        env = os.getenv("FLASK_ENV", "development")
        config_map = {
            "development": DevelopmentConfig,
            "production": ProductionConfig,
            "testing": Config,
        }
        config_class = config_map.get(env, DevelopmentConfig)

        logger.info(f"\n{'='*60}")
        logger.info(f"  AeroGuard Backend - Starting")
        logger.info(f"{'='*60}")
        logger.info(f"Environment : {env.upper()}")
        logger.info(f"Config      : {config_class.__name__}")

        # Create Flask app
        app = create_app(config_class)

        # Get server configuration
        host = os.getenv("FLASK_HOST", "0.0.0.0")
        port = int(os.getenv("FLASK_PORT", 5000))
        debug = env == "development"

        logger.info(f"Host        : {host}")
        logger.info(f"Port        : {port}")
        logger.info(f"Debug       : {debug}")
        logger.info(f"{'='*60}\n")

        # Start server
        logger.info(f"Starting Flask development server...")
        logger.info(f"Open browser at: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
        logger.info(f"Health check: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/health")
        logger.info(f"Quick start: See Readme.md for setup instructions\n")

        app.run(
            host=host,
            port=port,
            debug=debug,
        )

        return 0

    except KeyboardInterrupt:
        logger.info("\nShutdown requested")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
