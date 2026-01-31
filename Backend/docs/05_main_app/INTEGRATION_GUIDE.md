# Main Flask App - Integration Guide

Complete guide to integrating the main Flask application with all AeroGuard components.

## Architecture Overview

```
┌─────────────────────────────────────────┐
│     Frontend (React/Vue)                │
└──────────────┬──────────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────────┐
│   Flask Application (app/__init__.py)   │
│  ┌────────────────────────────────────┐ │
│  │ CORS, Error Handling, Logging      │ │
│  │ Request/Response Middleware        │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │   Blueprints (Routes)            │   │
│  ├──────────────────────────────────┤   │
│  │ - forecast_routes.py             │   │
│  │   ├─ /api/forecast/forecast      │   │
│  │   ├─ /api/forecast/risk          │   │
│  │   └─ /api/forecast/explain       │   │
│  │                                  │   │
│  │ - (future) analytics_routes.py   │   │
│  │ - (future) model_routes.py       │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │   Services Layer                 │   │
│  ├──────────────────────────────────┤   │
│  │ - ForecastingService             │   │
│  │ - HealthRiskClassifier           │   │
│  │ - AQIExplainer                   │   │
│  │ - GenerativeExplainer            │   │
│  │ - SpatialInterpolationService    │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │   Data & Models                  │   │
│  ├──────────────────────────────────┤   │
│  │ - XGBoost Models                 │   │
│  │ - SARIMA Models                  │   │
│  │ - Explainability Models          │   │
│  │ - LLM Integration (Generative)   │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Component Integration

### 1. Flask App ↔ Routes (Blueprints)

**How it works:**
- Flask app loads configuration
- App registers blueprints with URL prefixes
- Routes handle HTTP requests
- Routes call services for business logic

**Integration in app/__init__.py:**
```python
def _register_blueprints(app: Flask) -> None:
    from app.routes.forecast_routes import forecast_bp
    app.register_blueprint(forecast_bp, url_prefix='/api/forecast')
```

**Adding new blueprints:**
1. Create route file: `app/routes/new_routes.py`
2. Define blueprint: `new_bp = Blueprint('new', __name__)`
3. Add routes: `@new_bp.route('/endpoint')`
4. Register in `_register_blueprints()`:
   ```python
   from app.routes.new_routes import new_bp
   app.register_blueprint(new_bp, url_prefix='/api/new')
   ```

### 2. Routes ↔ Services

**How it works:**
- Routes receive HTTP requests
- Routes validate input data
- Routes call service methods
- Services perform business logic
- Routes format response

**Example (forecast_routes.py):**
```python
@forecast_bp.route('/forecast', methods=['POST'])
def forecast():
    # Validate input
    data = request.get_json()
    _validate_location(data.get('location'))
    
    # Call service
    service = _init_forecast_service()
    result = service.predict(
        location=data['location'],
        aqi_data=data['aqi_data']
    )
    
    # Return response
    return jsonify({
        'forecast': result,
        'timestamp': datetime.utcnow().isoformat()
    }), 200
```

**Services to integrate:**
- `ForecastingService`: XGBoost/SARIMA predictions
- `HealthRiskClassifier`: 6-persona health risk assessment
- `AQIExplainer`: Rule-based explanations
- `GenerativeExplainer`: LLM-powered explanations
- `SpatialInterpolationService`: Hyper-local AQI estimation

### 3. Services ↔ Models

**How it works:**
- Services load pre-trained models
- Services prepare input data
- Services call model.predict()
- Services post-process predictions
- Services return formatted results

**Service structure:**
```python
class ForecastingService:
    def __init__(self):
        self.model = self._load_model()  # Load XGBoost/SARIMA
    
    def predict(self, location, aqi_data):
        # Preprocess
        features = self._prepare_features(aqi_data)
        
        # Predict
        forecast = self.model.predict(features)
        
        # Postprocess
        return self._format_forecast(forecast)
```

### 4. Flask App ↔ Configuration

**How it works:**
- Flask app reads FLASK_ENV variable
- Loads appropriate config class
- Config sets up logging, security, features
- Services use config settings (caching, timeouts)

**Configuration hierarchy:**
```
Environment Variables (.env)
           ↓
Config Class (Config, DevelopmentConfig, ProductionConfig)
           ↓
Flask app.config
           ↓
Services (read config via app.config)
```

**Services accessing config:**
```python
from flask import current_app

class ForecastingService:
    def __init__(self):
        # Access Flask config
        self.cache_timeout = current_app.config['MODEL_CACHE_TIMEOUT']
        self.caching_enabled = current_app.config['MODEL_CACHE_ENABLED']
