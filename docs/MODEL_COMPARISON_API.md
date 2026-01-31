# Model Comparison REST API Documentation

## Overview

The Model Comparison REST API provides HTTP endpoints for running intelligent model comparisons on air quality forecasting data. The service automatically trains SARIMA and XGBoost models, compares their performance, and returns the best performer.

**Base URL:** `http://localhost:5000/api/v1/models`

**Status:** ✅ Production Ready

---

## Endpoints

### 1. Compare Models (Full)

**Endpoint:** `POST /api/v1/models/compare`

Run comprehensive model comparison with full configuration options.

#### Request

```json
{
  "data": [
    ["2024-01-01 00:00", 45.2, 60.5],
    ["2024-01-01 01:00", 46.1, 62.3],
    ["2024-01-01 02:00", 47.3, 64.2],
    ...
  ],
  "columns": ["date", "PM2.5", "PM10"],
  "target_col": "PM2.5",
  "forecast_steps": 6,
  "test_size": 0.2,
  "models": ["SARIMA", "XGBoost"]
}
```

#### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| data | array | ✅ Yes | — | Historical data as list of lists |
| columns | array | ✅ Yes | — | Column names corresponding to data columns |
| target_col | string | ❌ No | "PM2.5" | Column to forecast |
| forecast_steps | integer | ❌ No | 6 | Number of steps to forecast |
| test_size | float | ❌ No | 0.2 | Train/test split ratio (0.0-1.0) |
| models | array | ❌ No | ["SARIMA", "XGBoost"] | Models to compare |

#### Response (Success - 200)

```json
{
  "status": "success",
  "timestamp": "2024-01-31T10:30:00.123456",
  "data": {
    "best_model": "XGBoost",
    "metrics": {
      "SARIMA": {
        "MAE": 1.23,
        "RMSE": 2.45,
        "sample_count": 50
      },
      "XGBoost": {
        "MAE": 0.98,
        "RMSE": 1.67,
        "sample_count": 50
      }
    },
    "predictions": {
      "SARIMA": [45.2, 46.1, 47.3, ...],
      "XGBoost": [44.8, 46.2, 47.1, ...]
    },
    "test_actual": [45.0, 46.0, 47.0, ...],
    "comparison_report": {
      "timestamp": "2024-01-31T10:30:00",
      "models": {
        "XGBoost": {
          "rank": 1,
          "MAE": 0.98,
          "RMSE": 1.67,
          "is_best": true,
          "percentage_difference": 0.0
        },
        "SARIMA": {
          "rank": 2,
          "MAE": 1.23,
          "RMSE": 2.45,
          "is_best": false,
          "percentage_difference": 25.51
        }
      }
    }
  }
}
```

#### Response (Error - 400)

```json
{
  "status": "error",
  "message": "Missing required field: data",
  "code": 400
}
```

#### Example Usage

**cURL:**
```bash
curl -X POST http://localhost:5000/api/v1/models/compare \
  -H "Content-Type: application/json" \
  -d '{
    "data": [[...], [...], ...],
    "columns": ["date", "PM2.5", "PM10"],
    "target_col": "PM2.5",
    "forecast_steps": 6
  }'
```

**Python:**
```python
import requests
import pandas as pd

# Prepare data
df = pd.read_csv("aqi_data.csv")
data = df.values.tolist()
columns = df.columns.tolist()

# Send request
response = requests.post(
    'http://localhost:5000/api/v1/models/compare',
    json={
        'data': data,
        'columns': columns,
        'target_col': 'PM2.5',
        'forecast_steps': 6
    }
)

result = response.json()
print(f"Best Model: {result['data']['best_model']}")
print(f"Metrics: {result['data']['metrics']}")
```

---

### 2. Quick Compare

**Endpoint:** `POST /api/v1/models/quick-compare`

Quick model comparison with minimal parameters. Uses sensible defaults.

#### Request

```json
{
  "data": [
    ["2024-01-01 00:00", 45.2, 60.5],
    ...
  ],
  "target_col": "PM2.5"
}
```

**Or with dict format:**
```json
{
  "data": {
    "PM2.5": [45, 46, 47, ...],
    "PM10": [60, 62, 64, ...]
  },
  "target_col": "PM2.5"
}
```

#### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| data | array/object | ✅ Yes | — | Historical data |
| target_col | string | ❌ No | "PM2.5" | Column to forecast |

