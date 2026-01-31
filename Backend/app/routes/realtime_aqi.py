"""
Real-time AQI API Routes

Endpoints for fetching real-time air quality data from India.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

from app.services.realtime_aqi_service import (
    RealtimeAQIService,
    POPULAR_INDIAN_CITIES,
)

logger = logging.getLogger(__name__)

bp = Blueprint("realtime_aqi", __name__, url_prefix="/api/v1/realtime-aqi")
aqi_service = RealtimeAQIService()


@bp.route("/city/<city_name>", methods=["GET"])
def get_city_aqi(city_name):
    """
    Get real-time AQI data for a specific city.

    Args:
        city_name: Name of the city (e.g., 'Delhi', 'Mumbai')

    Returns:
        JSON with AQI data and pollutant details
    """
    try:
        if not city_name or len(city_name.strip()) == 0:
            return jsonify({
                "status": "error",
                "message": "City name cannot be empty",
            }), 400

        aqi_data = aqi_service.get_city_aqi(city_name)

        if not aqi_data:
            return jsonify({
                "status": "error",
                "message": f"Could not fetch AQI data for {city_name}",
            }), 404

        # Add category based on AQI value
        aqi_data['category'] = aqi_service.get_aqi_category(aqi_data.get('aqi'))
        aqi_data['timestamp'] = datetime.now().isoformat()

        return jsonify({
            "status": "success",
            "data": aqi_data,
        }), 200

    except Exception as e:
        logger.error(f"Error fetching AQI for {city_name}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch AQI data: {str(e)}",
        }), 500


@bp.route("/coordinates", methods=["GET"])
def get_aqi_by_coordinates():
    """
    Get real-time AQI data for a specific location by coordinates.

    Query Parameters:
        latitude: Location latitude (required)
        longitude: Location longitude (required)

    Returns:
        JSON with AQI data for the nearest monitoring station
    """
    try:
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')

        if not latitude or not longitude:
            return jsonify({
                "status": "error",
                "message": "latitude and longitude parameters are required",
            }), 400

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "latitude and longitude must be valid numbers",
            }), 400

        aqi_data = aqi_service.get_city_by_coordinates(latitude, longitude)

        if not aqi_data:
            return jsonify({
                "status": "error",
                "message": f"Could not fetch AQI data for coordinates ({latitude}, {longitude})",
            }), 404

        # Add category based on AQI value
        aqi_data['category'] = aqi_service.get_aqi_category(aqi_data.get('aqi'))
        aqi_data['timestamp'] = datetime.now().isoformat()

        return jsonify({
            "status": "success",
            "data": aqi_data,
        }), 200

    except Exception as e:
        logger.error(f"Error fetching AQI by coordinates: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch AQI data: {str(e)}",
        }), 500


@bp.route("/multiple-cities", methods=["POST"])
def get_multiple_cities():
    """
    Get real-time AQI data for multiple cities.

    Request Body (JSON):
        {
            "cities": ["Delhi", "Mumbai", "Bangalore", ...]
        }

    Returns:
        JSON with AQI data for all requested cities
    """
    try:
        data = request.get_json()

        if not data or 'cities' not in data:
            return jsonify({
                "status": "error",
                "message": "Request body must contain 'cities' array",
            }), 400

        cities = data.get('cities', [])

        if not isinstance(cities, list) or len(cities) == 0:
            return jsonify({
                "status": "error",
                "message": "cities must be a non-empty array",
            }), 400

        if len(cities) > 50:
            return jsonify({
                "status": "error",
                "message": "Maximum 50 cities allowed per request",
            }), 400

        aqi_results = aqi_service.get_multiple_cities_aqi(cities)

        # Process results
        processed_results = {}
        for city, aqi_data in aqi_results.items():
            if aqi_data:
                aqi_data['category'] = aqi_service.get_aqi_category(aqi_data.get('aqi'))
            processed_results[city] = aqi_data

        return jsonify({
            "status": "success",
            "data": processed_results,
            "timestamp": datetime.now().isoformat(),
        }), 200

    except Exception as e:
        logger.error(f"Error fetching multiple cities AQI: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch AQI data: {str(e)}",
        }), 500


@bp.route("/popular-cities", methods=["GET"])
def get_popular_cities_aqi():
    """
    Get real-time AQI data for popular Indian cities.

    Returns:
        JSON with AQI data for popular cities in India
    """
    try:
        aqi_results = aqi_service.get_multiple_cities_aqi(POPULAR_INDIAN_CITIES)

        # Process results
        processed_results = {}
        for city, aqi_data in aqi_results.items():
            if aqi_data:
                aqi_data['category'] = aqi_service.get_aqi_category(aqi_data.get('aqi'))
            processed_results[city] = aqi_data

        return jsonify({
            "status": "success",
            "data": processed_results,
            "timestamp": datetime.now().isoformat(),
        }), 200

    except Exception as e:
        logger.error(f"Error fetching popular cities AQI: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch AQI data: {str(e)}",
        }), 500


@bp.route("/health", methods=["GET"])
def health_check():
    """Check if real-time AQI service is operational."""
    return jsonify({
        "status": "operational" if aqi_service.api_key else "not_configured",
        "service": "Real-time AQI",
        "timestamp": datetime.now().isoformat(),
    }), 200
