"""
Startup Validation & Diagnostics

Provides tools for validating application setup and diagnosing issues.

Usage:
    from app.utils.startup import validate_setup, diagnose_issues
    
    if not validate_setup():
        diagnose_issues()
        exit(1)
"""

import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_setup():
    """
    Validate that the application setup is complete.

    Checks:
    - Python version >= 3.8
    - Required directories exist
    - Key dependencies importable
    - Configuration readable

    Returns:
        bool: True if setup is valid, False otherwise
    """
    checks = [
        ("Python Version", _check_python_version),
        ("Required Directories", _check_directories),
        ("Core Dependencies", _check_dependencies),
        ("Configuration", _check_configuration),
    ]

    all_valid = True
    for check_name, check_func in checks:
        try:
            result = check_func()
            if result:
                logger.info(f"✓ {check_name}")
            else:
                logger.error(f"✗ {check_name}")
                all_valid = False
        except Exception as e:
            logger.error(f"✗ {check_name}: {e}")
            all_valid = False

    return all_valid


def diagnose_issues():
    """
    Provide detailed diagnostic information for troubleshooting.

    Outputs:
    - Python version and path
    - Installed packages
    - Directory structure
    - Configuration files
    - Environment variables
    """
    logger.info("\n" + "="*60)
    logger.info("DIAGNOSTICS")
    logger.info("="*60)

    # Python info
    logger.info(f"\nPython Version: {sys.version}")
    logger.info(f"Python Executable: {sys.executable}")
    logger.info(f"Python Path: {sys.prefix}")

    # Check imports
    logger.info("\nTrying to import key packages:")
    packages = ["flask", "pandas", "xgboost", "statsmodels", "sklearn"]
    for package in packages:
        try:
            __import__(package)
            logger.info(f"  ✓ {package}")
        except ImportError as e:
            logger.error(f"  ✗ {package}: {e}")

    # Directory structure
    logger.info("\nDirectory Structure:")
    base_dirs = ["app", "app/routes", "app/services", "app/models", "tests", "docs"]
    for dir_name in base_dirs:
        exists = "✓" if os.path.isdir(dir_name) else "✗"
        logger.info(f"  {exists} {dir_name}/")

    # Configuration files
    logger.info("\nConfiguration Files:")
    config_files = ["app/config.py", ".env", "requirements.txt"]
    for config_file in config_files:
        exists = "✓" if os.path.isfile(config_file) else "✗"
        logger.info(f"  {exists} {config_file}")

    # Environment variables
    logger.info("\nEnvironment Variables:")
    env_vars = ["FLASK_ENV", "FLASK_HOST", "FLASK_PORT", "FLASK_DEBUG", "LOG_LEVEL"]
    for env_var in env_vars:
        value = os.getenv(env_var, "not set")
        logger.info(f"  {env_var}: {value}")

    logger.info("\n" + "="*60)


def _check_python_version():
    """Check Python version >= 3.8."""
    version = sys.version_info
    required = (3, 8)
    return version >= required


def _check_directories():
    """Check that required directories exist."""
    required_dirs = [
        "app",
        "app/routes",
        "app/services",
        "app/models",
        "app/utils",
    ]

    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            logger.error(f"Missing directory: {dir_path}")
            return False

    return True


def _check_dependencies():
    """Check that core dependencies can be imported."""
    required_packages = {
        "flask": "Flask web framework",
        "flask_cors": "CORS support",
        "pandas": "Data manipulation",
        "numpy": "Numerical computing",
        "xgboost": "XGBoost models",
        "statsmodels": "SARIMA models",
    }

    missing = []
    for package, description in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(f"{package} ({description})")

    if missing:
        logger.error(f"Missing packages: {', '.join(missing)}")
        logger.error("Run: pip install -r requirements.txt")
        return False

    return True


def _check_configuration():
    """Check that configuration can be loaded."""
    try:
        from app.config import Config, DevelopmentConfig, ProductionConfig

        # Test that config classes have required attributes
        # ENV is the Flask attribute name (uses FLASK_ENV env var internally)
        required_attrs = ["ENV", "DEBUG"]
        for config_class in [Config, DevelopmentConfig, ProductionConfig]:
            for attr in required_attrs:
                if not hasattr(config_class, attr):
                    logger.error(f"{config_class.__name__} missing {attr}")
                    return False

        return True
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return False


def health_check():
    """
    Perform a quick health check.

    Returns:
        dict: Health status with details
    """
    from datetime import datetime

    checks = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "setup_valid": validate_setup(),
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("FLASK_ENV", "development"),
    }

    return checks


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s"
    )

    print("\nValidating AeroGuard setup...\n")
    if validate_setup():
        print("\n✅ Setup is valid! Ready to start.\n")
    else:
        print("\n❌ Setup validation failed.\n")
        diagnose_issues()
        sys.exit(1)
