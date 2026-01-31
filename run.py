"""
AeroGuard Application Entry Point

Run the Flask application for development.
"""

import os
from app import create_app
from app.config import DevelopmentConfig, ProductionConfig

if __name__ == "__main__":
    # Load configuration based on environment
    env = os.getenv("FLASK_ENV", "development")
    config = DevelopmentConfig if env == "development" else ProductionConfig

    # Create Flask app
    app = create_app(config)

    # Run development server
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", True),
    )
