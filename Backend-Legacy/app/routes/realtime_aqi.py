"""
Real-time AQI API Routes

Endpoints for fetching real-time air quality data from India.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging
import os

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


@bp.route("/history/<city_name>", methods=["GET"])
def get_city_history(city_name):
    """Get historical AQI data for a city."""
    try:
        days = int(request.args.get('days', 7))
        
        # For Mumbai, we can serve some data from our CSV
        if city_name.lower() == 'mumbai':
            import pandas as pd
            csv_path = 'India-Air-Quality-Dataset/Mumbai_AQI_Dataset.csv'
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
                df = df.sort_values('Date', ascending=False).head(days)
                
                history = []
                for _, row in df.iterrows():
                    history.append({
                        "date": row['Date'].strftime('%Y-%m-%d'),
                        "aqi": int(row['AQI']),
                        "pm25": float(row['PM2.5']),
                        "pm10": float(row['PM10']),
                        "no2": float(row['NO2']),
                        "o3": float(row['O3'])
                    })
                return jsonify({
                    "status": "success",
                    "city": "Mumbai",
                    "data": history[::-1] # Return in chronological order
                }), 200

        # Fallback: Mock data for other cities
        import random
        from datetime import timedelta
        history = []
        now = datetime.now()
        for i in range(days, 0, -1):
            date = now - timedelta(days=i)
            history.append({
                "date": date.strftime('%Y-%m-%d'),
                "aqi": random.randint(50, 200),
                "pm25": random.randint(30, 150),
                "pm10": random.randint(50, 250),
                "no2": random.randint(10, 60),
                "o3": random.randint(5, 40)
            })
            
        return jsonify({
            "status": "success",
            "city": city_name,
            "data": history
        }), 200

    except Exception as e:
        logger.error(f"Error fetching history for {city_name}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@bp.route("/health", methods=["GET"])
def health_check():
    """Check if real-time AQI service is operational."""
    return jsonify({
        "status": "operational" if aqi_service.api_key else "not_configured",
        "service": "Real-time AQI",
        "timestamp": datetime.now().isoformat(),
    }), 200

@bp.route("/tiles/<int:z>/<int:x>/<int:y>.png", methods=["GET"])
def proxy_waqi_tiles(z, x, y):
    """
    Backend proxy for WAQI tiles to avoid exposing API key to the frontend.
    Includes basic caching and attribution requirements.
    """
    if not aqi_service.api_key:
        return jsonify({"status": "error", "message": "WAQI API key not configured"}), 500

    import requests
    from flask import Response
    
    try:
        url = f"https://tiles.waqi.info/tiles/usepa-aqi/{z}/{x}/{y}.png?token={aqi_service.api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Forward the image with appropriate headers
            res = Response(response.content, mimetype='image/png')
            res.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
            res.headers['X-Attribution'] = 'World Air Quality Index Project'
            return res
        else:
            return jsonify({"status": "error", "message": "Failed to fetch tile"}), response.status_code
            
    except Exception as e:
        logger.error(f"Tile proxy error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route("/nationwide", methods=["GET"])
def get_nationwide_aqi():
    """
    Get nationwide AQI points for heatmap visualization with supplementation for major cities.
    """
    try:
        points = aqi_service.get_supplemented_nationwide_data()

        return jsonify({
            "status": "success",
            "count": len(points),
            "data": points,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Nationwide AQI fetch failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
CITY_COORDS = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
}

@bp.route("/search", methods=["GET"])
def search_location():
    """
    Proxy location search to Nominatim to avoid CORS issues.
    """
    query = request.args.get('q')
    if not query:
        return jsonify({"status": "error", "message": "Query parameter 'q' is required"}), 400
    
    import requests
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "limit": 5,
            "countrycodes": "in",
            "bounded": 1,
            "viewbox": "68.7,37.1,97.25,6.5"
        }
        headers = {
            "User-Agent": "AeroGuard/1.0"
        }
        response = requests.get(url, params=params, headers=headers)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Location search proxy failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500