# Main Flask App - Examples

Complete working examples for using the AeroGuard Flask API.

## Table of Contents
1. [Basic Setup](#basic-setup)
2. [Health Checks](#health-checks)
3. [API Root](#api-root)
4. [Forecast Endpoint](#forecast-endpoint)
5. [Risk Assessment](#risk-assessment)
6. [Explanations](#explanations)
7. [Error Handling](#error-handling)
8. [Advanced Patterns](#advanced-patterns)

---

## Basic Setup

### Start the Server

```bash
cd Backend
python run.py
```

Output:
```
[2026-01-31 10:30:00] INFO in app: AeroGuard Flask application created (env: development)
 * Running on http://127.0.0.1:5000
```

### Verify Server is Running

```bash
curl http://localhost:5000/health
```

---

## Health Checks

### Example 1: Basic Health Check

```bash
curl http://localhost:5000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-31T10:30:45.123456",
  "version": "1.0.0",
  "environment": "development",
  "service": "AeroGuard API"
}
```

### Example 2: Health Check in Monitoring

```bash
#!/bin/bash
# health_monitor.sh

HEALTH_ENDPOINT="http://localhost:5000/health"
MAX_RETRIES=3
RETRY_DELAY=5

check_health() {
    response=$(curl -s "$HEALTH_ENDPOINT")
    status=$(echo "$response" | jq -r '.status')
    
    if [ "$status" = "healthy" ]; then
        echo "✓ Service is healthy"
        return 0
    else
        echo "✗ Service is unhealthy"
        return 1
    fi
}

# Retry logic
for i in $(seq 1 $MAX_RETRIES); do
    if check_health; then
        exit 0
    fi
    
    if [ $i -lt $MAX_RETRIES ]; then
        echo "Retry in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
    fi
done

echo "Health check failed after $MAX_RETRIES attempts"
exit 1
```

### Example 3: Health Check with Python

```python
import requests
import json

def check_aeroguard_health():
    """Check AeroGuard API health status."""
    url = "http://localhost:5000/health"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"Status: {data['status']}")
        print(f"Version: {data['version']}")
        print(f"Environment: {data['environment']}")
        print(f"Timestamp: {data['timestamp']}")
        
        return data['status'] == 'healthy'
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    is_healthy = check_aeroguard_health()
    exit(0 if is_healthy else 1)
```

---

## API Root

### Example 1: Get API Information

```bash
curl http://localhost:5000/
```

**Response (200 OK):**
```json
{
  "message": "Welcome to AeroGuard API",
  "description": "Air Quality Prediction & Explainability System",
  "endpoints": {
    "health": "/health",
    "info": "/info",
    "forecast": "/api/forecast/forecast",
    "risk": "/api/forecast/risk",
    "explain": "/api/forecast/explain"
  },
  "documentation": "See docs/ folder for complete API documentation",
  "timestamp": "2026-01-31T10:30:45.123456"
}
```

### Example 2: Get App Info

```bash
curl http://localhost:5000/info
```

**Response (200 OK):**
```json
{
  "name": "AeroGuard",
  "description": "Air Quality Prediction & Explainability System",
  "version": "1.0.0",
  "environment": "production",
  "debug": false,
  "timestamp": "2026-01-31T10:30:45.123456"
}
```

---

## Forecast Endpoint

### Example 1: Basic Forecast Request

```bash
curl -X POST http://localhost:5000/api/forecast/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "location": {
      "latitude": 28.7041,
      "longitude": 77.1025,
      "city": "Delhi"
    },
    "aqi_data": {
      "pm25": 85,
      "pm10": 150,
      "no2": 45,
      "o3": 35,
      "so2": 20,
      "co": 1200
    }
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "timestamp": "2026-01-31T10:30:45.123456",
  "request_id": "abc123def456",
  "location": {
    "latitude": 28.7041,
    "longitude": 77.1025,
    "city": "Delhi"
  },
  "forecast": {
    "aqi": 142,
    "category": "Poor",
    "timestamp": "2026-01-31T10:30:45.123456",
    "horizon_hours": 6,
    "prediction_interval": 0.95,
    "confidence": 0.88
  }
}
```

### Example 2: Forecast with Python

```python
import requests
import json

def get_forecast(latitude, longitude, aqi_data, city=None):
    """
    Get AQI forecast for a location.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        aqi_data: Dict with pm25, pm10, no2, o3, so2, co values
        city: Optional city name
        
    Returns:
        Forecast dict or None on error
    """
    url = "http://localhost:5000/api/forecast/forecast"
    
    payload = {
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "aqi_data": aqi_data
    }
    
    if city:
        payload["location"]["city"] = city
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        forecast = data.get('forecast', {})
        
        print(f"AQI: {forecast.get('aqi')}")
        print(f"Category: {forecast.get('category')}")
        print(f"Confidence: {forecast.get('confidence'):.1%}")
        
        return forecast
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Usage
aqi_data = {
    "pm25": 85,
    "pm10": 150,
    "no2": 45,
    "o3": 35,
    "so2": 20,
    "co": 1200
}

forecast = get_forecast(28.7041, 77.1025, aqi_data, city="Delhi")
```

### Example 3: Forecast with JavaScript

```javascript
// forecast.js

async function getAeroGuardForecast(location, aqiData) {
    const url = 'http://localhost:5000/api/forecast/forecast';
    
    const payload = {
        location: location,
        aqi_data: aqiData
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        return data.forecast;
        
    } catch (error) {
        console.error('Forecast error:', error);
        return null;
    }
}

// Usage
const location = {
    latitude: 28.7041,
    longitude: 77.1025,
    city: 'Delhi'
};

const aqiData = {
    pm25: 85,
    pm10: 150,
    no2: 45,
    o3: 35,
    so2: 20,
    co: 1200
};

getAeroGuardForecast(location, aqiData).then(forecast => {
    if (forecast) {
        console.log(`AQI: ${forecast.aqi}`);
        console.log(`Category: ${forecast.category}`);
    }
});
```

---

## Risk Assessment

### Example 1: Health Risk Assessment

```bash
curl -X POST http://localhost:5000/api/forecast/risk \
  -H "Content-Type: application/json" \
  -d '{
    "aqi": 142,
    "location": {
      "latitude": 28.7041,
      "longitude": 77.1025
    },
    "persona": "elderly",
    "duration_hours": 24
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "timestamp": "2026-01-31T10:30:45.123456",
  "risk_assessment": {
    "persona": "elderly",
    "aqi": 142,
    "risk_level": "high",
    "health_impacts": [
      "Respiratory disease exacerbation",
      "Cardiovascular symptoms",
      "Reduced lung function"
    ],
    "recommendations": [
      "Stay indoors in air-conditioned environments",
      "Use N95 masks if going outside",
      "Increase medication intake if prescribed",
      "Avoid strenuous outdoor activities"
    ],
    "duration_hours": 24
  }
}
```

### Example 2: Risk Assessment for All Personas

```python
import requests

def get_all_personas_risk(aqi, location):
    """Get risk assessment for all personas."""
    personas = [
        'general_public',
        'children',
        'elderly',
        'pregnant_women',
        'athletes',
        'asthma_patients'
    ]
    
    url = "http://localhost:5000/api/forecast/risk"
    
    results = {}
    
    for persona in personas:
        payload = {
            "aqi": aqi,
            "location": location,
            "persona": persona
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            results[persona] = data.get('risk_assessment', {})
            
        except requests.exceptions.RequestException as e:
            print(f"Error for {persona}: {e}")
    
    return results

# Usage
location = {"latitude": 28.7041, "longitude": 77.1025}
aqi = 142

all_risks = get_all_personas_risk(aqi, location)

for persona, risk in all_risks.items():
    print(f"\n{persona.upper()}")
    print(f"  Risk Level: {risk.get('risk_level')}")
    print(f"  Recommendations:")
    for rec in risk.get('recommendations', []):
        print(f"    - {rec}")
```

---

## Explanations

### Example 1: Get AI Explanation

```bash
curl -X POST http://localhost:5000/api/forecast/explain \
  -H "Content-Type: application/json" \
  -d '{
    "aqi": 142,
    "location": {
      "latitude": 28.7041,
      "longitude": 77.1025
    },
    "style": "detailed",
    "include_recommendations": true
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "timestamp": "2026-01-31T10:30:45.123456",
  "explanation": {
    "style": "detailed",
    "text": "The AQI of 142 indicates Poor air quality. This level results primarily from elevated PM2.5 concentrations (85 μg/m³) and PM10 levels (150 μg/m³). The combination of these particulates with nitrogen dioxide (45 ppb) creates hazardous conditions, especially for vulnerable populations...",
    "summary": "Poor air quality with high particulate matter",
    "contributing_factors": [
      {
        "pollutant": "PM2.5",
        "level": 85,
        "contribution": 0.45,
        "source": "vehicles, industrial"
      },
      {
        "pollutant": "PM10",
        "level": 150,
        "contribution": 0.35,
        "source": "dust, construction"
      }
    ],
    "recommendations": [
      "Use air purifiers indoors",
      "Limit outdoor activities",
      "Wear N95 masks if outside",
      "Monitor health symptoms"
    ]
  }
}
```

### Example 2: Explanation with Generative AI

```bash
curl -X POST http://localhost:5000/api/forecast/explain \
  -H "Content-Type: application/json" \
  -d '{
    "aqi": 142,
    "location": {
      "latitude": 28.7041,
      "longitude": 77.1025,
      "city": "Delhi"
    },
    "style": "generative",
    "include_context": true
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "timestamp": "2026-01-31T10:30:45.123456",
  "explanation": {
    "style": "generative",
    "text": "In Delhi today, the air quality is Poor with an AQI of 142. Particulate matter from vehicle emissions and construction activities has accumulated in the atmosphere. You should consider these precautions: stay indoors in air-conditioned spaces, reduce physical exertion, and use appropriate masks when venturing outside. Children and elderly residents should be extra cautious...",
    "generated_by": "GPT-based explanainer",
    "context": {
      "city": "Delhi",
      "time_of_day": "morning",
      "weather": "calm winds, temperature inversion"
    }
  }
}
```

---

## Error Handling

### Example 1: Invalid Location

```bash
curl -X POST http://localhost:5000/api/forecast/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "location": {},
    "aqi_data": {"pm25": 85}
  }'
```

**Response (400 Bad Request):**
```json
{
  "error": "INVALID_LOCATION",
  "message": "Location must include 'latitude' and 'longitude'",
  "status": 400,
  "timestamp": "2026-01-31T10:30:45.123456"
}
```

### Example 2: Missing Required Fields

```bash
curl -X POST http://localhost:5000/api/forecast/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "location": {"latitude": 28.7, "longitude": 77.1}
  }'
```

**Response (400 Bad Request):**
```json
{
  "error": "INVALID_REQUEST",
  "message": "Missing required field: 'aqi_data'",
  "status": 400,
  "timestamp": "2026-01-31T10:30:45.123456"
}
```

### Example 3: Invalid HTTP Method

```bash
curl -X GET http://localhost:5000/api/forecast/forecast
```

**Response (405 Method Not Allowed):**
```json
{
  "error": "METHOD_NOT_ALLOWED",
  "message": "The GET method is not allowed for this resource",
  "status": 405,
  "timestamp": "2026-01-31T10:30:45.123456"
}
```

### Example 4: Not Found

```bash
curl http://localhost:5000/api/nonexistent
```

**Response (404 Not Found):**
```json
{
  "error": "NOT_FOUND",
  "message": "The requested resource was not found",
  "status": 404,
  "timestamp": "2026-01-31T10:30:45.123456"
}
```

### Example 5: Error Handling in Python

```python
import requests
from requests.exceptions import RequestException

def safe_forecast_request(location, aqi_data):
    """Make forecast request with error handling."""
    url = "http://localhost:5000/api/forecast/forecast"
    
    payload = {
        "location": location,
        "aqi_data": aqi_data
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        data = e.response.json()
        error_code = data.get('error')
        message = data.get('message')
        
        print(f"API Error: {error_code}")
        print(f"Message: {message}")
        
        # Handle specific errors
        if error_code == 'INVALID_LOCATION':
            print("Please provide valid latitude and longitude")
        elif error_code == 'INVALID_REQUEST':
            print("Check required fields in request")
        elif error_code == 'SERVICE_UNAVAILABLE':
            print("Service is temporarily down, try again later")
        
        return None
    
    except RequestException as e:
        print(f"Network error: {e}")
        return None

# Usage
location = {"latitude": 28.7041, "longitude": 77.1025}
aqi_data = {"pm25": 85, "pm10": 150}

result = safe_forecast_request(location, aqi_data)
if result:
    print(f"Forecast: {result['forecast']}")
```

---

## Advanced Patterns

### Example 1: Batch Processing Multiple Locations

```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def forecast_location(location_data):
    """Get forecast for a single location."""
    url = "http://localhost:5000/api/forecast/forecast"
    
    try:
        response = requests.post(url, json=location_data, timeout=30)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        return {'error': str(e), 'location': location_data}

def batch_forecast(locations):
    """Get forecasts for multiple locations in parallel."""
    results = []
    
    # Use thread pool for concurrent requests
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(forecast_location, loc): loc
            for loc in locations
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    return results

# Usage
locations = [
    {
        "location": {"latitude": 28.7041, "longitude": 77.1025, "city": "Delhi"},
        "aqi_data": {"pm25": 85, "pm10": 150, "no2": 45, "o3": 35, "so2": 20, "co": 1200}
    },
    {
        "location": {"latitude": 19.0760, "longitude": 72.8777, "city": "Mumbai"},
        "aqi_data": {"pm25": 65, "pm10": 110, "no2": 35, "o3": 40, "so2": 15, "co": 900}
    },
    {
        "location": {"latitude": 12.9716, "longitude": 77.5946, "city": "Bangalore"},
        "aqi_data": {"pm25": 45, "pm10": 75, "no2": 25, "o3": 45, "so2": 10, "co": 600}
    }
]

start = time.time()
results = batch_forecast(locations)
duration = time.time() - start

print(f"Processed {len(results)} locations in {duration:.2f}s")

for result in results:
    if 'error' not in result:
        city = result['location'].get('city', 'Unknown')
        aqi = result['forecast'].get('aqi', 'N/A')
        print(f"{city}: AQI {aqi}")
```

### Example 2: Monitoring with Health Checks

```python
import requests
import time
from datetime import datetime, timedelta

class AeroGuardMonitor:
    """Monitor AeroGuard API health and performance."""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.checks = []
    
    def check_health(self):
        """Check API health status."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            check = {
                'timestamp': datetime.now(),
                'status': data['status'],
                'response_time': response.elapsed.total_seconds(),
                'success': True
            }
        except requests.RequestException as e:
            check = {
                'timestamp': datetime.now(),
                'status': 'error',
                'error': str(e),
                'success': False
            }
        
        self.checks.append(check)
        return check
    
    def get_uptime(self, minutes=60):
        """Calculate uptime percentage for last N minutes."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_checks = [c for c in self.checks if c['timestamp'] > cutoff]
        
        if not recent_checks:
            return None
        
        successful = sum(1 for c in recent_checks if c['success'])
        return (successful / len(recent_checks)) * 100
    
    def monitor_continuous(self, interval_seconds=60, duration_minutes=60):
        """Monitor API continuously."""
        start = datetime.now()
        end = start + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end:
            check = self.check_health()
            
            if check['success']:
                print(f"✓ {check['timestamp'].strftime('%H:%M:%S')} - "
                      f"Healthy ({check['response_time']:.3f}s)")
            else:
                print(f"✗ {check['timestamp'].strftime('%H:%M:%S')} - "
                      f"Error: {check['error']}")
            
            time.sleep(interval_seconds)
        
        uptime = self.get_uptime(duration_minutes)
        print(f"\nUptime: {uptime:.1f}%")

# Usage
monitor = AeroGuardMonitor()
monitor.monitor_continuous(interval_seconds=30, duration_minutes=5)
```

### Example 3: Caching Responses Locally

```python
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

class CachedAeroGuardClient:
    """AeroGuard client with local caching."""
    
    def __init__(self, base_url="http://localhost:5000", cache_dir=".cache"):
        self.base_url = base_url
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_ttl = 3600  # 1 hour
    
    def _get_cache_key(self, location, aqi_data):
        """Generate cache key from request data."""
        key_str = f"{location}_{aqi_data}"
        import hashlib
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_file):
        """Check if cache file is still valid."""
        if not cache_file.exists():
            return False
        
        age = time.time() - cache_file.stat().st_mtime
        return age < self.cache_ttl
    
    def forecast(self, location, aqi_data):
        """Get forecast with caching."""
        # Try cache first
        cache_key = self._get_cache_key(location, aqi_data)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if self._is_cache_valid(cache_file):
            print(f"Using cached response")
            with open(cache_file) as f:
                return json.load(f)
        
        # Fetch from API
        print(f"Fetching from API...")
        payload = {"location": location, "aqi_data": aqi_data}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/forecast/forecast",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Save to cache
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            return data
        
        except RequestException as e:
            print(f"API error: {e}")
            return None

# Usage
client = CachedAeroGuardClient()

location = {"latitude": 28.7041, "longitude": 77.1025}
aqi_data = {"pm25": 85, "pm10": 150}

# First call - fetches from API
result1 = client.forecast(location, aqi_data)

# Second call - uses cache
result2 = client.forecast(location, aqi_data)
```

---

## Summary

These examples demonstrate:

✅ Health checking  
✅ API discovery  
✅ Basic requests (curl, Python, JavaScript)  
✅ All three main endpoints  
✅ Error handling patterns  
✅ Advanced patterns (batch, monitoring, caching)  

For more details, see the [Full API Documentation](FORECAST_ROUTES_API.md)
