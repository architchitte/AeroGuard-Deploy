"""
Forecast Routes

Comprehensive Flask REST API routes for AeroGuard AQI forecasting system.

Endpoints:
- POST /forecast: Generate 6-hour AQI forecast from historical data
- POST /risk: Assess health risk from forecasted AQI and user persona
- POST /explain: Generate human-readable explanations for forecasts
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime, timedelta
import logging
import numpy as np

from app.services.forecasting_service import ForecastingService
from app.services.health_risk import HealthRiskClassifier, Persona
from app.services.explainability import AQIExplainer
from app.services.generative_explainer import GenerativeExplainer, ExplanationStyle
from app.utils.error_handlers import ValidationError

logger = logging.getLogger(__name__)

bp = Blueprint("forecast_routes", __name__, url_prefix="/api/v1")

# Service instances (lazy-loaded)
_forecast_service = None
_health_classifier = None
_explainability_engine = None
_generative_explainer = None


def _get_forecast_service() -> ForecastingService:
    """Get or initialize forecasting service."""
    global _forecast_service
    if _forecast_service is None:
        _forecast_service = ForecastingService()
    return _forecast_service


def _get_health_classifier() -> HealthRiskClassifier:
    """Get or initialize health risk classifier."""
    global _health_classifier
    if _health_classifier is None:
        _health_classifier = HealthRiskClassifier()
    return _health_classifier


def _get_explainability_engine() -> AQIExplainer:
    """Get or initialize explainability engine."""
    global _explainability_engine
    if _explainability_engine is None:
        _explainability_engine = AQIExplainer()
    return _explainability_engine


def _get_generative_explainer() -> GenerativeExplainer:
    """Get or initialize generative explainer."""
    global _generative_explainer
    if _generative_explainer is None:
        _generative_explainer = GenerativeExplainer()
    return _generative_explainer


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def _validate_location(data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate location field.

    Args:
        data: Request data dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    if "location" not in data:
        return False, "Missing required field: location"

    location = data["location"]
    if not isinstance(location, dict):
        return False, "Field 'location' must be an object"

    if "latitude" not in location or "longitude" not in location:
        return False, "Location must contain 'latitude' and 'longitude'"

    try:
        lat = float(location["latitude"])
        lon = float(location["longitude"])

        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90"
        if not (-180 <= lon <= 180):
            return False, "Longitude must be between -180 and 180"

        return True, None
    except (ValueError, TypeError):
        return False, "Latitude and longitude must be valid numbers"


def _validate_aqi_data(data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate AQI data array.

    Args:
        data: Request data dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    if "aqi_data" not in data:
        return False, "Missing required field: aqi_data"

    aqi_data = data["aqi_data"]
    if not isinstance(aqi_data, list):
        return False, "Field 'aqi_data' must be an array"

    if len(aqi_data) == 0:
        return False, "AQI data cannot be empty"

    if len(aqi_data) < 3:
        return False, "At least 3 historical AQI values required for forecasting"

    if len(aqi_data) > 365:
        return False, "Maximum 365 historical data points allowed"

    # Validate each data point
    for i, value in enumerate(aqi_data):
        try:
            aqi_value = float(value)
            if not (0 <= aqi_value <= 500):
                return False, f"AQI value at index {i} must be between 0 and 500"
        except (ValueError, TypeError):
            return False, f"AQI value at index {i} must be a valid number"

    return True, None


def _validate_persona(persona_str: str) -> Tuple[bool, Optional[str], Optional[Persona]]:
    """
    Validate persona value.

    Args:
        persona_str: Persona string from request

    Returns:
        Tuple of (is_valid, error_message, persona_enum)
    """
    valid_personas = [p.value for p in Persona]

    if persona_str not in valid_personas:
        return (
            False,
            f"Invalid persona. Must be one of: {', '.join(valid_personas)}",
            None,
        )

    persona = Persona(persona_str)
    return True, None, persona


def _validate_forecast_metadata(data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate forecast metadata for explanation endpoint.

    Args:
        data: Request data dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["forecast_values", "location"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    if not isinstance(data["forecast_values"], list):
        return False, "Field 'forecast_values' must be an array"

    if len(data["forecast_values"]) == 0:
        return False, "Forecast values cannot be empty"

    is_valid, error = _validate_location(data)
    if not is_valid:
        return False, error

    return True, None


# ============================================================================
# ENDPOINT: POST /forecast
# ============================================================================

@bp.route("/forecast", methods=["POST"])
def forecast():
    """
    Generate 6-hour AQI forecast from historical data.

    Request JSON:
    {
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "name": "New York" (optional)
        },
        "aqi_data": [45, 50, 52, 55, 60, 58, 61],
        "hours_ahead": 6 (optional, default 6, max 24),
        "include_confidence": true (optional, default true)
    }

    Returns:
        201 Created - Successfully generated forecast
        {
            "status": "success",
            "forecast": {
                "location": {...},
                "base_aqi": 61,
                "forecast_period_hours": 6,
                "predicted_values": [62, 64, 65, 65, 63, 60],
                "timestamps": ["2026-01-31T10:00:00", ...],
                "confidence": 0.87,
                "trend": "stable"
            },
            "timestamp": "2026-01-31T09:45:00"
        }

        400 Bad Request - Validation error
        {
            "status": "error",
            "error": "error message",
            "code": "VALIDATION_ERROR"
        }

        500 Internal Server Error - Server error
        {
            "status": "error",
            "error": "error message",
            "code": "FORECAST_ERROR"
        }
    """
    try:
        # Parse request JSON
        data = request.get_json()
        if data is None:
            return jsonify({
                "status": "error",
                "error": "Request body must be valid JSON",
                "code": "INVALID_JSON"
            }), 400

        # Validate location
        is_valid, error = _validate_location(data)
        if not is_valid:
            return jsonify({
                "status": "error",
                "error": error,
                "code": "VALIDATION_ERROR"
            }), 400

        # Validate AQI data
        is_valid, error = _validate_aqi_data(data)
        if not is_valid:
            return jsonify({
                "status": "error",
                "error": error,
                "code": "VALIDATION_ERROR"
            }), 400

        # Extract and validate optional parameters
        hours_ahead = data.get("hours_ahead", 6)
        try:
            hours_ahead = int(hours_ahead)
            if not (1 <= hours_ahead <= 24):
                return jsonify({
                    "status": "error",
                    "error": "Parameter 'hours_ahead' must be between 1 and 24",
                    "code": "VALIDATION_ERROR"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "error": "Parameter 'hours_ahead' must be an integer",
                "code": "VALIDATION_ERROR"
            }), 400

        include_confidence = data.get("include_confidence", True)

        # Prepare data for forecasting service
        location = data["location"]
        aqi_array = np.array(data["aqi_data"], dtype=float)

        # Generate forecast
        forecast_service = _get_forecast_service()
        forecast_result = forecast_service.generate_forecast(
            location_id=location.get("name", "Unknown"),
            days_ahead=hours_ahead / 24,
            historical_data=aqi_array
        )

        # Build response
        now = datetime.now()
        forecast_timestamps = [
            (now + timedelta(hours=i)).isoformat()
            for i in range(1, hours_ahead + 1)
        ]

        response = {
            "status": "success",
            "forecast": {
                "location": location,
                "base_aqi": float(aqi_array[-1]),
                "forecast_period_hours": hours_ahead,
                "predicted_values": forecast_result.get("forecast", []).tolist()
                    if isinstance(forecast_result.get("forecast"), np.ndarray)
                    else forecast_result.get("forecast", []),
                "timestamps": forecast_timestamps,
                "trend": forecast_result.get("trend", "stable"),
            },
            "timestamp": now.isoformat()
        }

        if include_confidence:
            response["forecast"]["confidence"] = forecast_result.get("confidence", 0.85)

        logger.info(f"Forecast generated for location: {location.get('name', 'Unknown')}")
        return jsonify(response), 201

    except ValidationError as e:
        logger.warning(f"Validation error in forecast endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "code": "VALIDATION_ERROR"
        }), 400

    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Failed to generate forecast. Please try again.",
            "code": "FORECAST_ERROR"
        }), 500


# ============================================================================
# ENDPOINT: POST /risk
# ============================================================================

@bp.route("/risk", methods=["POST"])
def assess_risk():
    """
    Assess health risk from forecasted AQI and user persona.

    Request JSON:
    {
        "aqi": 65,
        "persona": "Athletes",
        "forecast_trend": "rising" (optional),
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "name": "New York" (optional)
        }
    }

    Persona Options:
    - General Public
    - Children
    - Elderly
    - Outdoor Workers
    - Athletes
    - Sensitive Groups

    Returns:
        200 OK - Successfully assessed risk
        {
            "status": "success",
            "risk_assessment": {
                "aqi": 65,
                "persona": "Athletes",
                "risk_category": "Moderate",
                "risk_level": 2,
                "health_effects": [
                    "Exposure to air pollution for extended outdoor activities"
                ],
                "recommendations": {
                    "activity": "Reduce prolonged or heavy outdoor exertion",
                    "indoor_outdoor": "Enjoy outdoor activities, but increase time indoors",
                    "precautions": [
                        "Limit intense outdoor activities",
                        "Take more frequent breaks",
                        "Monitor symptoms"
                    ]
                },
                "symptoms_to_watch": [
                    "Coughing",
                    "Throat irritation",
                    "Shortness of breath"
                ]
            },
            "timestamp": "2026-01-31T09:45:00"
        }

        400 Bad Request - Validation error
        {
            "status": "error",
            "error": "error message",
            "code": "VALIDATION_ERROR"
        }

        500 Internal Server Error - Server error
        {
            "status": "error",
            "error": "error message",
            "code": "RISK_ERROR"
        }
    """
    try:
        # Parse request JSON
        data = request.get_json()
        if data is None:
            return jsonify({
                "status": "error",
                "error": "Request body must be valid JSON",
                "code": "INVALID_JSON"
            }), 400

        # Validate AQI value
        if "aqi" not in data:
            return jsonify({
                "status": "error",
                "error": "Missing required field: aqi",
                "code": "VALIDATION_ERROR"
            }), 400

        try:
            aqi = float(data["aqi"])
            if not (0 <= aqi <= 500):
                return jsonify({
                    "status": "error",
                    "error": "AQI value must be between 0 and 500",
                    "code": "VALIDATION_ERROR"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "error": "AQI value must be a valid number",
                "code": "VALIDATION_ERROR"
            }), 400

        # Validate persona
        if "persona" not in data:
            return jsonify({
                "status": "error",
                "error": "Missing required field: persona",
                "code": "VALIDATION_ERROR"
            }), 400

        is_valid, error, persona = _validate_persona(data["persona"])
        if not is_valid:
            return jsonify({
                "status": "error",
                "error": error,
                "code": "VALIDATION_ERROR"
            }), 400

        # Optional location validation
        location = data.get("location", {})
        if location:
            is_valid, error = _validate_location({"location": location})
            if not is_valid:
                return jsonify({
                    "status": "error",
                    "error": error,
                    "code": "VALIDATION_ERROR"
                }), 400

        # Assess risk
        health_classifier = _get_health_classifier()
        risk_assessment = health_classifier.assess_health_risk(aqi, persona)

        # Build response
        response = {
            "status": "success",
            "risk_assessment": {
                "aqi": aqi,
                "persona": data["persona"],
                "risk_category": risk_assessment.risk_category.value,
                "risk_level": risk_assessment.risk_level,
                "health_effects": risk_assessment.health_effects,
                "recommendations": {
                    "activity": risk_assessment.activity_recommendation,
                    "indoor_outdoor": risk_assessment.indoor_outdoor_recommendation,
                    "precautions": risk_assessment.precautions
                },
                "symptoms_to_watch": risk_assessment.symptoms_to_watch,
            },
            "timestamp": datetime.now().isoformat()
        }

        if location:
            response["risk_assessment"]["location"] = location

        logger.info(f"Risk assessment completed for AQI {aqi} and persona {data['persona']}")
        return jsonify(response), 200

    except ValidationError as e:
        logger.warning(f"Validation error in risk endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "code": "VALIDATION_ERROR"
        }), 400

    except Exception as e:
        logger.error(f"Error assessing risk: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Failed to assess risk. Please try again.",
            "code": "RISK_ERROR"
        }), 500


# ============================================================================
# ENDPOINT: POST /explain
# ============================================================================

@bp.route("/explain", methods=["POST"])
def explain():
    """
    Generate human-readable explanation for AQI forecast.

    Request JSON:
    {
        "forecast_metadata": {
            "forecast_values": [62, 64, 65, 65, 63, 60],
            "historical_values": [45, 50, 52, 55, 60, 58, 61],
            "trend": "stable",
            "confidence": 0.87
        },
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "name": "New York"
        },
        "style": "technical" (optional, default "casual"),
        "include_health_advisory": true (optional, default true)
    }

    Style Options:
    - technical: For professionals
    - casual: For general public
    - urgent: For alert/warning situations
    - reassuring: For good air quality

    Returns:
        200 OK - Successfully generated explanation
        {
            "status": "success",
            "explanation": {
                "summary": "Human-readable explanation...",
                "trend_description": "AQI is expected to remain stable...",
                "factors": [
                    {
                        "factor": "Weather patterns",
                        "impact": "Moderate",
                        "description": "Current wind patterns..."
                    }
                ],
                "health_advisory": {
                    "message": "General public should...",
                    "severity": "info",
                    "affected_groups": ["Children", "Elderly"],
                    "recommended_actions": [
                        "Reduce outdoor time",
                        "Use air purifiers"
                    ]
                }
            },
            "metadata": {
                "generated_at": "2026-01-31T09:45:00",
                "provider": "openai",
                "model": "gpt-3.5-turbo"
            },
            "timestamp": "2026-01-31T09:45:00"
        }

        400 Bad Request - Validation error
        {
            "status": "error",
            "error": "error message",
            "code": "VALIDATION_ERROR"
        }

        500 Internal Server Error - Server error
        {
            "status": "error",
            "error": "error message",
            "code": "EXPLANATION_ERROR"
        }
    """
    try:
        # Parse request JSON
        data = request.get_json()
        if data is None:
            return jsonify({
                "status": "error",
                "error": "Request body must be valid JSON",
                "code": "INVALID_JSON"
            }), 400

        # Validate forecast metadata
        if "forecast_metadata" not in data:
            return jsonify({
                "status": "error",
                "error": "Missing required field: forecast_metadata",
                "code": "VALIDATION_ERROR"
            }), 400

        forecast_metadata = data["forecast_metadata"]
        if not isinstance(forecast_metadata, dict):
            return jsonify({
                "status": "error",
                "error": "Field 'forecast_metadata' must be an object",
                "code": "VALIDATION_ERROR"
            }), 400

        # Validate location
        is_valid, error = _validate_location(data)
        if not is_valid:
            return jsonify({
                "status": "error",
                "error": error,
                "code": "VALIDATION_ERROR"
            }), 400

        # Validate forecast values
        if "forecast_values" not in forecast_metadata:
            return jsonify({
                "status": "error",
                "error": "forecast_metadata must contain 'forecast_values'",
                "code": "VALIDATION_ERROR"
            }), 400

        forecast_values = forecast_metadata["forecast_values"]
        if not isinstance(forecast_values, list) or len(forecast_values) == 0:
            return jsonify({
                "status": "error",
                "error": "Field 'forecast_values' must be a non-empty array",
                "code": "VALIDATION_ERROR"
            }), 400

        # Validate style (optional)
        style = data.get("style", "casual")
        valid_styles = [s.value for s in ExplanationStyle]
        if style not in valid_styles:
            return jsonify({
                "status": "error",
                "error": f"Invalid style. Must be one of: {', '.join(valid_styles)}",
                "code": "VALIDATION_ERROR"
            }), 400

        include_health_advisory = data.get("include_health_advisory", True)

        # Generate structured explanation using AQIExplainer
        explainability_engine = _get_explainability_engine()
        
        # Use historical values if provided, otherwise use forecast values
        historical_for_analysis = (
            forecast_metadata.get("historical_values", forecast_values)
            if forecast_metadata.get("historical_values") else forecast_values
        )
        
        structured_explanation = explainability_engine.explain(
            current_aqi=forecast_values[-1] if forecast_values else 50,
            aqi_history=historical_for_analysis
        )

        # Generate human-readable text using GenerativeExplainer
        generative_explainer = _get_generative_explainer()
        generated_explanation = generative_explainer.generate(
            structured_explanation=structured_explanation,
            style=ExplanationStyle(style),
            include_health_advisory=include_health_advisory
        )

        # Build response
        response = {
            "status": "success",
            "explanation": {
                "summary": generated_explanation.explanation,
                "trend_description": f"Trend: {structured_explanation.trend_analysis.trend.value}",
                "factors": [
                    {
                        "factor": factor.name,
                        "impact": factor.impact,
                        "description": factor.description
                    }
                    for factor in (
                        structured_explanation.factor_analysis.dominant_factors +
                        structured_explanation.factor_analysis.secondary_factors
                    )
                ],
                "duration": {
                    "classification": structured_explanation.duration_assessment.duration.value,
                    "expected_hours": structured_explanation.duration_assessment.expected_hours
                }
            },
            "metadata": {
                "generated_at": generated_explanation.generated_at.isoformat(),
                "provider": generated_explanation.provider_used.value,
                "model": generated_explanation.model_used,
                "tokens_used": generated_explanation.tokens_used,
            },
            "timestamp": datetime.now().isoformat()
        }

        if include_health_advisory:
            response["explanation"]["health_advisory"] = {
                "message": generated_explanation.health_advisory.message,
                "severity": generated_explanation.health_advisory.severity,
                "affected_groups": generated_explanation.health_advisory.affected_groups,
                "recommended_actions": generated_explanation.health_advisory.recommended_actions
            }

        logger.info(f"Explanation generated using {generated_explanation.provider_used.value}")
        return jsonify(response), 200

    except ValidationError as e:
        logger.warning(f"Validation error in explain endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "code": "VALIDATION_ERROR"
        }), 400

    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Failed to generate explanation. Please try again.",
            "code": "EXPLANATION_ERROR"
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({
        "status": "error",
        "error": "Bad request",
        "code": "BAD_REQUEST"
    }), 400


@bp.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({
        "status": "error",
        "error": "Endpoint not found",
        "code": "NOT_FOUND"
    }), 404


@bp.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "status": "error",
        "error": "Internal server error",
        "code": "INTERNAL_ERROR"
    }), 500
