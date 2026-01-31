"""
Test suite for model comparison REST API endpoints.

Tests all endpoints of the model comparison service including:
- POST /api/v1/models/compare
- POST /api/v1/models/quick-compare
- GET /api/v1/models/available-models
- GET /api/v1/models/comparison-info
- GET /api/v1/models/health
"""

import pytest
import pandas as pd
import numpy as np
import json
from datetime import datetime

from app import create_app
from app.config import Config


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


@pytest.fixture
def app():
    """Create and configure test app"""
    app = create_app(TestConfig)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_data():
    """Create sample time-series data"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='h')
    
    # Create synthetic air quality data
    pm25 = 50 + np.sin(np.arange(200) * 0.1) * 10 + np.random.normal(0, 2, 200)
    pm10 = 70 + np.sin(np.arange(200) * 0.1) * 15 + np.random.normal(0, 3, 200)
    
    return {
        "data": [
            list(row) for row in zip(dates.strftime('%Y-%m-%d %H:%M'), pm25, pm10)
        ],
        "columns": ["date", "PM2.5", "PM10"]
    }


class TestCompareEndpoint:
    """Tests for POST /api/v1/models/compare endpoint"""
    
    def test_compare_success(self, client, sample_data):
        """Test successful model comparison"""
        payload = {
            **sample_data,
            "target_col": "PM2.5",
            "forecast_steps": 6,
            "test_size": 0.2,
            "models": ["SARIMA", "XGBoost"]
        }
        
        response = client.post('/api/v1/models/compare', json=payload)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'best_model' in data['data']
        assert 'metrics' in data['data']
        assert 'predictions' in data['data']
        assert 'test_actual' in data['data']
        
    def test_compare_missing_data(self, client):
        """Test comparison with missing data field"""
        payload = {
            "columns": ["date", "PM2.5"],
            "target_col": "PM2.5"
        }
        
        response = client.post('/api/v1/models/compare', json=payload)
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'data' in data['message'].lower()
    
    def test_compare_missing_columns(self, client, sample_data):
        """Test comparison with missing columns field"""
        payload = {
            "data": sample_data['data'],
            "target_col": "PM2.5"
        }
        
        response = client.post('/api/v1/models/compare', json=payload)
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'columns' in data['message'].lower()
    
    def test_compare_invalid_target_col(self, client, sample_data):
        """Test comparison with invalid target column"""
        payload = {
            **sample_data,
            "target_col": "NonExistent"
        }
        
        response = client.post('/api/v1/models/compare', json=payload)
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'target' in data['message'].lower() or 'column' in data['message'].lower()
    
    def test_compare_empty_request(self, client):
        """Test comparison with empty request"""
        response = client.post('/api/v1/models/compare', json={})
        assert response.status_code == 400
    
    def test_compare_single_model(self, client, sample_data):
        """Test comparison with single model"""
        payload = {
            **sample_data,
            "target_col": "PM2.5",
            "models": ["SARIMA"]
        }
        
        response = client.post('/api/v1/models/compare', json=payload)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['best_model'] == "SARIMA"
    
    def test_compare_custom_forecast_steps(self, client, sample_data):
        """Test comparison with custom forecast steps"""
        payload = {
            **sample_data,
            "target_col": "PM2.5",
            "forecast_steps": 12
        }
        
        response = client.post('/api/v1/models/compare', json=payload)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        # Check forecast length matches requested steps
        for model_forecast in data['data']['predictions'].values():
            assert len(model_forecast) == 12
    
    def test_compare_metrics_accuracy(self, client, sample_data):
        """Test that metrics are calculated correctly"""
        payload = {
            **sample_data,
            "target_col": "PM2.5"
        }
        
        response = client.post('/api/v1/models/compare', json=payload)
        assert response.status_code == 200
        
        data = response.get_json()
        metrics = data['data']['metrics']
        
        # Check all models have MAE and RMSE
        for model, model_metrics in metrics.items():
            assert 'MAE' in model_metrics
            assert 'RMSE' in model_metrics
            assert model_metrics['MAE'] > 0
            assert model_metrics['RMSE'] > 0
            assert model_metrics['RMSE'] >= model_metrics['MAE']  # RMSE >= MAE


class TestQuickCompareEndpoint:
    """Tests for POST /api/v1/models/quick-compare endpoint"""
    
    def test_quick_compare_success(self, client, sample_data):
        """Test successful quick comparison"""
        payload = {
            "data": sample_data['data'],
            "target_col": "PM2.5"
        }
        
        response = client.post('/api/v1/models/quick-compare', json=payload)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'best_model' in data['data']
        assert 'metrics' in data['data']
        assert 'winner_forecast' in data['data']
    
    def test_quick_compare_dict_data(self, client):
        """Test quick comparison with dict data"""
        payload = {
            "data": {
                "PM2.5": [45, 46, 47, 48, 49, 50] * 20,
                "PM10": [60, 62, 64, 66, 68, 70] * 20
            },
            "target_col": "PM2.5"
        }
        
        response = client.post('/api/v1/models/quick-compare', json=payload)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
    
    def test_quick_compare_missing_data(self, client):
        """Test quick comparison without data"""
        payload = {"target_col": "PM2.5"}
        
        response = client.post('/api/v1/models/quick-compare', json=payload)
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['status'] == 'error'


class TestAvailableModelsEndpoint:
    """Tests for GET /api/v1/models/available-models endpoint"""
    
    def test_available_models_success(self, client):
        """Test getting available models"""
        response = client.get('/api/v1/models/available-models')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'available_models' in data['data']
        assert len(data['data']['available_models']) > 0
    
    def test_available_models_structure(self, client):
        """Test available models response structure"""
        response = client.get('/api/v1/models/available-models')
        data = response.get_json()
        
        models = data['data']['available_models']
        
        # Check required fields for each model
        for model in models:
            assert 'name' in model
            assert 'type' in model
            assert 'description' in model
            assert 'best_for' in model
    
    def test_available_models_content(self, client):
        """Test that SARIMA and XGBoost are available"""
        response = client.get('/api/v1/models/available-models')
        data = response.get_json()
        
        model_names = [m['name'] for m in data['data']['available_models']]
        assert 'SARIMA' in model_names
        assert 'XGBoost' in model_names


class TestComparisonInfoEndpoint:
    """Tests for GET /api/v1/models/comparison-info endpoint"""
    
    def test_comparison_info_success(self, client):
        """Test getting comparison service info"""
        response = client.get('/api/v1/models/comparison-info')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'service_name' in data['data']
        assert 'version' in data['data']
        assert 'metrics_supported' in data['data']
        assert 'endpoints' in data['data']
    
    def test_comparison_info_endpoints(self, client):
        """Test that endpoints are documented"""
        response = client.get('/api/v1/models/comparison-info')
        data = response.get_json()
        
        endpoints = data['data']['endpoints']
        assert len(endpoints) > 0
        
        # Check structure of endpoints
        for endpoint in endpoints:
            assert 'method' in endpoint
            assert 'path' in endpoint
            assert 'description' in endpoint


class TestHealthEndpoint:
    """Tests for GET /api/v1/models/health endpoint"""
    
    def test_health_check_success(self, client):
        """Test health check endpoint"""
        response = client.get('/api/v1/models/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'service' in data
        assert data['service'] == 'model_comparison'
        assert 'available_models' in data
    
    def test_health_check_timestamp(self, client):
        """Test that health check includes timestamp"""
        response = client.get('/api/v1/models/health')
        data = response.get_json()
        
        assert 'timestamp' in data
        # Verify timestamp format is ISO 8601
        timestamp = data['timestamp']
        datetime.fromisoformat(timestamp)  # Will raise if invalid


class TestResponseFormat:
    """Tests for response format consistency"""
    
    def test_success_response_format(self, client, sample_data):
        """Test that success responses follow consistent format"""
        payload = {
            **sample_data,
            "target_col": "PM2.5"
        }
        
        response = client.post('/api/v1/models/compare', json=payload)
        data = response.get_json()
        
        # Check response structure
        assert 'status' in data
        assert 'timestamp' in data
        assert 'data' in data
        
        # Check timestamp format
        datetime.fromisoformat(data['timestamp'])
    
    def test_error_response_format(self, client):
        """Test that error responses follow consistent format"""
        response = client.post('/api/v1/models/compare', json={})
        data = response.get_json()
        
        # Check error structure
        assert 'status' in data
        assert data['status'] == 'error'
        assert 'message' in data
        assert 'code' in data


class TestDataValidation:
    """Tests for request data validation"""
    
    def test_non_numeric_data(self, client):
        """Test handling of non-numeric data in target column"""
        payload = {
            "data": [["2024-01-01", "invalid", "70"], ["2024-01-02", "data", "72"]],
            "columns": ["date", "PM2.5", "PM10"],
            "target_col": "PM2.5"
        }
        
        response = client.post('/api/v1/models/compare', json=payload)
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_insufficient_data(self, client):
        """Test handling of insufficient data"""
        payload = {
            "data": [["2024-01-01", "45", "60"]],  # Only 1 sample
            "columns": ["date", "PM2.5", "PM10"],
            "target_col": "PM2.5"
        }
        
        response = client.post('/api/v1/models/compare', json=payload)
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['status'] == 'error'


class TestIntegration:
    """Integration tests for model comparison API"""
    
    def test_full_workflow(self, client, sample_data):
        """Test complete workflow from data to results"""
        # 1. Check service health
        health_response = client.get('/api/v1/models/health')
        assert health_response.status_code == 200
        
        # 2. Get available models
        models_response = client.get('/api/v1/models/available-models')
        assert models_response.status_code == 200
        
        # 3. Run comparison
        compare_payload = {
            **sample_data,
            "target_col": "PM2.5",
            "models": ["SARIMA", "XGBoost"]
        }
        
        compare_response = client.post('/api/v1/models/compare', json=compare_payload)
        assert compare_response.status_code == 200
        
        data = compare_response.get_json()
        assert data['status'] == 'success'
        assert data['data']['best_model'] in ["SARIMA", "XGBoost"]
    
    def test_multiple_targets(self, client, sample_data):
        """Test comparison across multiple target columns"""
        for target in ["PM2.5", "PM10"]:
            payload = {
                **sample_data,
                "target_col": target
            }
            
            response = client.post('/api/v1/models/compare', json=payload)
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['status'] == 'success'
            assert 'best_model' in data['data']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