```

## Request Flow Diagram

```
┌─ Frontend (React/Vue)
│
├─ HTTP POST /api/forecast/forecast
│  └─ Content-Type: application/json
│     Body: {location, aqi_data}
│
├─ Flask CORS Middleware
│  └─ Validate origin
│     Add CORS headers
│
├─ Request Logger (@before_request)
│  └─ Capture timestamp
│     Assign request ID
│     Log request details
│
├─ Route Handler (forecast_routes.py)
│  ├─ Validate input (_validate_location, _validate_aqi_data)
│  ├─ Call ForecastingService.predict()
│  │  ├─ Load XGBoost/SARIMA model
│  │  ├─ Prepare features
│  │  ├─ Generate predictions
│  │  └─ Return forecast
│  │
│  ├─ Call HealthRiskClassifier.classify() [if needed]
│  │  ├─ Map AQI to health categories
│  │  ├─ Generate persona-specific advice
│  │  └─ Return risk assessment
│  │
│  ├─ Format response JSON
│  └─ Return 200 OK with data
│
├─ Response Logger (@after_request)
│  ├─ Calculate duration
│  ├─ Log response status
│  ├─ Add X-Response-Time header
│  └─ Add X-Request-ID header
│
└─ Frontend receives JSON response
```

## Integration Checklist

### Phase 1: Core Setup ✅
- [x] Flask app factory created
- [x] Configuration system implemented
- [x] Error handlers registered
- [x] Request/response logging
- [x] CORS configured
- [x] Health check endpoint
- [x] Blueprint registration system

### Phase 2: Route Integration ✅
- [x] Forecast routes implemented (3 endpoints)
- [x] Input validation helpers
- [x] Service initialization functions
- [x] Error handling per endpoint
- [x] Response formatting

### Phase 3: Service Integration
- [ ] ForecastingService integration
  - [ ] Load XGBoost models
  - [ ] Load SARIMA models
  - [ ] Handle model caching
  - [ ] Error handling and fallbacks
  
- [ ] HealthRiskClassifier integration
  - [ ] 6 persona support
  - [ ] Advice generation
  - [ ] Response formatting
  
- [ ] AQIExplainer integration
  - [ ] Rule-based explanations
  - [ ] Feature importance analysis
  - [ ] Risk explanation
  
- [ ] GenerativeExplainer integration
  - [ ] LLM API integration
  - [ ] Prompt engineering
  - [ ] Response parsing
  
- [ ] SpatialInterpolationService integration
  - [ ] IDW algorithm
  - [ ] Hyper-local estimation
  - [ ] Cache management

### Phase 4: Frontend Integration
- [ ] CORS testing with frontend
- [ ] API endpoint testing
- [ ] Error handling in frontend
- [ ] Loading states
- [ ] Response parsing
- [ ] User feedback

### Phase 5: Deployment
- [ ] Environment configuration (.env.production)
- [ ] Secret key generation
- [ ] Database setup (if using)
- [ ] Logging to files
- [ ] Health check monitoring
- [ ] Rate limiting enablement
- [ ] HTTPS configuration

## Adding a New Service

### Step 1: Create Service Class

```python
# app/services/new_service.py

class NewService:
    """Service description."""
    
    def __init__(self):
        """Initialize service with models/resources."""
        pass
    
    def process(self, input_data):
        """Process input and return output."""
        pass
```

### Step 2: Create Route Handler

```python
# app/routes/new_routes.py

from flask import Blueprint, request, jsonify
from app.services.new_service import NewService

new_bp = Blueprint('new', __name__)

def _init_new_service():
    """Lazy-load service."""
    return NewService()

@new_bp.route('/endpoint', methods=['POST'])
def endpoint():
    """Handle request."""
    data = request.get_json()
    
    # Validate
    if not data:
        return jsonify({'error': 'INVALID_REQUEST'}), 400
    
    # Process
    service = _init_new_service()
    result = service.process(data)
    
    # Return
    return jsonify({'result': result}), 200
```

### Step 3: Register Blueprint

```python
# app/__init__.py

def _register_blueprints(app: Flask) -> None:
    from app.routes.new_routes import new_bp
    app.register_blueprint(new_bp, url_prefix='/api/new')
```

### Step 4: Test

```bash
curl -X POST http://localhost:5000/api/new/endpoint \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

## Accessing Configuration in Services

