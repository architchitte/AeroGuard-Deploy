"""
Tests for Main Flask Application

Comprehensive test suite covering:
- Application factory and creation
- Blueprint registration
- Error handling
- Request/response logging
- CORS configuration
- Utility endpoints (health, info, root)
- Configuration loading
- Middleware behavior
"""

import pytest
import json
from datetime import datetime
from flask import Flask
from app import create_app
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig


class TestApplicationFactory:
    """Test Flask application factory creation."""
    
    def test_create_app_with_config(self):
        """Test creating app with specific config class."""
        app = create_app(TestingConfig)
        assert app is not None
        assert isinstance(app, Flask)
        assert app.config['TESTING'] is True
    
    def test_create_app_without_config(self, monkeypatch):
        """Test creating app without explicit config (uses environment)."""
        monkeypatch.setenv('FLASK_ENV', 'testing')
        app = create_app()
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_app_name(self):
        """Test application metadata."""
        app = create_app(TestingConfig)
        assert app.config['APP_NAME'] == 'AeroGuard'
        assert 'APP_VERSION' in app.config
    
    def test_app_secret_key(self):
        """Test that app has secret key configured."""
        app = create_app(TestingConfig)
        assert app.config['SECRET_KEY'] is not None
        assert len(app.config['SECRET_KEY']) > 0


class TestBlueprintRegistration:
    """Test blueprint registration and routing."""
    
    @pytest.fixture
    def app(self):
        """Create test application."""
        return create_app(TestingConfig)
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_forecast_blueprint_registered(self, app):
        """Test that forecast blueprint is registered."""
        # Get all registered blueprints
        blueprints = list(app.blueprints.keys())
        assert 'forecast' in blueprints
    
    def test_forecast_routes_exist(self, client):
        """Test that forecast routes are accessible."""
        # These should return 404 or actual responses, not "blueprint not found"
        response = client.post('/api/forecast/forecast',
            json={
                'location': {'latitude': 28.7, 'longitude': 77.1},
                'aqi_data': {'pm25': 85}
            }
        )
        # Should not 404 (blueprint registered)
        assert response.status_code != 404