#### Response (Success - 200)

```json
{
  "status": "success",
  "timestamp": "2024-01-31T10:30:00",
  "data": {
    "best_model": "XGBoost",
    "metrics": {
      "SARIMA": {"MAE": 1.23, "RMSE": 2.45},
      "XGBoost": {"MAE": 0.98, "RMSE": 1.67}
    },
    "winner_forecast": [44.8, 46.2, 47.1, 48.5, 49.2, 50.1]
  }
}
```

#### Example Usage

**Python:**
```python
import requests

response = requests.post(
    'http://localhost:5000/api/v1/models/quick-compare',
    json={
        'data': [[...], [...], ...],
        'target_col': 'PM2.5'
    }
)

result = response.json()
forecast = result['data']['winner_forecast']
```

---

### 3. Available Models

**Endpoint:** `GET /api/v1/models/available-models`

Get list of available models and their characteristics.

#### Request

```
GET /api/v1/models/available-models
```

#### Response (200)

```json
{
  "status": "success",
  "timestamp": "2024-01-31T10:30:00",
  "data": {
    "available_models": [
      {
        "name": "SARIMA",
        "type": "Statistical Forecasting",
        "description": "Seasonal Auto-Regressive Integrated Moving Average",
        "best_for": "Seasonal patterns, 7-14 day horizons",
        "pros": ["High interpretability", "Handles seasonality", "Good for trends"],
        "cons": ["Slow training", "Requires stationarity", "Linear only"],
        "training_time": "Slow (O(n²))"
      },
      {
        "name": "XGBoost",
        "type": "Gradient Boosting",
        "description": "XGBoost regression with lag-based features",
        "best_for": "Non-linear patterns, 6-48 hour horizons",
        "pros": ["Fast training", "Non-linear patterns", "Feature importance"],
        "cons": ["Less interpretable", "Needs feature engineering", "Potential overfitting"],
        "training_time": "Very fast (O(n log n))"
      }
    ],
    "total": 2
  }
}
```

#### Example Usage

**cURL:**
```bash
curl http://localhost:5000/api/v1/models/available-models
```

---

### 4. Comparison Service Info

**Endpoint:** `GET /api/v1/models/comparison-info`

Get information about the comparison service and available endpoints.

#### Request

```
GET /api/v1/models/comparison-info
```

#### Response (200)

```json
{
  "status": "success",
  "timestamp": "2024-01-31T10:30:00",
  "data": {
    "service_name": "Judge Favorite ⭐ Model Comparison Service",
    "version": "1.0.0",
    "description": "Intelligent model comparison for air quality forecasting",
    "metrics_supported": ["MAE", "RMSE", "Percentage Difference"],
    "endpoints": [
      {
        "method": "POST",
        "path": "/api/v1/models/compare",
        "description": "Full model comparison",
        "params": ["data", "columns", "target_col", "forecast_steps", "test_size", "models"]
      },
      ...
    ]
  }
}
```

---

### 5. Health Check

**Endpoint:** `GET /api/v1/models/health`

Check service health and available models.

#### Request

```
GET /api/v1/models/health
```

#### Response (200)

```json
{
  "status": "healthy",
  "service": "model_comparison",
  "timestamp": "2024-01-31T10:30:00",
  "available_models": ["SARIMA", "XGBoost"]
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "status": "error",
  "message": "Descriptive error message",
  "code": 400
}
```

### Common Errors

| Code | Message | Cause |
|------|---------|-------|
| 400 | Missing required field: data | Missing data field in request |
| 400 | Missing required field: columns | Missing columns field in request |
| 400 | Invalid target column 'X' | Column doesn't exist in data |
| 400 | Invalid data format | Data cannot be converted to DataFrame |
| 400 | No valid models specified | All requested models are invalid |
| 400 | Insufficient data (N rows, need ≥20) | Not enough data samples |
| 500 | Internal server error | Unexpected server error |

---

## Response Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 500 | Internal Server Error | Server error |

---

## Data Format

### Time-Series Data (List of Lists)

```json
{
  "data": [
    ["2024-01-01 00:00", 45.2, 60.5],
    ["2024-01-01 01:00", 46.1, 62.3],
    ["2024-01-01 02:00", 47.3, 64.2]
  ],
  "columns": ["date", "PM2.5", "PM10"]
}
```

