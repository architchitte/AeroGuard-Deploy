"""
Health Check Routes

Endpoints for system health monitoring.
"""

from flask import Blueprint, jsonify
from datetime import datetime

bp = Blueprint("health", __name__, url_prefix="/api/v1/health")


@bp.route("", methods=["GET"])
def health_check():
    """
    Health check endpoint.

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


@bp.route("/ready", methods=["GET"])
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


@bp.route("/live", methods=["GET"])
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
