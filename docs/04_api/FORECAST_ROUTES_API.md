## Flask REST API Routes - AeroGuard Forecasting System

**File:** `app/routes/forecast_routes.py`

Complete REST API documentation for AeroGuard's air quality forecasting system. Three integrated endpoints providing forecasting, health risk assessment, and AI-generated explanations.

---

## Table of Contents

1. [Overview](#overview)
2. [Endpoints](#endpoints)
   - [POST /forecast](#post-forecast)
   - [POST /risk](#post-risk)
   - [POST /explain](#post-explain)
3. [Request/Response Format](#requestresponse-format)
4. [Error Handling](#error-handling)
5. [Integration Patterns](#integration-patterns)
6. [Example Workflows](#example-workflows)

---

## Overview

The forecast routes provide three core capabilities:

| Endpoint | Purpose | Input | Output |
|----------|---------|-------|--------|
| **POST /forecast** | 6-hour AQI prediction | Location + historical AQI | Forecast values + trend |
| **POST /risk** | Health risk assessment | AQI + user persona | Risk level + recommendations |
| **POST /explain** | AI explanation generation | Forecast metadata | Human-readable explanation |

**Base URL:** `http://localhost:5000/api/v1`

**Content-Type:** All requests and responses use `application/json`

**Status Codes:**
- `200 OK` - Successful request
- `201 Created` - Resource created (forecast)
- `400 Bad Request` - Validation error
- `500 Internal Server Error` - Server error

---

## Endpoints

### POST /forecast

**Purpose:** Generate 6-hour AQI forecast from historical data

**URL:** `/api/v1/forecast`

**Request Format:**

```json
{
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "name": "New York" // optional
  },
  "aqi_data": [45, 50, 52, 55, 60, 58, 61],
  "hours_ahead": 6,
  "include_confidence": true
}
```

**Request Parameters:**

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `location.latitude` | number | Yes | Geographic latitude | -90 to 90 |
| `location.longitude` | number | Yes | Geographic longitude | -180 to 180 |
| `location.name` | string | No | Location name | Any string |
| `aqi_data` | array | Yes | Historical AQI values | 3-365 values, each 0-500 |
| `hours_ahead` | integer | No | Forecast horizon | 1-24, default 6 |
| `include_confidence` | boolean | No | Include confidence score | default true |

**Response Format (201 Created):**

```json
{
  "status": "success",
  "forecast": {
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "name": "New York"
    },
    "base_aqi": 61.0,
    "forecast_period_hours": 6,
    "predicted_values": [62, 64, 65, 65, 63, 60],
    "timestamps": [
      "2026-01-31T10:00:00",
      "2026-01-31T11:00:00",
      "2026-01-31T12:00:00",
      "2026-01-31T13:00:00",
      "2026-01-31T14:00:00",
      "2026-01-31T15:00:00"
    ],
    "confidence": 0.87,
    "trend": "stable"
  },
  "timestamp": "2026-01-31T09:45:00"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `base_aqi` | number | Most recent AQI value |
| `forecast_period_hours` | integer | Number of hours forecast |
| `predicted_values` | array | Hourly AQI predictions |
| `timestamps` | array | ISO timestamps for each hour |
| `confidence` | number | 0.0-1.0 confidence in forecast |
| `trend` | string | rising, falling, or stable |

**Error Response (400 Bad Request):**

```json
{
  "status": "error",
  "error": "At least 3 historical AQI values required for forecasting",
  "code": "VALIDATION_ERROR"
}
```

**Error Codes:**

| Code | Meaning |
|------|---------|
| `VALIDATION_ERROR` | Input validation failed |
| `INVALID_JSON` | Malformed JSON in request |
| `FORECAST_ERROR` | Forecasting service error |

**Examples:**

*Request:*
```bash
curl -X POST http://localhost:5000/api/v1/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "location": {"latitude": 40.7128, "longitude": -74.0060},
    "aqi_data": [45, 50, 52, 55, 60, 58, 61],
    "hours_ahead": 6
  }'
```

*Success Response:*
```json
{
  "status": "success",
  "forecast": {
    "location": {"latitude": 40.7128, "longitude": -74.0060},
    "base_aqi": 61.0,
    "forecast_period_hours": 6,
    "predicted_values": [62, 64, 65, 65, 63, 60],
    "timestamps": ["2026-01-31T10:00:00", ...],
    "confidence": 0.87,
    "trend": "stable"
  }
}
```

---

### POST /risk

**Purpose:** Assess health risk from AQI and user persona

**URL:** `/api/v1/risk`

**Request Format:**

```json
{
  "aqi": 65,
  "persona": "Athletes",
  "forecast_trend": "rising",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "name": "New York"
  }
}
```

**Request Parameters:**

| Parameter | Type | Required | Description | Valid Values |
|-----------|------|----------|-------------|--------------|
| `aqi` | number | Yes | Current/forecasted AQI | 0-500 |
| `persona` | string | Yes | User persona | General Public, Children, Elderly, Outdoor Workers, Athletes, Sensitive Groups |
| `forecast_trend` | string | No | Expected trend | rising, falling, stable |
| `location.latitude` | number | No | Geographic latitude | -90 to 90 |
| `location.longitude` | number | No | Geographic longitude | -180 to 180 |
| `location.name` | string | No | Location name | Any string |

**Valid Personas:**

```
- General Public
- Children
- Elderly
- Outdoor Workers
- Athletes
- Sensitive Groups
```

**Response Format (200 OK):**

```json
{
  "status": "success",
  "risk_assessment": {
    "aqi": 65,
    "persona": "Athletes",
    "risk_category": "Moderate",
    "risk_level": 2,
    "health_effects": [
      "Exposure to air pollution for extended outdoor activities"
    ],
    "recommendations": {
      "activity": "Reduce prolonged or heavy outdoor exertion",
      "indoor_outdoor": "Enjoy outdoor activities, but increase time indoors",
      "precautions": [
        "Limit intense outdoor activities",
        "Take more frequent breaks",
        "Monitor symptoms"
      ]
    },
    "symptoms_to_watch": [
      "Coughing",
      "Throat irritation",
      "Shortness of breath"
    ]
  },
  "timestamp": "2026-01-31T09:45:00"
}
```

**Risk Categories:**

| Category | AQI Range | Health Impact |
|----------|-----------|---------------|
| Good | 0-50 | No health concerns |
| Moderate | 51-100 | Members of sensitive groups may be affected |
| Unhealthy for Sensitive Groups | 101-150 | General public may begin to experience health effects |
| Unhealthy | 151-200 | Health alert condition |
| Very Unhealthy | 201-300 | Health warning |
| Hazardous | 301+ | Emergency conditions |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `risk_category` | string | EPA air quality category |
| `risk_level` | integer | 0-5 (0=best, 5=worst) |
| `health_effects` | array | Specific health effects for persona |
| `activity` | string | Activity recommendation |
| `indoor_outdoor` | string | Indoor/outdoor guidance |
| `precautions` | array | Protective actions to take |
| `symptoms_to_watch` | array | Warning signs to monitor |

**Error Response (400 Bad Request):**

```json
{
  "status": "error",
  "error": "Invalid persona. Must be one of: General Public, Children, Elderly, Outdoor Workers, Athletes, Sensitive Groups",
  "code": "VALIDATION_ERROR"
}
```

**Examples:**

*Request - High AQI with Children:*
```bash
curl -X POST http://localhost:5000/api/v1/risk \
  -H "Content-Type: application/json" \
  -d '{
    "aqi": 150,
    "persona": "Children",
    "location": {"name": "New York"}
  }'
```

*Response - Unhealthy:*
```json
{
  "status": "success",
  "risk_assessment": {
    "aqi": 150,
    "persona": "Children",
    "risk_category": "Unhealthy for Sensitive Groups",
    "risk_level": 3,
    "health_effects": [
      "Respiratory symptoms in children",
      "Reduced lung function",
      "Increased asthma risk"
    ],
    "recommendations": {
      "activity": "Avoid outdoor activities",
      "indoor_outdoor": "Stay indoors",
      "precautions": [
        "Keep windows closed",
        "Use air purifiers",
        "Avoid strenuous activities"
      ]
    },
    "symptoms_to_watch": [
      "Wheezing",
      "Coughing",
      "Difficulty breathing"
    ]
  }
}
```

---

### POST /explain

**Purpose:** Generate AI-powered human-readable explanation for forecasts

**URL:** `/api/v1/explain`

**Request Format:**

```json
{
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
  "include_health_advisory": true
}
```

**Request Parameters:**

| Parameter | Type | Required | Description | Valid Values |
|-----------|------|----------|-------------|--------------|
| `forecast_metadata.forecast_values` | array | Yes | Predicted AQI values | 0-500 per value |
| `forecast_metadata.historical_values` | array | No | Historical AQI data | 0-500 per value |
| `forecast_metadata.trend` | string | No | Expected trend | rising, falling, stable |
| `forecast_metadata.confidence` | number | No | Confidence score | 0.0-1.0 |
| `location.latitude` | number | Yes | Geographic latitude | -90 to 90 |
| `location.longitude` | number | Yes | Geographic longitude | -180 to 180 |
| `location.name` | string | No | Location name | Any string |
| `style` | string | No | Explanation style | technical, casual, urgent, reassuring (default: casual) |
| `include_health_advisory` | boolean | No | Include health advisory | default true |

**Explanation Styles:**

| Style | Best For | Tone |
|-------|----------|------|
| `technical` | Professionals, scientists | Precise, data-focused |
| `casual` | General public | Friendly, accessible |
| `urgent` | Alerts, warnings | Serious, action-oriented |
| `reassuring` | Good air quality | Positive, comforting |

**Response Format (200 OK):**

```json
{
  "status": "success",
  "explanation": {
    "summary": "Air quality is expected to remain moderate with stable conditions...",
    "trend_description": "Trend: stable",
    "factors": [
      {
        "factor": "Weather patterns",
        "impact": "Neutral",
        "description": "Current wind patterns allow moderate pollutant dispersion"
      },
      {
        "factor": "AQI persistence",
        "impact": "Positive",
        "description": "Recent air quality trends suggest stability"
      }
    ],
    "duration": {
      "classification": "temporary",
      "expected_hours": 12
    },
    "health_advisory": {
      "message": "General public may experience minor symptoms...",
      "severity": "warning",
      "affected_groups": ["Sensitive Groups", "Athletes"],
      "recommended_actions": [
        "Limit prolonged outdoor activities",
        "Use air purifiers indoors",
        "Monitor local AQI updates"
      ]
    }
  },
  "metadata": {
    "generated_at": "2026-01-31T09:45:00",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "tokens_used": 125
  },
  "timestamp": "2026-01-31T09:45:00"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Main explanation paragraph |
| `trend_description` | string | Trend analysis summary |
| `factors` | array | Contributing factors to forecast |
| `duration.classification` | string | temporary or persistent |
| `duration.expected_hours` | integer | Expected duration |
| `health_advisory.message` | string | Health guidance text |
| `health_advisory.severity` | string | info, warning, alert |
| `health_advisory.affected_groups` | array | Groups most affected |
| `health_advisory.recommended_actions` | array | Action recommendations |

**Error Response (400 Bad Request):**

```json
{
  "status": "error",
  "error": "Invalid style. Must be one of: technical, casual, urgent, reassuring",
  "code": "VALIDATION_ERROR"
}
```

**Examples:**

*Request - Casual explanation:*
```bash
curl -X POST http://localhost:5000/api/v1/explain \
  -H "Content-Type: application/json" \
  -d '{
    "forecast_metadata": {
      "forecast_values": [62, 64, 65, 65, 63, 60],
      "historical_values": [45, 50, 52, 55, 60, 58, 61],
      "trend": "rising",
      "confidence": 0.87
    },
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "name": "New York"
    },
    "style": "casual"
  }'
```

*Response - Clear explanation:*
```json
{
  "status": "success",
  "explanation": {
    "summary": "New York's air quality is expected to get slightly worse over the next few hours, reaching moderate levels. The air pollution is mainly temporary and should improve by evening.",
    "trend_description": "Trend: rising",
    "factors": [
      {
        "factor": "Traffic emissions",
        "impact": "Positive",
        "description": "Morning rush hour traffic increases pollutants"
      },
      {
        "factor": "Wind patterns",
        "impact": "Neutral",
        "description": "Light winds limit pollutant dispersion"
      }
    ],
    "duration": {
      "classification": "temporary",
      "expected_hours": 6
    },
    "health_advisory": {
      "message": "Sensitive groups should limit strenuous outdoor activities",
      "severity": "warning",
      "affected_groups": ["Children", "Elderly", "Athletes"],
      "recommended_actions": [
        "Avoid outdoor sports",
        "Keep windows closed",
        "Use N95 masks if going outside"
      ]
    }
  }
}
```

---

## Request/Response Format

### Content-Type

All endpoints require and return `application/json`:

```
Content-Type: application/json
```

### Standard Response Structure

All responses follow this structure:

```json
{
  "status": "success|error",
  "data": { ... },  // Endpoint-specific data
  "timestamp": "ISO-8601 timestamp",
  "code": "ERROR_CODE"  // Only present on error
}
```

### Date/Time Format

All timestamps use ISO-8601 format:

```
2026-01-31T09:45:00
```

### Number Precision

- **AQI values:** Integer 0-500
- **Confidence:** Float 0.0-1.0
- **Coordinates:** Float with up to 6 decimal places

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful GET/POST (risk, explain) |
| 201 | Created | Forecast generated successfully |
| 400 | Bad Request | Validation error |
| 404 | Not Found | Endpoint doesn't exist |
| 500 | Server Error | Internal error |

### Error Response Format

```json
{
  "status": "error",
  "error": "Description of what went wrong",
  "code": "ERROR_CODE",
  "timestamp": "2026-01-31T09:45:00"
}
```

### Common Error Codes

| Code | Cause | Solution |
|------|-------|----------|
| `VALIDATION_ERROR` | Invalid input | Check request format against spec |
| `INVALID_JSON` | Malformed JSON | Ensure valid JSON syntax |
| `FORECAST_ERROR` | Forecasting failed | Retry with valid historical data |
| `RISK_ERROR` | Risk assessment failed | Check persona and AQI values |
| `EXPLANATION_ERROR` | Explanation generation failed | Verify forecast metadata |
| `BAD_REQUEST` | General bad request | Review request structure |
| `NOT_FOUND` | Unknown endpoint | Check endpoint URL |
| `INTERNAL_ERROR` | Server error | Try again or contact support |

### Validation Rules Summary

**Forecast Endpoint:**
```
latitude: -90 to 90
longitude: -180 to 180
aqi_data: 3-365 values, each 0-500
hours_ahead: 1-24 (default 6)
```

**Risk Endpoint:**
```
aqi: 0-500
persona: must be valid persona string
location: optional if provided, must be valid coords
```

**Explain Endpoint:**
```
forecast_values: 1+ values, each 0-500
forecast_metadata: must have forecast_values
location: latitude -90 to 90, longitude -180 to 180
style: technical, casual, urgent, or reassuring
```

---

## Integration Patterns

### 1. Complete Forecasting Workflow

1. Call `/forecast` to get AQI predictions
2. Call `/risk` with highest predicted AQI and persona
3. Call `/explain` with forecast metadata to get explanation

```python
# 1. Get forecast
forecast_response = requests.post(
    'http://localhost:5000/api/v1/forecast',
    json={
        'location': {'latitude': 40.7128, 'longitude': -74.0060},
        'aqi_data': [45, 50, 52, 55, 60, 58, 61],
        'hours_ahead': 6
    }
)
forecast = forecast_response.json()['forecast']
max_aqi = max(forecast['predicted_values'])

# 2. Assess risk
risk_response = requests.post(
    'http://localhost:5000/api/v1/risk',
    json={'aqi': max_aqi, 'persona': 'Athletes'}
)
risk = risk_response.json()['risk_assessment']

# 3. Get explanation
explain_response = requests.post(
    'http://localhost:5000/api/v1/explain',
    json={
        'forecast_metadata': {
            'forecast_values': forecast['predicted_values'],
            'trend': forecast['trend'],
            'confidence': forecast['confidence']
        },
        'location': forecast['location'],
        'style': 'casual'
    }
)
explanation = explain_response.json()['explanation']
```

### 2. Web API Integration

```javascript
async function getAQIInsights(latitude, longitude, historicalData) {
  const baseURL = 'http://localhost:5000/api/v1';
  
  try {
    // 1. Forecast
    const forecastRes = await fetch(`${baseURL}/forecast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: { latitude, longitude },
        aqi_data: historicalData,
        hours_ahead: 6
      })
    });
    
    const forecast = await forecastRes.json();
    
    // 2. Risk assessment
    const riskRes = await fetch(`${baseURL}/risk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        aqi: Math.max(...forecast.forecast.predicted_values),
        persona: 'General Public'
      })
    });
    
    const risk = await riskRes.json();
    
    // 3. Explanation
    const explainRes = await fetch(`${baseURL}/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        forecast_metadata: {
          forecast_values: forecast.forecast.predicted_values,
          trend: forecast.forecast.trend,
          confidence: forecast.forecast.confidence
        },
        location: forecast.forecast.location,
        style: 'casual'
      })
    });
    
    const explanation = await explainRes.json();
    
    return { forecast, risk, explanation };
  } catch (error) {
    console.error('API error:', error);
  }
}
```

### 3. Database Storage Integration

```python
def store_forecast_result(forecast_data, risk_data, explanation_data):
    """Store complete forecast result in database"""
    
    result = {
        'location': forecast_data['location'],
        'timestamp': forecast_data['timestamp'],
        'forecast': {
            'values': forecast_data['forecast']['predicted_values'],
            'trend': forecast_data['forecast']['trend'],
            'confidence': forecast_data['forecast']['confidence']
        },
        'risk': {
            'category': risk_data['risk_assessment']['risk_category'],
            'level': risk_data['risk_assessment']['risk_level']
        },
        'explanation': {
            'summary': explanation_data['explanation']['summary'],
            'provider': explanation_data['metadata']['provider']
        }
    }
    
    # Save to database
    db.forecasts.insert_one(result)
    return result['_id']
