"""
Error Handlers

Centralized error handling for the Flask application.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException


class AeroGuardException(Exception):
    """Base exception for AeroGuard application."""

    def __init__(self, message: str, status_code: int = 400):
        """
        Initialize custom exception.

        Args:
            message: Error message
            status_code: HTTP status code
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AeroGuardException):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, 400)


class ModelNotTrainedError(AeroGuardException):
    """Raised when model is used before training."""

    def __init__(self, message: str = "Model must be trained before use"):
        super().__init__(message, 400)


class DataServiceError(AeroGuardException):
    """Raised when data service operations fail."""

    def __init__(self, message: str):
        super().__init__(message, 500)


class ModelLoadError(AeroGuardException):
    """Raised when model loading fails."""

    def __init__(self, message: str = "Failed to load model"):
        super().__init__(message, 500)


def register_error_handlers(app):
    """
    Register error handlers with Flask app.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(AeroGuardException)
    def handle_aeroguard_exception(error):
        """Handle custom AeroGuard exceptions."""
        response = {
            "status": "error",
            "message": error.message,
            "code": error.status_code,
        }
        return jsonify(response), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors."""
        response = {
            "status": "error",
            "message": error.message,
            "code": 400,
        }
        return jsonify(response), 400

    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle bad request errors."""
        response = {
            "status": "error",
            "message": "Bad request",
            "code": 400,
        }
        return jsonify(response), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle not found errors."""
        response = {
            "status": "error",
            "message": "Resource not found",
            "code": 404,
        }
        return jsonify(response), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle internal server errors."""
        response = {
            "status": "error",
            "message": "Internal server error",
            "code": 500,
        }
        return jsonify(response), 500

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all unhandled exceptions."""
        response = {
            "status": "error",
            "message": "An unexpected error occurred",
            "code": 500,
        }
        return jsonify(response), 500