### Time-Series Data (Dictionary)

```json
{
  "data": {
    "date": ["2024-01-01 00:00", "2024-01-01 01:00", ...],
    "PM2.5": [45.2, 46.1, 47.3, ...],
    "PM10": [60.5, 62.3, 64.2, ...]
  }
}
```

### Data Requirements

- **Minimum samples:** 20
- **Numeric columns:** Target column must be numeric
- **No missing values:** Remove or interpolate NaN values
- **Time ordering:** Data should be ordered chronologically

---

## Metrics Explained

### Mean Absolute Error (MAE)

Average absolute difference between predicted and actual values.

- **Unit:** Same as target variable
- **Interpretation:** Lower is better
- **Use case:** When errors are equally important

### Root Mean Squared Error (RMSE)

Root of average squared differences. Penalizes large errors more.

- **Unit:** Same as target variable
- **Interpretation:** Lower is better
- **Use case:** When large errors are unacceptable

### Percentage Difference

How much worse a model performs compared to the best model.

- **Calculation:** `(MAE - best_MAE) / best_MAE * 100`
- **Interpretation:** 0% = best performer, >0% = worse
- **Use case:** Relative model comparison

---

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider adding:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app=app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)
```

---

## Authentication

Currently no authentication is required. For production, consider:

```python
@app.before_request
def check_api_key():
    if request.endpoint and 'models' in request.endpoint:
        api_key = request.headers.get('X-API-Key')
        if not api_key or not verify_api_key(api_key):
            return jsonify({'error': 'Unauthorized'}), 401
```

---

## Usage Examples

### Example 1: Basic Comparison

```python
import requests
import pandas as pd

# Load data
df = pd.read_csv("aqi_data.csv")

# Send to API
response = requests.post(
    'http://localhost:5000/api/v1/models/compare',
    json={
        'data': df.values.tolist(),
        'columns': df.columns.tolist(),
        'target_col': 'PM2.5'
    }
)

# Get results
result = response.json()
print(f"Best: {result['data']['best_model']}")
print(f"MAE: {result['data']['metrics'][result['data']['best_model']]['MAE']}")
```

### Example 2: Quick Forecast

```python
response = requests.post(
    'http://localhost:5000/api/v1/models/quick-compare',
    json={
        'data': df.values.tolist(),
        'target_col': 'PM2.5'
    }
)

forecast = response.json()['data']['winner_forecast']
```

### Example 3: Compare Multiple Targets

```python
for target in ['PM2.5', 'PM10', 'NO2']:
    response = requests.post(
        'http://localhost:5000/api/v1/models/compare',
        json={
            'data': df.values.tolist(),
            'columns': df.columns.tolist(),
            'target_col': target
        }
    )
    result = response.json()
    print(f"{target}: {result['data']['best_model']} wins")
```

---

## Integration with Frontend

### JavaScript/Node.js

```javascript
async function compareModels(data, columns, target) {
    const response = await fetch('http://localhost:5000/api/v1/models/compare', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            data: data,
            columns: columns,
            target_col: target
        })
    });
    
    const result = await response.json();
    return result.data;
}
```

---

## Performance

| Data Size | Time | Status |
|-----------|------|--------|
| 200 samples | 20-30s | Fast |
| 500 samples | 50-100s | Normal |
| 1000 samples | 100-200s | Acceptable |

---

## Troubleshooting

### Issue: "No valid models specified"
**Solution:** Ensure model names in request are correct: "SARIMA" or "XGBoost"

### Issue: "Insufficient data"
**Solution:** Provide at least 100+ historical samples for better results

### Issue: "Invalid data format"
**Solution:** Ensure data is properly formatted as list of lists or dict

### Issue: Timeout
**Solution:** For large datasets (>1000 samples), consider setting longer timeout in client

---

## API Versioning

Current version: **1.0.0**

All endpoints are under `/api/v1/models`

Future versions will maintain backward compatibility.

---

## Support & Documentation

- [MODEL_SELECTOR.md](../../docs/MODEL_SELECTOR.md) - Service documentation
- [JUDGE_FAVORITE_QUICK_START.md](../../JUDGE_FAVORITE_QUICK_START.md) - Quick start
- [examples/model_comparison_example.py](../../examples/model_comparison_example.py) - Code examples

---

**Status:** ✅ Production Ready
