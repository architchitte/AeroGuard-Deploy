"""
Application Constants

Centralized constants to avoid magic numbers and improve maintainability.
"""


class AQIThresholds:
    """AQI threshold values for categorization."""
    GOOD = 50
    MODERATE = 100
    UNHEALTHY_SENSITIVE = 150
    UNHEALTHY = 200
    VERY_UNHEALTHY = 300
    HAZARDOUS = 301


class AQICategories:
    """AQI category names."""
    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"


class ForecastLimits:
    """Forecast configuration limits."""
    MIN_DAYS = 1
    MAX_DAYS = 30
    DEFAULT_DAYS = 7
    MIN_HOURS = 1
    MAX_HOURS = 168  # 7 days
    DEFAULT_HOURS = 6


class PollutantUnits:
    """Units for air quality parameters."""
    PM25 = "µg/m³"
    PM10 = "µg/m³"
    NO2 = "ppb"
    O3 = "ppb"
    SO2 = "ppb"
    CO = "ppm"
    AQI = "index"


class HTTPStatus:
    """HTTP status codes."""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class CacheTimeout:
    """Cache timeout values in seconds."""
    SHORT = 300  # 5 minutes
    MEDIUM = 1800  # 30 minutes
    LONG = 3600  # 1 hour
    VERY_LONG = 86400  # 24 hours


def get_aqi_category(aqi_value: float) -> str:
    """
    Get AQI category based on value.
    
    Args:
        aqi_value: AQI numeric value
        
    Returns:
        Category name string
    """
    if aqi_value <= AQIThresholds.GOOD:
        return AQICategories.GOOD
    elif aqi_value <= AQIThresholds.MODERATE:
        return AQICategories.MODERATE
    elif aqi_value <= AQIThresholds.UNHEALTHY_SENSITIVE:
        return AQICategories.UNHEALTHY_SENSITIVE
    elif aqi_value <= AQIThresholds.UNHEALTHY:
        return AQICategories.UNHEALTHY
    elif aqi_value <= AQIThresholds.VERY_UNHEALTHY:
        return AQICategories.VERY_UNHEALTHY
    else:
        return AQICategories.HAZARDOUS