```

---

## Example Workflows

### Scenario 1: Morning Air Quality Check

User checks air quality for New York City with recent AQI readings.

**Request:**
```bash
POST /api/v1/forecast
{
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "name": "New York"
  },
  "aqi_data": [48, 50, 52, 55, 58],
  "hours_ahead": 6
}
```

**Response:**
```json
{
  "status": "success",
  "forecast": {
    "base_aqi": 58,
    "predicted_values": [60, 62, 64, 63, 62, 60],
    "trend": "rising_then_falling",
    "confidence": 0.92
  }
}
```

**Follow-up: Assess Risk for Athletes**
```bash
POST /api/v1/risk
{
  "aqi": 64,
  "persona": "Athletes"
}
```

**Response:**
```json
{
  "risk_assessment": {
    "risk_category": "Moderate",
    "recommendations": {
      "activity": "Reduce intense outdoor exertion"
    }
  }
}
```

### Scenario 2: Urgent Health Alert

Forecast shows dangerous AQI spike. Generate urgent explanation.

**Request:**
```bash
POST /api/v1/explain
{
  "forecast_metadata": {
    "forecast_values": [150, 180, 200, 190, 170, 140],
    "trend": "rising",
    "confidence": 0.95
  },
  "location": {"latitude": 40.7128, "longitude": -74.0060},
  "style": "urgent",
  "include_health_advisory": true
}
```

**Response:**
```json
{
  "explanation": {
    "summary": "ALERT: Air quality will reach unhealthy levels with peak AQI 200...",
    "health_advisory": {
      "severity": "alert",
      "affected_groups": ["Children", "Elderly", "Athletes"],
      "recommended_actions": ["Stay indoors", "Seek medical advice if symptoms develop"]
    }
  }
}
```

### Scenario 3: Batch Location Monitoring

Monitor multiple locations simultaneously.

```python
locations = [
    {"name": "Manhattan", "lat": 40.7831, "lon": -73.9712},
    {"name": "Brooklyn", "lat": 40.6782, "lon": -73.9442},
    {"name": "Queens", "lat": 40.7282, "lon": -73.7949}
]

