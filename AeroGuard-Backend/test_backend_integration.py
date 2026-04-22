import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

# ANSI Color Codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
YELLOW = "\033[93m"
CYAN = "\033[96m"

# Test Trackers
passed_tests = 0
failed_tests = 0

def print_success(msg: str):
    global passed_tests
    print(f"{GREEN}✔ SUCCESS:{RESET} {msg}")
    passed_tests += 1

def print_failure(msg: str):
    global failed_tests
    print(f"{RED}✖ FAILED:{RESET} {msg}")
    failed_tests += 1

def test_health_risk(client: httpx.Client):
    print(f"\n{CYAN}--- Test 1: Health Risk Logic ---{RESET}")
    url = f"{BASE_URL}/api/v1/health-risk/"
    params = {"aqi": 145, "persona": "Children / Elderly"}
    
    try:
        # Added timeout=30.0 to handle ML artifact cold-loading
        response = client.get(url, params=params, timeout=30.0)
        if response.status_code == 200:
            data = response.json()
            if "risk_category" in data and "actionable_advice" in data:
                print_success(f"Endpoint returned 200 OK. Risk Category identified as: {data['risk_category']}")
            else:
                print_failure(f"Response missing required fields. Got: {data}")
        else:
            print_failure(f"Expected 200 OK, got {response.status_code}. Response: {response.text}")
    except Exception as e:
        print_failure(f"Connection Error: {e}")

def test_ml_forecasting(client: httpx.Client):
    print(f"\n{CYAN}--- Test 2: ML Forecasting Ensemble ---{RESET}")
    url = f"{BASE_URL}/api/v1/forecast/"
    
    # Create a dummy payload matching ForecastRequest schema (a 2D list of floats).
    # Shape logic depends on your specific model, assuming 24 timesteps by 15 features here.
    dummy_features = [[0.5] * 15 for _ in range(24)] 
    payload = {"features": dummy_features}
    
    try:
        # Increased timeout to 90.0 to handle massive ensemble cold-start loading
        response = client.post(url, json=payload, timeout=90.0)
        if response.status_code == 200:
            data = response.json()
            if "forecasts" in data and "components" in data:
                print_success("Endpoint returned 200 OK. Extracted multi-pollutant forecasts and nested components.")
            else:
                print_failure(f"Response missing 'forecasts' or 'components'. Got: {data}")
        elif response.status_code == 503:
            print_failure(f"Endpoint returned 503 Service Unavailable. (Ensure ML artifacts are placed in app/ml/artifacts/). Response: {response.text}")
        else:
            print_failure(f"Expected 200 OK, got {response.status_code}. Response: {response.text}")
    except Exception as e:
        print_failure(f"Connection Error: {e}")

def test_waqi_realtime(client: httpx.Client):
    print(f"\n{CYAN}--- Test 3: WAQI Realtime Service ---{RESET}")
    # Corrected target URL to point to the specific city endpoint defined in realtime.py
    # Targeted absolute URL: prefix '/api/v1/realtime-aqi' + route '/city/{city_name}'
    url = f"{BASE_URL}/api/v1/realtime-aqi/city/Mumbai"
    
    try:
        response = client.get(url, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and "data" in data:
                print_success("Endpoint returned 200 OK. Successfully fetched and parsed external WAQI data.")
            else:
                print_failure(f"Unexpected response structure. Got: {data}")
        else:
            print_failure(f"Expected 200 OK, got {response.status_code}. Response: {response.text}")
    except Exception as e:
        print_failure(f"Connection Error: {e}")

def test_ai_briefing(client: httpx.Client):
    print(f"\n{CYAN}--- Test 4: AI Explainability - Briefing ---{RESET}")
    url = f"{BASE_URL}/api/v1/ai/briefing"
    params = {"city": "Mumbai", "persona": "Outdoor Workers / Athletes"}
    
    try:
        # Increase timeout because generative AI models can take a few seconds
        response = client.get(url, params=params, timeout=20.0) 
        if response.status_code == 200:
            data = response.json()
            if "briefing" in data and "advice" in data:
                print_success("Endpoint returned 200 OK. Generated human-readable briefing and advice.")
            else:
                print_failure(f"Response missing required fields. Got: {data}")
        else:
            print_failure(f"Expected 200 OK, got {response.status_code}. Response: {response.text}")
    except Exception as e:
        print_failure(f"Connection Error: {e}")

def test_ai_forecast_explanation(client: httpx.Client):
    print(f"\n{CYAN}--- Test 5: AI Explainability - Forecast ---{RESET}")
    url = f"{BASE_URL}/api/v1/ai/explain-forecast"
    payload = {
        "aqi_value": 120,
        "trend": "rising",
        "factors": ["High Traffic", "Temperature Inversion"]
    }
    
    try:
        response = client.post(url, json=payload, timeout=20.0)
        if response.status_code == 200:
            data = response.json()
            if "explanation" in data:
                print_success("Endpoint returned 200 OK. Generated scientific forecast explanation.")
            else:
                print_failure(f"Response missing required field. Got: {data}")
        else:
            print_failure(f"Expected 200 OK, got {response.status_code}. Response: {response.text}")
    except Exception as e:
        print_failure(f"Connection Error: {e}")

def main():
    print(f"{YELLOW}=============================================={RESET}")
    print(f"{YELLOW}    AeroGuard Backend Integration Tests       {RESET}")
    print(f"{YELLOW}=============================================={RESET}")
    
    # Verify the backend server is actually running before executing the suite
    try:
        with httpx.Client() as client:
            client.get(f"{BASE_URL}/")
    except httpx.ConnectError:
        print(f"\n{RED}CRITICAL ERROR: Could not connect to {BASE_URL}.{RESET}")
        print(f"Please ensure you have started the FastAPI server (e.g., using 'uvicorn app.main:app --reload').\n")
        sys.exit(1)
        
    # Execute the Test Suite synchronously
    with httpx.Client() as client:
        test_health_risk(client)
        test_ml_forecasting(client)
        test_waqi_realtime(client)
        test_ai_briefing(client)
        test_ai_forecast_explanation(client)
        
    # Print the Final Summary
    print(f"\n{YELLOW}=============================================={RESET}")
    print(f"               Test Summary                   ")
    print(f"=============================================={RESET}")
    print(f"{GREEN}Passed: {passed_tests}{RESET}")
    print(f"{RED}Failed: {failed_tests}{RESET}")
    
    if failed_tests == 0:
        print(f"\n{GREEN}All core systems are operational!{RESET}")
    else:
        print(f"\n{RED}Some tests failed. Please review the errors above.{RESET}")
        
    print(f"{YELLOW}=============================================={RESET}\n")

if __name__ == "__main__":
    main()