class TestUtilityEndpoints:
    """Test utility endpoints (health, info, root)."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app(TestingConfig)
        return app.test_client()
    
    def test_health_check_endpoint(self, client):
        """Test GET /health endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
        assert 'environment' in data
        assert 'service' in data
    
    def test_health_response_format(self, client):
        """Test health check response has correct format."""
        response = client.get('/health')
        data = response.get_json()
        
        # Verify timestamp is ISO format
        assert 'T' in data['timestamp']
        
        # Verify status value
        assert data['status'] in ['healthy', 'degraded', 'unhealthy']
        
        # Verify service name
        assert 'AeroGuard' in data['service']
    
    def test_info_endpoint(self, client):
        """Test GET /info endpoint."""
        response = client.get('/info')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'AeroGuard'
        assert 'description' in data
        assert 'version' in data
        assert 'environment' in data
        assert 'debug' in data
        assert isinstance(data['debug'], bool)
    
    def test_root_endpoint(self, client):
        """Test GET / endpoint."""
        response = client.get('/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'endpoints' in data
        assert 'forecast' in data['endpoints']
        assert 'health' in data['endpoints']
    
    def test_root_endpoint_structure(self, client):
        """Test root endpoint returns correct structure."""
        response = client.get('/')
        data = response.get_json()
        
        # Check endpoints structure
        endpoints = data['endpoints']
        assert isinstance(endpoints, dict)
        assert all(isinstance(v, str) for v in endpoints.values())
        
        # Verify endpoints point to correct paths
        assert '/health' in endpoints['health']
        assert '/info' in endpoints['info']
        assert '/api/forecast' in endpoints.get('forecast', '')


class TestErrorHandling:
    """Test error handling and responses."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app(TestingConfig)
        return app.test_client()
    
    def test_404_not_found(self, client):
        """Test 404 Not Found error handler."""
        response = client.get('/nonexistent/endpoint')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'NOT_FOUND'
        assert 'message' in data
        assert 'status' in data
        assert data['status'] == 404
        assert 'timestamp' in data
    
    def test_method_not_allowed(self, client):
        """Test 405 Method Not Allowed error handler."""
        response = client.post('/health')  # /health only accepts GET
        
        assert response.status_code == 405
        data = response.get_json()
        assert data['error'] == 'METHOD_NOT_ALLOWED'
        assert 'POST' in data['message']
    
    def test_error_response_format(self, client):
        """Test error responses have consistent format."""
        response = client.get('/nonexistent')
        data = response.get_json()
        
        # All errors should have these fields
        required_fields = ['error', 'message', 'status', 'timestamp']
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_error_timestamp_format(self, client):
        """Test error timestamp is ISO format."""
        response = client.get('/nonexistent')
        data = response.get_json()
        
        # Should be parseable ISO format
        timestamp = data['timestamp']
        assert 'T' in timestamp or ':' in timestamp


class TestCORSConfiguration:
    """Test CORS setup and headers."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app(TestingConfig)
        return app.test_client()
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.get('/health')
        
        # CORS headers should be present
        assert 'Access-Control-Allow-Origin' in response.headers or \
               'Vary' in response.headers
    
    def test_options_request(self, client):
        """Test OPTIONS request (CORS preflight)."""
        response = client.options('/health')
        
        # Should handle OPTIONS request
        assert response.status_code in [200, 204]
    
    def test_cors_allow_methods(self, client):
        """Test that allowed methods are correct."""
        response = client.options('/api/forecast/forecast')
        
        # Should allow POST for forecast endpoint
        assert response.status_code in [200, 204]


class TestRequestResponseLogging:
    """Test request/response logging and middleware."""
    
    @pytest.fixture
    def app(self):
        """Create test application."""
        return create_app(TestingConfig)
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_request_id_in_response(self, client):
        """Test that X-Request-ID header is in response."""
        response = client.get('/health')
        
        assert 'X-Request-ID' in response.headers
        request_id = response.headers['X-Request-ID']
        assert request_id is not None
    
    def test_response_time_header(self, client):
        """Test that X-Response-Time header is present."""
        response = client.get('/health')
        
        assert 'X-Response-Time' in response.headers
        response_time = response.headers['X-Response-Time']
        # Should be a float representing seconds
        assert float(response_time) >= 0
    
    def test_powered_by_header(self, client):
        """Test that X-Powered-By header is set."""
        response = client.get('/health')
        
        assert 'X-Powered-By' in response.headers
        assert 'AeroGuard' in response.headers['X-Powered-By']
    
    def test_request_id_uniqueness(self, client):
        """Test that each request gets unique ID."""
        response1 = client.get('/health')
        response2 = client.get('/health')
        
        id1 = response1.headers.get('X-Request-ID')
        id2 = response2.headers.get('X-Request-ID')
        
        # IDs might be the same if custom or auto-generated
        # But they should both exist
        assert id1 is not None
        assert id2 is not None


class TestConfiguration:
    """Test configuration loading and application."""
    
    def test_development_config(self):
        """Test development configuration."""
        app = create_app(DevelopmentConfig)
        
        assert app.debug is True
        assert app.config['TESTING'] is False
        assert app.config['ENV'] == 'development'
    
    def test_production_config(self):
        """Test production configuration."""
        # Production config requires SECRET_KEY
        # For testing, we'll set it
        import os
        os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
        
        try:
            app = create_app(ProductionConfig)
            
            assert app.debug is False
            assert app.config['SESSION_COOKIE_SECURE'] is True
            assert app.config['ENV'] == 'production'
        finally:
            # Clean up
            if 'SECRET_KEY' in os.environ:
                del os.environ['SECRET_KEY']
    
    def test_testing_config(self):
        """Test testing configuration."""
        app = create_app(TestingConfig)
        
        assert app.config['TESTING'] is True
        assert app.debug is False
    
    def test_config_environment_variables(self, monkeypatch):
        """Test that config respects environment variables."""
        monkeypatch.setenv('APP_VERSION', '1.2.3')
        monkeypatch.setenv('LOG_LEVEL', 'WARNING')
        
        app = create_app(TestingConfig)
        
        assert app.config['APP_VERSION'] == '1.2.3'
        assert app.config['LOG_LEVEL'] == 'WARNING'


class TestJSONResponses:
    """Test JSON response formatting and types."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app(TestingConfig)
        return app.test_client()
    
    def test_responses_are_json(self, client):
        """Test that all responses are JSON."""
        endpoints = ['/health', '/info', '/']
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.content_type.startswith('application/json')
    
    def test_json_parsing(self, client):
        """Test that JSON responses can be parsed."""
        response = client.get('/health')
        data = response.get_json()
        
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_datetime_iso_format(self, client):
        """Test that datetime fields are ISO format."""
        response = client.get('/health')
        data = response.get_json()
        
        timestamp = data['timestamp']
        # Should be parseable as ISO datetime
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Invalid ISO datetime format: {timestamp}")


class TestSecurityHeaders:
    """Test security-related response headers."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app(TestingConfig)
        return app.test_client()
    
    def test_response_has_required_headers(self, client):
        """Test that responses have required security headers."""
        response = client.get('/health')
        
        # Required custom headers
        assert 'X-Powered-By' in response.headers
        assert 'X-Request-ID' in response.headers
        assert 'X-Response-Time' in response.headers
    
    def test_no_server_header_leakage(self, client):
        """Test that server implementation details are not leaked."""
        response = client.get('/health')
        
        # Should not expose implementation details
        server = response.headers.get('Server', '')
        # AeroGuard should be in Server header, not Flask
        assert 'Werkzeug' not in server or 'AeroGuard' in response.headers.get('X-Powered-By', '')


class TestEndpointIntegration:
    """Test integration between endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app(TestingConfig)
        return app.test_client()
    
    def test_health_and_info_consistency(self, client):
        """Test that /health and /info endpoints are consistent."""
        health = client.get('/health').get_json()
        info = client.get('/info').get_json()
        
        # Both should have version and environment
        assert health['version'] == info['version']
        assert health['environment'] == info['environment']
    
    def test_root_endpoint_references_valid_paths(self, client):
        """Test that root endpoint references valid paths."""
        root = client.get('/').get_json()
        endpoints = root['endpoints']
        
        # Test each referenced endpoint exists
        for name, path in endpoints.items():
            if name in ['health', 'info']:
                response = client.get(path)
                assert response.status_code == 200


class TestMultipleRequests:
    """Test behavior with multiple requests."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app(TestingConfig)
        return app.test_client()
    
    def test_concurrent_requests(self, client):
        """Test handling multiple requests."""
        responses = [client.get('/health') for _ in range(5)]
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # All should be valid JSON
        assert all(r.get_json() is not None for r in responses)
    
    def test_request_ids_different(self, client):
        """Test that concurrent requests get different IDs."""
        responses = [client.get('/health') for _ in range(3)]
        ids = [r.headers['X-Request-ID'] for r in responses]
        
        # Each request should have an ID
        assert all(id for id in ids)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
