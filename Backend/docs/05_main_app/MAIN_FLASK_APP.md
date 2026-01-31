# AeroGuard Main Flask Application

## Overview

The main Flask application for AeroGuard implements a production-grade Flask setup with:

- **Application Factory Pattern**: Modular app creation with configuration management
- **Blueprint Registration**: Organized route management with URL prefixes
- **CORS Support**: Cross-origin request handling for frontend integration
- **Global Error Handling**: Consistent error response format across all endpoints
- **Request/Response Logging**: Detailed request tracking with unique request IDs
- **Health Check Endpoint**: For monitoring and service status verification
- **Environment-based Configuration**: Development, testing, and production configs
- **Security Best Practices**: HTTPS enforcement, secure cookies, CSRF protection

## Architecture

### File Structure

```
Backend/
├── app/
│   ├── __init__.py           # Main Flask app factory (this module)
│   ├── config.py             # Environment-based configuration classes
│   ├── routes/
│   │   ├── __init__.py
│   │   └── forecast_routes.py # Forecast, risk, and explain endpoints
│   ├── services/
│   │   ├── spatial_interpolation.py
│   │   ├── forecasting_service.py
│   │   └── ... (other services)
│   └── models/
├── run.py                     # Development server entry point
├── wsgi.py                    # Production WSGI entry point (Gunicorn)
└── requirements.txt
```

## Application Factory (app/__init__.py)

### Functions

#### `create_app(config=None) -> Flask`

Creates and configures a Flask application instance.

**Parameters:**
- `config` (optional): Configuration class (e.g., `ProductionConfig`)
  - If None, auto-detects from `FLASK_ENV` environment variable

**Returns:**
- Configured Flask application instance

**What it does:**
1. Creates Flask app instance
2. Loads configuration (from parameter or environment variable)
3. Configures logging (file + console handlers)
4. Registers request/response handlers (logging, metrics)
5. Sets up CORS (cross-origin support)
6. Registers error handlers (400-503 + generic)
7. Registers utility routes (/health, /info, /)
8. Registers all blueprints (forecast_routes, etc.)

**Example Usage:**

```python
# Development
from app import create_app
app = create_app()  # Auto-detects from FLASK_ENV
app.run(debug=True)

# Production
from app import create_app
from app.config import ProductionConfig
app = create_app(ProductionConfig)
# Run with Gunicorn
```

### Helper Functions

#### `_configure_logging(app)`

Configures application logging with:
- **Console handler**: Real-time log output
- **File handler** (production only): Persistent logs in `logs/aeroguard.log`
- **Log level**: Configurable via `LOG_LEVEL` environment variable
- **Format**: Includes timestamp, level, module, and message

#### `_register_blueprints(app)`

Registers route blueprints:
- `forecast_routes.py` → `/api/forecast` prefix
  - `/api/forecast/forecast` - POST (AQI prediction)
  - `/api/forecast/risk` - POST (Health risk)
  - `/api/forecast/explain` - POST (Explanations)

#### `_setup_cors(app)`

Configures CORS with:
- **Origins**: Configurable via `CORS_ORIGINS` environment variable
  - Development: `*` (allow all)
  - Production: Specific origins from config
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Content-Type, Authorization
- **Credentials**: Supported with SameSite=Lax
- **Max age**: 3600 seconds (1 hour)

#### `_register_error_handlers(app)`

Implements consistent error responses for:
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `405 Method Not Allowed`: Wrong HTTP method
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service down
- Generic exceptions: Caught and logged

**Error Response Format:**
```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "status": 400,
  "timestamp": "2026-01-31T10:30:00.000000"
}
```

#### `_register_request_handlers(app)`

Implements request/response lifecycle:

**Before Request:**
- Captures start time
- Assigns unique request ID (from header or generated)
- Logs incoming request details

**After Response:**
- Calculates response time
- Logs response status and duration
- Adds headers:
  - `X-Request-ID`: Unique request identifier
  - `X-Response-Time`: Duration in seconds
  - `X-Powered-By`: "AeroGuard"

#### `_register_routes(app)`

Registers utility routes:

**GET `/`**
- API root endpoint
- Lists available endpoints
- Returns welcome message

