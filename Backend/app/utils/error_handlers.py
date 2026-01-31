"""
Error Handlers

Centralized error handling for the Flask application.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException
from datetime import datetime
import uuid


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

    # Mapping of HTTP status codes to error code names
    ERROR_CODES = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }

    def _make_error_response(error_code, message, status_code):
        """Helper to create consistent error responses."""
        return jsonify({
            "error": error_code,
            "message": message,
            "status": status_code,
            "timestamp": datetime.now().isoformat(),
        }), status_code

    @app.errorhandler(AeroGuardException)
    def handle_aeroguard_exception(error):
        """Handle custom AeroGuard exceptions."""
        error_code = ERROR_CODES.get(error.status_code, "ERROR")
        return _make_error_response(error_code, error.message, error.status_code)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors."""
        return _make_error_response("BAD_REQUEST", error.message, 400)

    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle bad request errors."""
        message = "Bad request"
        if hasattr(error, 'description'):
            message = str(error.description)
        return _make_error_response("BAD_REQUEST", message, 400)

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle not found errors."""
        return _make_error_response("NOT_FOUND", "Resource not found", 404)

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle method not allowed errors."""
        # Try to extract the allowed methods and HTTP method from the error
        message = "Method not allowed"
        if hasattr(error, 'description') and error.description:
            # Description format is usually like "Method GET. Not Allowed"
            description = str(error.description)
            # Try to extract HTTP method name from the request
            from flask import request
            method = request.method
            if method:
                message = f"Method {method} not allowed"
            else:
                message = description
        return _make_error_response("METHOD_NOT_ALLOWED", message, 405)

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle internal server errors."""
        return _make_error_response("INTERNAL_SERVER_ERROR", "Internal server error", 500)

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all unhandled exceptions."""
        # Check if it's an HTTP exception
        if isinstance(error, HTTPException):
            status_code = error.code if hasattr(error, 'code') else 500
            error_code = ERROR_CODES.get(status_code, "ERROR")
            message = str(error.description) if hasattr(error, 'description') else str(error)
            return _make_error_response(error_code, message, status_code)
        
        return _make_error_response("INTERNAL_SERVER_ERROR", "An unexpected error occurred", 500)
