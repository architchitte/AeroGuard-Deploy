# Main Flask App - Quick Start Guide

Get AeroGuard running in 30 seconds!

## Installation

```bash
cd Backend
pip install -r requirements.txt
```

## Configuration

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Update .env** (if needed):
   ```env
   FLASK_ENV=development
   FLASK_DEBUG=True
   FLASK_HOST=127.0.0.1
   FLASK_PORT=5000
   CORS_ORIGINS=*
   ```

## Run Development Server

```bash
# From Backend/ directory
python run.py

# Or using Flask CLI
export FLASK_ENV=development
flask --app app run
```

**Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

## Test the API

### Health Check
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "AeroGuard API",
  "version": "1.0.0",
  "environment": "development"
}
```

### List Endpoints
```bash
curl http://localhost:5000/
```

### Forecast (Main Endpoint)
```bash
curl -X POST http://localhost:5000/api/forecast/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "location": {"latitude": 28.7041, "longitude": 77.1025},
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

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API root / welcome |
| `/health` | GET | Health check |
| `/info` | GET | App info |
| `/api/forecast/forecast` | POST | AQI prediction |
| `/api/forecast/risk` | POST | Health risk assessment |
| `/api/forecast/explain` | POST | AI explanations |

## Environment Configuration

### Development
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
```

### Production
```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

## Run with Gunicorn (Production)

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

# With environment file
gunicorn -w 4 -b 0.0.0.0:8000 --env-file .env.production wsgi:app
```

## Docker

```bash
# Build
docker build -t aeroguard:1.0 .

# Run
docker run -p 8000:8000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  aeroguard:1.0

# Check health
curl http://localhost:8000/health
```

## Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: Run from `Backend/` directory
```bash
cd Backend
python run.py
```

### Port Already in Use
```
Address already in use
```
**Solution**: Change port in .env
```bash
export FLASK_PORT=5001
```

### CORS Errors
**Solution**: Set CORS_ORIGINS in .env
```bash
export CORS_ORIGINS=http://localhost:3000
```

## Features

✅ Health check endpoint  
✅ CORS enabled  
✅ Global error handling  
✅ Request logging with IDs  
✅ Blueprint-based routing  
✅ Environment configuration  
✅ Production-ready  

## Next Steps

1. **Test the forecast endpoint**: See [Forecast Routes API](../04_api/FORECAST_ROUTES_API.md)
2. **Understand the config**: See [Configuration Guide](../05_main_app/MAIN_FLASK_APP.md#configuration-appconfig)
3. **Deploy to production**: See deployment guides in README.md
4. **Integrate frontend**: Connect your React/Vue app to endpoints

## Quick Reference

| Task | Command |
|------|---------|
| Run dev server | `python run.py` |
| Run tests | `pytest` |
| Check health | `curl /health` |
| View logs | `tail -f logs/aeroguard.log` |
| Install deps | `pip install -r requirements.txt` |
| Generate secret | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

## Environment Variables Cheat Sheet

```bash
# Core
FLASK_ENV=development|production|testing
FLASK_DEBUG=True|False
SECRET_KEY=your-secret-key

# Server
FLASK_HOST=0.0.0.0
FLASK_PORT=8000

# CORS
CORS_ORIGINS=*|http://localhost:3000

# Logging
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# Features
MODEL_CACHE_ENABLED=true|false
FEATURE_GENERATIVE_EXPLANATIONS=true|false
RATE_LIMIT_ENABLED=true|false
```

## Support

See [Full Documentation](MAIN_FLASK_APP.md) for:
- Detailed configuration
- Adding new blueprints
- Custom error handlers
- Performance tuning
- Monitoring setup

Need help? Check the troubleshooting section in the main docs!