**GET `/health`**
- Health check for monitoring
- Returns current status, version, environment
- Status code: 200 OK

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-31T10:30:00.000000",
  "version": "1.0.0",
  "environment": "production",
  "service": "AeroGuard API"
}
```

**GET `/info`**
- Application metadata and configuration
- Shows version, environment, debug status
- Status code: 200 OK

**Response:**
```json
{
  "name": "AeroGuard",
  "description": "Air Quality Prediction & Explainability System",
  "version": "1.0.0",
  "environment": "production",
  "debug": false,
  "timestamp": "2026-01-31T10:30:00.000000"
}
```

## Configuration (app/config.py)

### Configuration Classes

#### `Config` (Base)

Common settings for all environments:
- Security: HTTPS enforcement, secure cookies, CSRF protection
- Limits: 50MB max upload, request timeout, session lifetime
- Logging: File and console handlers
- Features: Caching, rate limiting, service flags
- CORS: Configurable origins and methods

#### `DevelopmentConfig`

Development-specific overrides:
- `DEBUG=True`: Auto-reload, detailed error pages
- `LOG_LEVEL=DEBUG`: Verbose logging
- `CORS_ORIGINS='*'`: Allow all origins
- `MODEL_CACHE_ENABLED=False`: Always fresh data
- `SQLALCHEMY_ECHO=True`: SQL query logging
- `RATE_LIMIT_ENABLED=False`: No rate limiting

#### `TestingConfig`

Testing-specific settings:
- `TESTING=True`: Test mode
- `SQLALCHEMY_DATABASE_URI=sqlite:///:memory:`: In-memory DB
- `WTF_CSRF_ENABLED=False`: No CSRF validation
- `REQUEST_TIMEOUT=5`: Short timeout for fast tests
- `LOG_LEVEL=WARNING`: Minimal logging
- `MODEL_CACHE_ENABLED=False`: No caching
- `CORS_ORIGINS='*'`: Permissive CORS

#### `ProductionConfig`

Production-specific settings:
- `DEBUG=False`: No debug mode or error details
- `SESSION_COOKIE_SECURE=True`: HTTPS only
- `SESSION_COOKIE_SAMESITE='Strict'`: CSRF protection
- `LOG_LEVEL=INFO`: Essential logs only
- `JSONIFY_PRETTYPRINT_REGULAR=False`: Compact JSON
- `RATE_LIMIT_ENABLED=True`: 100 requests/minute
- `MODEL_CACHE_ENABLED=True`: 1-hour cache TTL
- `CORS_ORIGINS`: Restricted to configured origins

### Environment Variables

#### Core Configuration

- `FLASK_ENV` (default: `development`)
  - Values: `development`, `testing`, `production`
  - Determines which config class is loaded

- `FLASK_DEBUG` (default: `False`)
  - Enable/disable debug mode
  - Only applies in development

- `SECRET_KEY` (REQUIRED for production)
  - Session signing key
  - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

- `APP_VERSION` (default: `1.0.0`)
  - Application version string
  - Displayed in /health and /info endpoints

#### Flask Server Configuration

- `FLASK_HOST` (default: `0.0.0.0`)
  - Host to bind the development server
  - Example: `127.0.0.1` (localhost only)

- `FLASK_PORT` (default: `8000`)
  - Port for development server
  - Example: `5000`

#### CORS Configuration

- `CORS_ORIGINS` (default: `*`)
  - Allowed origins for cross-origin requests
  - Format: comma-separated list
  - Examples:
    - Dev: `*`
    - Prod: `http://frontend.example.com,https://frontend.example.com`

#### Logging Configuration

- `LOG_LEVEL` (default: `INFO`)
  - Logging verbosity
  - Values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

#### Request Configuration

- `REQUEST_TIMEOUT` (default: `30`)
  - Request timeout in seconds
  - Example: `30`

#### Model Configuration

- `MODEL_CACHE_TIMEOUT` (default: `3600`)
  - Cache time-to-live in seconds (1 hour)

- `MODEL_CACHE_ENABLED` (default: `true`)
  - Enable/disable caching
  - Values: `true`, `false`

#### Service Configuration

- `FORECAST_SERVICE_ENABLED` (default: `true`)
- `HEALTH_RISK_SERVICE_ENABLED` (default: `true`)
- `EXPLAINABILITY_SERVICE_ENABLED` (default: `true`)

#### Feature Flags

- `FEATURE_GENERATIVE_EXPLANATIONS` (default: `true`)
  - Enable AI-powered explanations
  - Requires LLM service

- `FEATURE_BATCH_PROCESSING` (default: `false`)
  - Enable batch request processing
  - For bulk predictions

- `FEATURE_CACHING` (default: `true`)
  - Enable response caching

#### Rate Limiting

- `RATE_LIMIT_ENABLED` (default: `false`)
  - Enable/disable rate limiting

- `RATE_LIMIT_REQUESTS` (default: `100`)
  - Requests per window

- `RATE_LIMIT_WINDOW` (default: `60`)
  - Time window in seconds

### Example .env Files

**Development (.env)**
```
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
CORS_ORIGINS=*
LOG_LEVEL=DEBUG
MODEL_CACHE_ENABLED=false
APP_VERSION=1.0.0-dev
```

**Production (.env.production)**
```
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
CORS_ORIGINS=https://frontend.example.com
LOG_LEVEL=INFO
MODEL_CACHE_ENABLED=true
MODEL_CACHE_TIMEOUT=3600
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
SECRET_KEY=<generate-with-secrets-module>
APP_VERSION=1.0.0
DATABASE_URL=postgresql://user:pass@host/db
```

## Running the Application

### Development

```bash
# Using run.py
python run.py

# Using Flask CLI
export FLASK_ENV=development
export FLASK_DEBUG=True
flask --app app run

# With specific host/port
python run.py  # Reads FLASK_HOST, FLASK_PORT from .env
```

### Production