historical_data = [45, 48, 50, 52, 55]

for loc in locations:
    forecast = requests.post('http://localhost:5000/api/v1/forecast', json={
        'location': {'latitude': loc['lat'], 'longitude': loc['lon'], 'name': loc['name']},
        'aqi_data': historical_data
    }).json()
    
    print(f"{loc['name']}: {forecast['forecast']['predicted_values']}")
```

---

## Testing

### cURL Examples

**Forecast:**
```bash
curl -X POST http://localhost:5000/api/v1/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "location": {"latitude": 40.7128, "longitude": -74.0060},
    "aqi_data": [45, 50, 52, 55, 60, 58, 61],
    "hours_ahead": 6,
    "include_confidence": true
  }' | jq
```

**Risk:**
```bash
curl -X POST http://localhost:5000/api/v1/risk \
  -H "Content-Type: application/json" \
  -d '{
    "aqi": 65,
    "persona": "Athletes"
  }' | jq
```

**Explain:**
```bash
curl -X POST http://localhost:5000/api/v1/explain \
  -H "Content-Type: application/json" \
  -d '{
    "forecast_metadata": {
      "forecast_values": [62, 64, 65, 65, 63, 60],
      "trend": "stable"
    },
    "location": {"latitude": 40.7128, "longitude": -74.0060},
    "style": "casual"
  }' | jq
