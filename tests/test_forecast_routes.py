"""
Test Suite for Forecast Routes

Comprehensive tests for Flask REST API endpoints:
- POST /forecast
- POST /risk
- POST /explain
"""

import pytest
import json
from datetime import datetime, timedelta
import numpy as np


class TestForecastEndpoint:
    """Tests for POST /forecast endpoint."""

    def test_forecast_success(self, client):
        """Test successful forecast generation."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "name": "New York"
            },
            "aqi_data": [45, 50, 52, 55, 60, 58, 61],
            "hours_ahead": 6,
            "include_confidence": True
        }

        response = client.post("/api/v1/forecast", 
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "success"
        assert "forecast" in data
        assert data["forecast"]["location"]["name"] == "New York"
        assert data["forecast"]["base_aqi"] == 61.0
        assert data["forecast"]["forecast_period_hours"] == 6
        assert len(data["forecast"]["predicted_values"]) == 6
        assert "confidence" in data["forecast"]

    def test_forecast_missing_location(self, client):
        """Test forecast with missing location."""
        payload = {
            "aqi_data": [45, 50, 52, 55, 60, 58, 61]
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "location" in data["error"].lower()
        assert data["code"] == "VALIDATION_ERROR"

    def test_forecast_invalid_location_coordinates(self, client):
        """Test forecast with invalid latitude/longitude."""
        payload = {
            "location": {
                "latitude": 91,  # Invalid: > 90
                "longitude": -74.0060
            },
            "aqi_data": [45, 50, 52, 55, 60, 58, 61]
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert data["code"] == "VALIDATION_ERROR"

    def test_forecast_missing_aqi_data(self, client):
        """Test forecast with missing AQI data."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "aqi_data" in data["error"].lower()

    def test_forecast_insufficient_aqi_data(self, client):
        """Test forecast with insufficient historical AQI data."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "aqi_data": [45, 50]  # Only 2 values, need 3+
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_forecast_aqi_out_of_range(self, client):
        """Test forecast with AQI values out of valid range."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "aqi_data": [45, 50, 600]  # 600 > 500
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_forecast_invalid_hours_ahead(self, client):
        """Test forecast with invalid hours_ahead parameter."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "aqi_data": [45, 50, 52, 55, 60, 58, 61],
            "hours_ahead": 48  # Max is 24
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert "hours_ahead" in data["error"].lower()

    def test_forecast_hours_ahead_zero(self, client):
        """Test forecast with zero hours_ahead."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "aqi_data": [45, 50, 52, 55, 60, 58, 61],
            "hours_ahead": 0
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400

    def test_forecast_invalid_json(self, client):
        """Test forecast with invalid JSON."""
        response = client.post("/api/v1/forecast",
                             data="invalid json",
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert "JSON" in data["error"]

    def test_forecast_default_parameters(self, client):
        """Test forecast with default optional parameters."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "aqi_data": [45, 50, 52, 55, 60, 58, 61]
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 201
        data = response.get_json()
        assert data["forecast"]["forecast_period_hours"] == 6  # Default
        assert "confidence" in data["forecast"]  # Default True

    def test_forecast_response_contains_timestamps(self, client):
        """Test that forecast response includes hourly timestamps."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "aqi_data": [45, 50, 52, 55, 60, 58, 61],
            "hours_ahead": 3
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 201
        data = response.get_json()
        assert len(data["forecast"]["timestamps"]) == 3


class TestRiskEndpoint:
    """Tests for POST /risk endpoint."""

    def test_risk_assessment_success(self, client):
        """Test successful risk assessment."""
        payload = {
            "aqi": 65,
            "persona": "Athletes",
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "name": "New York"
            }
        }

        response = client.post("/api/v1/risk",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "risk_assessment" in data
        assert data["risk_assessment"]["aqi"] == 65
        assert data["risk_assessment"]["persona"] == "Athletes"
        assert "risk_category" in data["risk_assessment"]
        assert "recommendations" in data["risk_assessment"]

    def test_risk_missing_aqi(self, client):
        """Test risk assessment with missing AQI."""
        payload = {
            "persona": "Athletes"
        }

        response = client.post("/api/v1/risk",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "aqi" in data["error"].lower()

    def test_risk_missing_persona(self, client):
        """Test risk assessment with missing persona."""
        payload = {
            "aqi": 65
        }

        response = client.post("/api/v1/risk",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "persona" in data["error"].lower()

    def test_risk_invalid_aqi_value(self, client):
        """Test risk assessment with invalid AQI value."""
        payload = {
            "aqi": 550,  # > 500
            "persona": "Athletes"
        }

        response = client.post("/api/v1/risk",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_risk_negative_aqi(self, client):
        """Test risk assessment with negative AQI."""
        payload = {
            "aqi": -10,
            "persona": "Athletes"
        }

        response = client.post("/api/v1/risk",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400

    def test_risk_invalid_persona(self, client):
        """Test risk assessment with invalid persona."""
        payload = {
            "aqi": 65,
            "persona": "Invalid Persona"
        }

        response = client.post("/api/v1/risk",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_risk_all_valid_personas(self, client):
        """Test risk assessment with all valid personas."""
        personas = [
            "General Public",
            "Children",
            "Elderly",
            "Outdoor Workers",
            "Athletes",
            "Sensitive Groups"
        ]

        for persona in personas:
            payload = {
                "aqi": 65,
                "persona": persona
            }

            response = client.post("/api/v1/risk",
                                 json=payload,
                                 content_type="application/json")

            assert response.status_code == 200
            data = response.get_json()
            assert data["risk_assessment"]["persona"] == persona

    def test_risk_response_includes_health_effects(self, client):
        """Test that risk response includes health effects and recommendations."""
        payload = {
            "aqi": 150,  # Unhealthy
            "persona": "Children"
        }

        response = client.post("/api/v1/risk",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 200
        data = response.get_json()
        assert "health_effects" in data["risk_assessment"]
        assert "precautions" in data["risk_assessment"]["recommendations"]
        assert "symptoms_to_watch" in data["risk_assessment"]

    def test_risk_with_location_optional(self, client):
        """Test that location is optional in risk assessment."""
        payload = {
            "aqi": 65,
            "persona": "Athletes"
        }

        response = client.post("/api/v1/risk",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 200
        data = response.get_json()
        # Location should not be in response if not provided
        assert "location" not in data["risk_assessment"] or data["risk_assessment"]["location"] == {}


class TestExplainEndpoint:
    """Tests for POST /explain endpoint."""

    def test_explain_success(self, client):
        """Test successful explanation generation."""
        payload = {
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
            "style": "casual",
            "include_health_advisory": True
        }

        response = client.post("/api/v1/explain",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "explanation" in data
        assert "summary" in data["explanation"]
        assert "health_advisory" in data["explanation"]
        assert "metadata" in data

    def test_explain_missing_forecast_metadata(self, client):
        """Test explain with missing forecast_metadata."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }

        response = client.post("/api/v1/explain",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_explain_missing_location(self, client):
        """Test explain with missing location."""
        payload = {
            "forecast_metadata": {
                "forecast_values": [62, 64, 65, 65, 63, 60]
            }
        }

        response = client.post("/api/v1/explain",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_explain_empty_forecast_values(self, client):
        """Test explain with empty forecast_values."""
        payload = {
            "forecast_metadata": {
                "forecast_values": []
            },
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }

        response = client.post("/api/v1/explain",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400

    def test_explain_invalid_style(self, client):
        """Test explain with invalid style."""
        payload = {
            "forecast_metadata": {
                "forecast_values": [62, 64, 65]
            },
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "style": "invalid_style"
        }

        response = client.post("/api/v1/explain",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400

    def test_explain_valid_styles(self, client):
        """Test explain with all valid styles."""
        styles = ["technical", "casual", "urgent", "reassuring"]

        for style in styles:
            payload = {
                "forecast_metadata": {
                    "forecast_values": [62, 64, 65]
                },
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "style": style
            }

            response = client.post("/api/v1/explain",
                                 json=payload,
                                 content_type="application/json")

            assert response.status_code == 200

    def test_explain_response_includes_factors(self, client):
        """Test that explain response includes factor analysis."""
        payload = {
            "forecast_metadata": {
                "forecast_values": [62, 64, 65, 65, 63, 60],
                "historical_values": [45, 50, 52, 55, 60, 58, 61],
                "trend": "rising",
                "confidence": 0.87
            },
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }

        response = client.post("/api/v1/explain",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 200
        data = response.get_json()
        assert "factors" in data["explanation"]

    def test_explain_default_style(self, client):
        """Test explain with default style (casual)."""
        payload = {
            "forecast_metadata": {
                "forecast_values": [62, 64, 65]
            },
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }

        response = client.post("/api/v1/explain",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 200

    def test_explain_without_health_advisory(self, client):
        """Test explain with include_health_advisory=False."""
        payload = {
            "forecast_metadata": {
                "forecast_values": [62, 64, 65]
            },
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "include_health_advisory": False
        }

        response = client.post("/api/v1/explain",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 200
        data = response.get_json()
        assert "health_advisory" not in data["explanation"]

    def test_explain_invalid_location_coordinates(self, client):
        """Test explain with invalid location coordinates."""
        payload = {
            "forecast_metadata": {
                "forecast_values": [62, 64, 65]
            },
            "location": {
                "latitude": 181,  # Invalid
                "longitude": -74.0060
            }
        }

        response = client.post("/api/v1/explain",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_malformed_json(self, client):
        """Test endpoint with malformed JSON."""
        response = client.post("/api/v1/forecast",
                             data="{invalid json}",
                             content_type="application/json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"

    def test_missing_content_type(self, client):
        """Test request without JSON content type."""
        response = client.post("/api/v1/risk",
                             data='{"aqi": 65, "persona": "Athletes"}')

        # Should fail or be handled gracefully
        assert response.status_code in [400, 415]

    def test_very_large_aqi_array(self, client):
        """Test forecast with maximum allowed AQI data points."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "aqi_data": list(range(1, 366))  # 365 points
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 201

    def test_exceeds_max_aqi_array(self, client):
        """Test forecast exceeding maximum AQI data points."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "aqi_data": list(range(1, 367))  # 366 points (over limit)
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 400

    def test_aqi_string_instead_of_number(self, client):
        """Test with AQI values as strings instead of numbers."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "aqi_data": ["45", "50", "52"]  # Strings instead of numbers
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        # Should either accept and convert or reject
        assert response.status_code in [201, 400]

    def test_float_latitude_longitude(self, client):
        """Test with float lat/lon values."""
        payload = {
            "location": {
                "latitude": 40.712776,
                "longitude": -74.005974
            },
            "aqi_data": [45, 50, 52, 55, 60]
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 201

    def test_boundary_aqi_values(self, client):
        """Test with boundary AQI values."""
        payload = {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "aqi_data": [0, 250, 500]  # Min, mid, max
        }

        response = client.post("/api/v1/forecast",
                             json=payload,
                             content_type="application/json")

        assert response.status_code == 201

    def test_boundary_lat_lon(self, client):
        """Test with boundary lat/lon values."""
        test_cases = [
            {"lat": 90, "lon": 180},      # NE corner
            {"lat": -90, "lon": -180},    # SW corner
            {"lat": 0, "lon": 0},         # Center
            {"lat": 45, "lon": -74},      # Mid-range
        ]

        for case in test_cases:
            payload = {
                "location": {
                    "latitude": case["lat"],
                    "longitude": case["lon"]
                },
                "aqi_data": [45, 50, 52, 55, 60]
            }

            response = client.post("/api/v1/forecast",
                                 json=payload,
                                 content_type="application/json")

            assert response.status_code == 201
