"""
Forecast Routes

Endpoints for air quality forecasting.
"""

from flask import Blueprint, request, jsonify, current_app
from app.models.forecast_model import ForecastModel
from app.services.forecasting_service import ForecastingService
from app.services.data_service import DataService
from app.utils.validators import InputValidator
from app.utils.error_handlers import ValidationError

bp = Blueprint("forecast", __name__, url_prefix="/api/v1/forecast")

# Initialize services
_model = None
_forecast_service = None
_data_service = None


def _get_services():
    """Get or initialize services."""
    global _model, _forecast_service, _data_service

    if _forecast_service is None:
        _model = ForecastModel(model_type="ensemble")
        _forecast_service = ForecastingService(_model)
        _data_service = DataService()

    return _forecast_service, _data_service


@bp.route("", methods=["GET", "POST"])
def generate_forecast():
    """
    Generate air quality forecast.

    Request JSON:
        {
            "location_id": "string",
            "days_ahead": "int (1-30, default 7)",
            "include_current": "bool (default true)"
        }

    Returns:
        JSON with forecast predictions
    """
    try:
        data = request.get_json()

        # Validate request
        is_valid, error_msg = InputValidator.validate_forecast_request(data)
        if not is_valid:
            raise ValidationError(error_msg)

        location_id = data.get("location_id")
        days_ahead = int(data.get("days_ahead", 7))

        # Validate location
        is_valid, msg = DataService().validate_location(location_id)
        if not is_valid:
            raise ValidationError(msg)

        # Get services
        forecast_service, data_service = _get_services()

        # Fetch historical data
        historical_data = data_service.fetch_historical_data(location_id, days=30)

        # Generate forecast
        forecast_result = forecast_service.generate_forecast(
            location_id=location_id,
            days_ahead=days_ahead,
            historical_data=historical_data,
        )

        return jsonify(forecast_result), 200

    except ValidationError as e:
        return jsonify(
            {"status": "error", "message": e.message, "code": 400}
        ), 400
    except Exception as e:
        return jsonify(
            {"status": "error", "message": str(e), "code": 500}
        ), 500


@bp.route("/<location_id>", methods=["GET"])
def get_forecast_for_location(location_id: str):
    """
    Get forecast for a specific location.

    Args:
        location_id: Location identifier

    Query Parameters:
        days_ahead: Number of days to forecast (default: 7)

    Returns:
        JSON with forecast data
    """
    try:
        days_ahead = request.args.get("days_ahead", 7, type=int)

        # Validate inputs
        is_valid, error_msg = InputValidator.validate_location_id(location_id)
        if not is_valid:
            raise ValidationError(error_msg)

        is_valid, error_msg = InputValidator.validate_days_ahead(days_ahead)
        if not is_valid:
            raise ValidationError(error_msg)

        # Get services
        forecast_service, data_service = _get_services()

        # Validate location
        is_valid, msg = data_service.validate_location(location_id)
        if not is_valid:
            raise ValidationError(msg)

        # Fetch data and generate forecast
        historical_data = data_service.fetch_historical_data(
            location_id, days=30
        )
        forecast_result = forecast_service.generate_forecast(
            location_id=location_id,
            days_ahead=days_ahead,
            historical_data=historical_data,
        )

        return jsonify(forecast_result), 200

    except ValidationError as e:
        return jsonify(
            {"status": "error", "message": e.message, "code": 400}
        ), 400
    except Exception as e:
        return jsonify(
            {"status": "error", "message": str(e), "code": 500}
        ), 500


@bp.route("/<location_id>/current", methods=["GET"])
def get_current_conditions(location_id: str):
    """
    Get current air quality conditions.

    Args:
        location_id: Location identifier

    Returns:
        JSON with current conditions
    """
    try:
        is_valid, error_msg = InputValidator.validate_location_id(location_id)
        if not is_valid:
            raise ValidationError(error_msg)

        _, data_service = _get_services()

        # Validate location
        is_valid, msg = data_service.validate_location(location_id)
        if not is_valid:
            raise ValidationError(msg)

        # Fetch current conditions
        conditions = data_service.fetch_current_conditions(location_id)

        return jsonify(
            {
                "status": "success",
                "data": conditions,
            }
        ), 200

    except ValidationError as e:
        return jsonify(
            {"status": "error", "message": e.message, "code": 400}
        ), 400
    except Exception as e:
        return jsonify(
            {"status": "error", "message": str(e), "code": 500}
        ), 500

@bp.route("/<location_id>/6h", methods=["GET"])
def get_6h_forecast(location_id: str):
    """
    Get 6-hour AQI forecast for a specific location using hybrid ensemble model.

    Returns:
        JSON with hourly AQI predictions for next 6 hours
    """
    try:
        # Validate and sanitize location id
        is_valid, error_msg = InputValidator.validate_location_id(location_id)
        if not is_valid:
            raise ValidationError(error_msg)
        
        location_id = InputValidator.sanitize_string(location_id, max_length=50)

        # Try to use hybrid model first
        try:
            from app.services.hybrid_forecast_service import get_hybrid_forecast_service
            
            hybrid_service = get_hybrid_forecast_service()
            
            # Get current AQI if available
            try:
                from app.services.realtime_aqi_service import RealtimeAQIService
                aqi_service = RealtimeAQIService()
                
                # Use coordinates if provided for best anchoring
                lat = request.args.get("latitude", type=float)
                lon = request.args.get("longitude", type=float)
                
                if lat is not None and lon is not None:
                    aqi_data = aqi_service.get_city_by_coordinates(lat, lon)
                else:
                    aqi_data = aqi_service.get_city_aqi(location_id)
                
                current_aqi = aqi_data.get('aqi') if aqi_data else None
            except:
                current_aqi = None
            
            # Generate hybrid forecast
            forecast_result = hybrid_service.generate_6h_forecast(
                location=location_id,
                current_aqi=current_aqi
            )
            
            return jsonify(forecast_result), 200
            
        except Exception as hybrid_error:
            current_app.logger.warning(f"Hybrid model failed, falling back to ensemble: {hybrid_error}")
            
            # Fallback to original ensemble method
            forecast_service, data_service = _get_services()

            # Validate location exists
            is_valid, msg = data_service.validate_location(location_id)
            if not is_valid:
                raise ValidationError(msg)

            # Fetch short historical window (last 48h is enough)
            historical_data = data_service.fetch_historical_data(
                location_id, days=2
            )

            # Call original 6H forecast method
            forecast_result = forecast_service.generate_6h_forecast(
                location_id=location_id,
                historical_data=historical_data,
            )

            return jsonify(forecast_result), 200

    except ValidationError as e:
        return jsonify(
            {"status": "error", "message": e.message, "code": 400}
        ), 400
    except Exception as e:
        current_app.logger.exception("6H forecast failed")
        return jsonify(
            {"status": "error", "message": str(e), "code": 500}
        ), 500
