"""
API Testing Script

Test all AeroGuard endpoints with various scenarios.
"""

import requests
import json
import numpy as np
from typing import Dict, Any

BASE_URL = "http://localhost:5000/api/v1"
HEADERS = {"Content-Type": "application/json"}


class TestColors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"


def print_test(test_name: str, success: bool, message: str = ""):
    """Print test result."""
    status = f"{TestColors.GREEN}✓ PASS{TestColors.END}" if success else f"{TestColors.RED}✗ FAIL{TestColors.END}"
    print(f"{status} {test_name}")
    if message:
        print(f"     {message}")


def test_health_endpoints():
    """Test health check endpoints."""
    print(f"\n{TestColors.BLUE}=== Health Check Endpoints ==={TestColors.END}")
    
    try:
        # Test /health
        response = requests.get(f"{BASE_URL}/health")
        success = response.status_code == 200
        print_test("GET /health", success, f"Status: {response.status_code}")
        
        # Test /health/ready
        response = requests.get(f"{BASE_URL}/health/ready")
        success = response.status_code == 200
        print_test("GET /health/ready", success, f"Status: {response.status_code}")
        
        # Test /health/live
        response = requests.get(f"{BASE_URL}/health/live")
        success = response.status_code == 200
        print_test("GET /health/live", success, f"Status: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print(f"{TestColors.RED}✗ Cannot connect to server at {BASE_URL}{TestColors.END}")
        return False
    
    return True


def test_forecast_endpoints():
    """Test forecasting endpoints."""
    print(f"\n{TestColors.BLUE}=== Forecast Endpoints ==={TestColors.END}")
    
    # Test POST forecast
    payload = {
        "location_id": "test_mumbai",
        "days_ahead": 7
    }
    response = requests.post(f"{BASE_URL}/forecast", json=payload, headers=HEADERS)
    success = response.status_code == 200
    print_test("POST /forecast", success, f"Status: {response.status_code}")
    
    # Test GET forecast for location
    response = requests.get(f"{BASE_URL}/forecast/test_mumbai?days_ahead=5")
    success = response.status_code == 200
    print_test("GET /forecast/<location_id>", success, f"Status: {response.status_code}")
    
    # Test GET current conditions
    response = requests.get(f"{BASE_URL}/forecast/test_mumbai/current")
    success = response.status_code == 200
    print_test("GET /forecast/<location_id>/current", success, f"Status: {response.status_code}")


def test_model_endpoints():
    """Test model management endpoints."""
    print(f"\n{TestColors.BLUE}=== Model Management Endpoints ==={TestColors.END}")
    
    # Test GET model status
    response = requests.get(f"{BASE_URL}/model/status")
    success = response.status_code == 200
    print_test("GET /model/status", success, f"Status: {response.status_code}")
    
    # Generate sample training data
    np.random.seed(42)
    n_samples = 50
    n_features = 10
    X = np.random.normal(50, 20, (n_samples, n_features)).tolist()
    y = {
        "pm25": np.random.uniform(10, 100, n_samples).tolist(),
        "pm10": np.random.uniform(20, 150, n_samples).tolist(),
    }
    
    # Test POST train
    payload = {
        "X": X,
        "y": y,
        "model_type": "ensemble"
    }
    response = requests.post(f"{BASE_URL}/model/train", json=payload, headers=HEADERS)
    success = response.status_code == 200
    print_test("POST /model/train", success, f"Status: {response.status_code}")
    
    if success:
        # Test GET feature importance
        response = requests.get(f"{BASE_URL}/model/pm25/feature-importance")
        success = response.status_code == 200
        print_test("GET /model/<parameter>/feature-importance", success, f"Status: {response.status_code}")


def test_error_handling():
    """Test error handling."""
    print(f"\n{TestColors.BLUE}=== Error Handling ==={TestColors.END}")
    
    # Test invalid location_id
    payload = {"location_id": "", "days_ahead": 7}
    response = requests.post(f"{BASE_URL}/forecast", json=payload, headers=HEADERS)
    success = response.status_code == 400
    print_test("Invalid location_id", success, f"Status: {response.status_code} (Expected: 400)")
    
    # Test invalid days_ahead
    payload = {"location_id": "test", "days_ahead": 100}
    response = requests.post(f"{BASE_URL}/forecast", json=payload, headers=HEADERS)
    success = response.status_code == 400
    print_test("Invalid days_ahead (>30)", success, f"Status: {response.status_code} (Expected: 400)")
    
    # Test 404 not found
    response = requests.get(f"{BASE_URL}/invalid/endpoint")
    success = response.status_code == 404
    print_test("Invalid endpoint (404)", success, f"Status: {response.status_code} (Expected: 404)")


def test_response_format():
    """Test response format consistency."""
    print(f"\n{TestColors.BLUE}=== Response Format Validation ==={TestColors.END}")
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        has_status = "status" in data
        has_timestamp = "timestamp" in data
        success = has_status and has_timestamp
        print_test("Response contains required fields", success, f"Fields: status={has_status}, timestamp={has_timestamp}")


def run_all_tests():
    """Run all tests."""
    print(f"\n{TestColors.YELLOW}{'='*60}")
    print("AeroGuard API Test Suite")
    print(f"{'='*60}{TestColors.END}")
    
    # Check server connectivity
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"\n{TestColors.RED}✗ Cannot connect to {BASE_URL}")
        print("Make sure the server is running: python run.py{TestColors.END}\n")
        return
    
    # Run test suites
    test_health_endpoints()
    test_forecast_endpoints()
    test_model_endpoints()
    test_error_handling()
    test_response_format()
    
    print(f"\n{TestColors.YELLOW}{'='*60}")
    print("Test Suite Complete!")
    print(f"{'='*60}{TestColors.END}\n")


if __name__ == "__main__":
    run_all_tests()