```bash
# Using Gunicorn (WSGI server)
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

# With environment file
gunicorn -w 4 -b 0.0.0.0:8000 --env-file .env.production wsgi:app

# With more options
gunicorn \
  -w 4 \
  -b 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  wsgi:app
```

### Docker

```bash
# Build
docker build -t aeroguard:1.0 .

# Run
docker run -p 8000:8000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  aeroguard:1.0
```

## Testing the Application

### Health Check
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-31T10:30:00.000000",
  "version": "1.0.0",
  "environment": "development",
  "service": "AeroGuard API"
}
```

### API Info
```bash
curl http://localhost:5000/info
```

### Root Endpoint
```bash
curl http://localhost:5000/
```

### Forecast Endpoint
```bash
curl -X POST http://localhost:5000/api/forecast/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "location": {"latitude": 28.7041, "longitude": 77.1025},
    "aqi_data": {"pm25": 85, "pm10": 150, "no2": 45, "o3": 35, "so2": 20, "co": 1200}
  }'
```

## Best Practices Implemented

### 1. Application Factory Pattern
- Decouples app creation from configuration
- Enables multiple app instances for testing
- Facilitates circular import prevention

### 2. Modular Route Organization
- Blueprints for logical grouping
- URL prefix isolation
- Easy to extend with new routes

### 3. Consistent Error Handling
- Standardized error response format
- Proper HTTP status codes
- Detailed error logging with stack traces

### 4. Request/Response Logging
- Unique request IDs for tracking
- Response time measurement
- Non-intrusive implementation

### 5. Configuration Management
- Environment-specific configs
- Secret management (no hardcoded secrets)
- Feature flags for gradual rollout

### 6. Security Best Practices
- CORS with origin validation
- Secure cookies (HTTPS, HttpOnly, SameSite)
- CSRF protection (token validation)
- Input validation (in routes module)
- Secret key enforcement in production

### 7. Monitoring & Observability
- Health check endpoint
- Application info endpoint
- Structured logging
- Request/response metrics

### 8. Performance Optimization
- Response caching (configurable)
- Connection pooling (database)
- Request timeout enforcement
- Rate limiting (configurable)

## Extending the Application

### Adding a New Blueprint

1. Create route file in `app/routes/`:
```python
# app/routes/new_routes.py
from flask import Blueprint

new_bp = Blueprint('new', __name__)

@new_bp.route('/endpoint', methods=['GET'])
def new_endpoint():
    return {'message': 'Hello'}, 200
```

2. Register in `_register_blueprints()`:
```python
def _register_blueprints(app: Flask) -> None:
    from app.routes.new_routes import new_bp
    app.register_blueprint(new_bp, url_prefix='/api/new')
```

### Adding a Custom Error Handler

```python
@app.errorhandler(CustomException)
def handle_custom_exception(error):
    return jsonify({
        'error': 'CUSTOM_ERROR',
        'message': str(error),
        'status': 400
    }), 400
```

### Adding Middleware

```python
@app.before_request
def custom_middleware():
    # Execute before each request
    pass

@app.after_request
def custom_response_handler(response):
    # Execute after each response
    return response
```

## Troubleshooting

### Issue: "SECRET_KEY environment variable is required"
**Solution**: Set `SECRET_KEY` in .env or environment:
```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### Issue: "Address already in use" error
**Solution**: Change `FLASK_PORT` in .env or kill the process:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Issue: CORS errors from frontend
**Solution**: Set `CORS_ORIGINS` to your frontend URL:
```bash
export CORS_ORIGINS=http://localhost:3000
```

### Issue: Blueprints not registered
**Solution**: Verify import path in `_register_blueprints()`:
```python
# Check import path
from app.routes.forecast_routes import forecast_bp

# Check blueprint name and prefix
app.register_blueprint(forecast_bp, url_prefix='/api/forecast')
```

## Performance Considerations

### Caching
- Model predictions cached for 1 hour (configurable)
- Cache key based on input parameters
- Reduces redundant computations

### Connection Pooling
- Database connections pooled for reuse
- Pool size: 10 (configurable)
- Automatic connection recycling

### Rate Limiting
- 100 requests/minute per IP (production)
- Prevents abuse and DDoS
- Configurable per environment

### Logging
- Async file handlers for minimal impact
- Structured logging for easy parsing
- Request ID for distributed tracing

## Monitoring

### Health Check Endpoint
```bash
# Check application status
curl http://localhost:8000/health

# In monitoring system (Prometheus, etc.)
# Check status code == 200
# Check response.status == "healthy"
```

### Logging
```bash
# View application logs
tail -f logs/aeroguard.log

# Filter errors
grep ERROR logs/aeroguard.log
```

### Metrics
- Request count by endpoint
- Response time distribution
- Error rate by type
- Cache hit ratio

## Related Documentation

- [Forecast Routes API](FORECAST_ROUTES_API.md)
- [Configuration Guide](app/config.py)
- [Spatial Interpolation Service](services/spatial_interpolation.py)
- [Health Risk Classification](services/health_risk_classifier.py)
- [Explainability Services](services/aqi_explainer.py)
