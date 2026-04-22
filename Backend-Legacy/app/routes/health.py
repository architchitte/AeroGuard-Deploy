"""
Health Check Routes

Endpoints for system health monitoring.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime

bp = Blueprint("health", __name__)


@bp.route("/", methods=["GET"])
def root():
    """Root endpoint with API information."""
    return jsonify(
        {
            "message": f"Welcome to {current_app.config.get('APP_NAME', 'AeroGuard')}",
            "version": current_app.config.get("APP_VERSION", "1.0.0"),
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "health": "/health",
                "info": "/info",
                "forecast": "/api/forecast",
                "models": "/api/v1/models",
            }
        }
    ), 200


@bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": current_app.config.get("APP_VERSION", "1.0.0"),
            "service": current_app.config.get("APP_NAME", "AeroGuard"),
            "environment": current_app.config.get("ENV", "production"),
        }
    ), 200


@bp.route("/info", methods=["GET"])
def info():
    """Application information endpoint."""
    return jsonify(
        {
            "name": current_app.config.get("APP_NAME", "AeroGuard"),
            "version": current_app.config.get("APP_VERSION", "1.0.0"),
            "description": current_app.config.get("APP_DESCRIPTION", "Air Quality Forecasting System"),
            "environment": current_app.config.get("ENV", "production"),
            "debug": current_app.debug,
            "timestamp": datetime.now().isoformat(),
        }
    ), 200


@bp.route("/api/v1/health", methods=["GET"])
def health_check_api():
    """
    Health check endpoint (API version).

    Returns:
        JSON with health status
    """
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "service": "AeroGuard",
        }
    ), 200


@bp.route("/api/v1/health/ready", methods=["GET"])
def readiness_check():
    """
    Readiness check endpoint.

    Returns:
        JSON with readiness status
    """
    return jsonify(
        {
            "ready": True,
            "timestamp": datetime.now().isoformat(),
        }
    ), 200


@bp.route("/api/v1/health/live", methods=["GET"])
def liveness_check():
    """
    Liveness check endpoint.

    Returns:
        JSON with liveness status
    """
    return jsonify(
        {
            "alive": True,
            "timestamp": datetime.now().isoformat(),
        }
    ), 200