```

### Python Test Client

```python
import requests

BASE_URL = "http://localhost:5000/api/v1"

# Test forecast
response = requests.post(f"{BASE_URL}/forecast", json={
    "location": {"latitude": 40.7128, "longitude": -74.0060},
    "aqi_data": [45, 50, 52, 55, 60, 58, 61]
})
print("Forecast:", response.status_code, response.json())

# Test risk
response = requests.post(f"{BASE_URL}/risk", json={
    "aqi": 65,
    "persona": "Athletes"
})
print("Risk:", response.status_code, response.json())

# Test explain
response = requests.post(f"{BASE_URL}/explain", json={
    "forecast_metadata": {"forecast_values": [62, 64, 65]},
    "location": {"latitude": 40.7128, "longitude": -74.0060}
})
print("Explain:", response.status_code, response.json())
```

---

## Performance Considerations

### Response Times

| Endpoint | Typical | Max |
|----------|---------|-----|
| POST /forecast | 200-500ms | 2s |
| POST /risk | 50-100ms | 500ms |
| POST /explain | 1-3s | 10s |

*Note: Explanation times depend on LLM provider (OpenAI default)*

### Best Practices

1. **Batch requests** - Combine forecast + risk + explain into single workflow
2. **Cache results** - Store forecasts for 10-30 minutes
3. **Error handling** - Implement retry logic for transient errors
4. **Timeout** - Set 15-30 second timeouts on API calls
5. **Monitoring** - Track response times and error rates

---

## Security & Authentication

**Current:** No authentication (for development)

**Production Recommendations:**
- Add API key authentication
- Implement rate limiting (10-100 req/min per key)
- Use HTTPS only
- Validate all inputs (currently implemented)
- Log all requests for audit trail
- Add request signing for sensitive operations

---

## Changelog

**v1.0 (Current)**
- Initial release
- Three core endpoints (forecast, risk, explain)
- Comprehensive input validation
- JSON responses with proper status codes
- Error handling and recovery
- 80+ test cases

---

## Support

For issues, questions, or feature requests:
1. Check error message and code in response
2. Review this documentation for request format
3. Verify input data meets validation requirements
4. Check server logs for detailed error information
5. Contact development team with request/response examples
