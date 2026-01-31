#!/usr/bin/env python3
"""
Load environment variables from .env file

This script uses python-dotenv to load environment variables from .env file.
It should be called at the start of the application.

Usage:
    from dotenv import load_dotenv
    load_dotenv()  # Load from .env file in current directory
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Verify critical variables are set
def verify_env_setup():
    """Verify that required environment variables are configured."""
    required_vars = {
        "FLASK_ENV": "Flask environment (development/production/testing)",
        "SECRET_KEY": "Secret key for Flask session management",
    }
    
    optional_vars = {
        "OPENAI_API_KEY": "OpenAI API key (for generative explanations)",
        "CORS_ORIGINS": "Comma-separated CORS origins",
    }
    
    print("\n" + "="*70)
    print("ENVIRONMENT CONFIGURATION CHECK")
    print("="*70)
    
    missing_required = []
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value and var not in ["SECRET_KEY"]:  # Don't print secret keys
            status = "✓"
        elif value:
            status = "✓ (hidden)"
        else:
            status = "✗ MISSING"
            missing_required.append(var)
        print(f"{status:12} {var:20} - {desc}")
    
    print("\n" + "-"*70)
    print("OPTIONAL VARIABLES:")
    print("-"*70)
    
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        status = "✓" if value else "○"
        print(f"{status:12} {var:20} - {desc}")
    
    print("="*70 + "\n")
    
    if missing_required:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_required)}\n"
            f"Please set these in your .env file."
        )

if __name__ == "__main__":
    verify_env_setup()
    print("✓ Environment loaded successfully!")