### In Services
```python
from flask import current_app

class MyService:
    def __init__(self):
        # Access config
        timeout = current_app.config['REQUEST_TIMEOUT']
        cache_enabled = current_app.config['FEATURE_CACHING']
        log_level = current_app.config['LOG_LEVEL']
        
        # Log
        current_app.logger.info('Service initialized')
```

### In Routes
```python
from flask import current_app

@my_bp.route('/endpoint')
def endpoint():
    # Access config
    max_requests = current_app.config['RATE_LIMIT_REQUESTS']
    
    # Log
    current_app.logger.debug('Processing request')
```

## Error Handling Integration

### Service-level Errors

```python
class ForecastingService:
    def predict(self, location, aqi_data):
        try:
            # Process
            result = self.model.predict(features)
            return result
        except Exception as e:
            # Log error
            current_app.logger.error(f'Prediction failed: {e}')
            # Re-raise for route to handle
            raise PredictionError(str(e)) from e
```

### Route-level Error Handling

```python
@forecast_bp.route('/forecast', methods=['POST'])
def forecast():
    try:
        service = _init_forecast_service()
        result = service.predict(location, aqi_data)
        return jsonify(result), 200
    except PredictionError as e:
        current_app.logger.warning(f'Prediction error: {e}')
        return jsonify({
            'error': 'PREDICTION_ERROR',
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f'Unexpected error: {e}')
        return jsonify({
            'error': 'INTERNAL_SERVER_ERROR',
            'message': 'An error occurred'
        }), 500
```

## Testing Integration

### Unit Tests

```python
# tests/test_app.py

def test_health_check(app):
    """Test health check endpoint."""
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_forecast_endpoint(app):
    """Test forecast endpoint."""
    client = app.test_client()
    response = client.post('/api/forecast/forecast',
        json={
            'location': {'latitude': 28.7, 'longitude': 77.1},
            'aqi_data': {'pm25': 85, 'pm10': 150}
        }
    )
    assert response.status_code == 200
```

### Integration Tests

```python
# tests/test_integration.py

def test_full_workflow(app):
    """Test full forecast -> risk -> explain workflow."""
    client = app.test_client()
    
    # Step 1: Forecast
    forecast_resp = client.post('/api/forecast/forecast', json={...})
    assert forecast_resp.status_code == 200
    forecast_data = forecast_resp.json
    
    # Step 2: Risk assessment
    risk_resp = client.post('/api/forecast/risk', json={
        'aqi': forecast_data['forecast']['aqi']
    })
    assert risk_resp.status_code == 200
    
    # Step 3: Explanation
    explain_resp = client.post('/api/forecast/explain', json={
        'metadata': forecast_data
    })
    assert explain_resp.status_code == 200
```

## Performance Optimization

### Request Timeout
```python
# Enforced by Flask/Gunicorn
REQUEST_TIMEOUT = 30  # seconds

# In routes, set explicit timeout
try:
    result = service.predict(...)  # Must complete in 30s
except TimeoutError:
    return jsonify({'error': 'REQUEST_TIMEOUT'}), 504
```

### Caching
```python
# In service
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

class ForecastingService:
    @cache.cached(timeout=3600)  # Cache for 1 hour
    def predict(self, location, aqi_data):
        # Cached computation
        return model.predict(...)
```

### Connection Pooling
```python
# In config.py (ProductionConfig)
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,  # Verify connection is alive
}
```

## Monitoring Integration

### Health Checks
```bash
# Kubernetes liveness probe
curl http://localhost:8000/health

# Monitoring system
while true; do
    curl -s http://localhost:8000/health | jq .status
    sleep 60
done
```

### Logging
```python
# Application logs automatically saved
tail -f logs/aeroguard.log

# Filter by level
grep ERROR logs/aeroguard.log
grep WARNING logs/aeroguard.log
```

### Metrics
```python
# Request metrics (via request ID)
grep "POST /api/forecast/forecast" logs/aeroguard.log | wc -l

# Response times
grep "X-Response-Time" logs/aeroguard.log
```

## Deployment Integration

### Development
```bash
cd Backend
export FLASK_ENV=development
python run.py
```

### Production with Gunicorn
```bash
cd Backend
gunicorn -w 4 -b 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  wsgi:app
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY Backend/requirements.txt .
RUN pip install -r requirements.txt

COPY Backend/ .

ENV FLASK_ENV=production
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:app"]
```

## Related Documentation

- [Main Flask App](MAIN_FLASK_APP.md)
- [Quick Start Guide](QUICK_START.md)
- [Forecast Routes API](../04_api/FORECAST_ROUTES_API.md)
- [Forecast Routes Examples](../04_api/FORECAST_ROUTES_EXAMPLES.md)
