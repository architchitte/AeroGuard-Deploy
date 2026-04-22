"""
Health Risk Routes

Endpoints for health risk assessment based on AQI data.
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.health_risk_ml import get_health_risk_service
from app.services.realtime_aqi_service import RealtimeAQIService
from app.utils.validators import InputValidator
from app.utils.error_handlers import ValidationError

bp = Blueprint("health_risk", __name__, url_prefix="/api/v1/health-risk")

@bp.route("", methods=["GET"])
def get_health_risk_assessment():
    """
    Get health risk assessment for a given AQI, location, and persona.
    
    Query Parameters:
        aqi (float): AQI value (optional if location provided)
        location (str): Location name (optional)
        pollutant (str): Primary pollutant (default: PM2.5)
        persona (str): User persona (optional)
        
    Returns:
        JSON with health risk assessment
    """
    try:
        aqi_value = request.args.get("aqi", type=float)
        location = request.args.get("location")
        pollutant = request.args.get("pollutant", "PM2.5")
        persona = request.args.get("persona")

        # If location is provided but no AQI, fetch real-time AQI
        if location and aqi_value is None:
            aqi_service = RealtimeAQIService()
            aqi_data = aqi_service.get_city_aqi(location)
            if not aqi_data or 'aqi' not in aqi_data:
                return jsonify({
                    "status": "error",
                    "message": f"Could not fetch real-time AQI for {location}",
                    "code": 404
                }), 404
            aqi_value = aqi_data['aqi']
            pollutant = aqi_data.get('dominant', 'PM2.5')

        # If still no AQI value, error
        if aqi_value is None:
            return jsonify({
                "status": "error",
                "message": "AQI value or location must be provided",
                "code": 400
            }), 400

        # Get service and assess risk
        health_service = get_health_risk_service()
        assessment = health_service.assess_health_risk(
            aqi_value=aqi_value,
            pollutant=pollutant,
            location=location,
            persona=persona
        )

        return jsonify(assessment), 200

    except Exception as e:
        current_app.logger.exception("Health risk assessment failed")
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500

@bp.route("/info", methods=["GET"])
def get_model_info():
    """Get information about the health risk model."""
    try:
        health_service = get_health_risk_service()
        info = health_service.get_model_info()
        return jsonify(info), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500
