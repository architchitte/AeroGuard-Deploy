# 🚀 AeroGuard Hackathon Quick Start

**Get AeroGuard running in 5 minutes!**

## ⚡ Ultra-Quick Setup (5 minutes)

### 1. Install Dependencies (1 minute)

```bash
# Navigate to Backend directory
cd Backend

# Install Python packages
pip install -r requirements.txt

# Verify installation
python -c "import flask, pandas, xgboost; print('✓ All dependencies installed')"
```

### 2. Start the Server (1 minute)

```bash
# Run with default development config
python run.py

# Or specify custom port
FLASK_PORT=8080 python run.py

# Expected output:
# ============================================================
#   AeroGuard Backend - Starting
# ============================================================
# Environment : DEVELOPMENT
# Config      : DevelopmentConfig
# Host        : 0.0.0.0
# Port        : 5000
# Debug       : True
# ============================================================
#
# Starting Flask development server...
# Open browser at: http://localhost:5000
# Health check: http://localhost:5000/health
```

### 3. Test the API (2 minutes)

```bash
# In another terminal, test health check
curl http://localhost:5000/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2026-01-31T...",
#   "environment": "development"
# }
```

✅ **Done! You're running AeroGuard!**

---

## 🎯 Common Development Tasks

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_forecast.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v
```

### Format & Lint Code

```bash
# Format code with Black
black app/

# Lint with Flake8
flake8 app/ --max-line-length=100

# Type checking with Mypy
mypy app/ --ignore-missing-imports
```

### Debug Mode

```bash
# Run with increased logging
LOG_LEVEL=DEBUG python run.py

# Python debugger
python -m pdb run.py
```

### Using Different Configurations

```bash
# Production mode
FLASK_ENV=production python run.py

# Testing mode
FLASK_ENV=testing python run.py

# Custom CORS origins
CORS_ORIGINS="http://localhost:3000,http://example.com" python run.py
```

---

## 📊 API Quick Reference

### Health & Status

```bash
# Health check
GET /health
curl http://localhost:5000/health

# App info
GET /info
curl http://localhost:5000/info
```

### Forecasting

```bash
# Generate forecast
POST /api/v1/forecast
curl -X POST http://localhost:5000/api/v1/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": "central_delhi",
    "days_ahead": 7,
    "include_current": true
  }'

# Get forecast for location
GET /api/v1/forecast/<location_id>
curl http://localhost:5000/api/v1/forecast/central_delhi?days_ahead=7
```

### Model Management

```bash
# Get model info
GET /api/v1/model/info
curl http://localhost:5000/api/v1/model/info

# Compare models
POST /api/v1/model/compare
curl -X POST http://localhost:5000/api/v1/model/compare \
  -H "Content-Type: application/json" \
  -d '{"models": ["xgboost", "sarima"]}'
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Use different port
FLASK_PORT=8080 python run.py

# Or find and kill process on port 5000
lsof -i :5000
kill -9 <PID>
```

### Import Errors

```bash
# Reinstall all dependencies
pip install --upgrade -r requirements.txt

# Check Python version (need 3.8+)
python --version

# Verify backend directory structure
ls -la app/routes/  # Should exist and have files
```

### Models Not Loading

```bash
# Check model directory
ls -la app/models/

# Increase logging
LOG_LEVEL=DEBUG python run.py

# Check XGBoost installation
python -c "import xgboost; print(xgboost.__version__)"
```

### Slow Requests

```bash
# Check response times in logs
LOG_LEVEL=DEBUG python run.py

# Profile with Flask profiler (install flask-profiler)
pip install flask-profiler
# Then add profiling middleware in app/__init__.py
```

---

## 📁 Project Structure

```
Backend/
├── app/                    # Main application
│   ├── __init__.py         # Flask factory
│   ├── config.py           # Configuration
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   ├── models/             # ML models
│   └── utils/              # Utilities
├── tests/                  # Test suite
├── examples/               # Usage examples
├── docs/                   # Documentation
├── requirements.txt        # Dependencies
├── run.py                  # Entry point
└── wsgi.py                 # Production WSGI
```

---

## 🔧 Environment Variables

```bash
# Development
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=true
LOG_LEVEL=DEBUG

# CORS
CORS_ORIGINS="*"  # or specific origins

# Models
MODEL_CACHE_TIMEOUT=3600

# Timeouts
REQUEST_TIMEOUT=30
```

Create a `.env` file:

```bash
# .env
FLASK_ENV=development
FLASK_HOST=localhost
FLASK_PORT=5000
LOG_LEVEL=DEBUG
```

Then load with:

```bash
# Linux/Mac
export $(cat .env | xargs)
python run.py

# Windows PowerShell
Get-Content .env | ForEach-Object { $_ -split '=' | Set-Item env: }
python run.py
```

---

## 🚀 Production Deployment

### Using Gunicorn

```bash
# Install gunicorn (included in requirements.txt)
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# With configuration
gunicorn \
  --workers 4 \
  --worker-class sync \
  --bind 0.0.0.0:5000 \
  --access-logfile - \
  --error-logfile - \
  wsgi:app
```

### Using Docker

```bash
# Build image
docker build -t aeroguard:latest .

# Run container
docker run -p 5000:5000 aeroguard:latest

# With environment
docker run \
  -e FLASK_ENV=production \
  -e CORS_ORIGINS="https://yourdomain.com" \
  -p 5000:5000 \
  aeroguard:latest
```

### Using Docker Compose

```bash
# Run full stack
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app
```

---

## 📚 Documentation Links

- **Setup & Configuration**: [docs/01_getting_started/](docs/01_getting_started/)
- **API Reference**: [docs/05_apis/API_ENDPOINTS_COMPLETE.md](docs/05_apis/API_ENDPOINTS_COMPLETE.md)
- **Services**: [docs/04_services/](docs/04_services/)
- **Models**: [docs/02_models/](docs/02_models/)

---

## 💡 Pro Tips for Hackathon

### 1. **Fast Testing**

```bash
# Test one endpoint quickly
python -m pytest tests/test_forecast.py::test_forecast -v

# Profile specific function
python -c "
from app.services.forecasting_service import ForecastingService
import timeit
print(timeit.timeit(lambda: ForecastingService().generate_forecast(...)))
"
```

### 2. **Mock External Services**

```python
# In tests, use mock
from unittest.mock import patch

@patch('requests.get')
def test_with_mock(mock_get):
    mock_get.return_value.json.return_value = {'status': 'ok'}
    # Your test
```

### 3. **Debug in Browser**

```bash
# Add debug view in app/__init__.py
@app.route('/debug')
def debug_info():
    return {
        'config': dict(app.config),
        'blueprints': list(app.blueprints.keys()),
        'routes': [str(r) for r in app.url_map.iter_rules()]
    }

# Then visit http://localhost:5000/debug
```

### 4. **Quick Performance Check**

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test endpoint performance
ab -n 100 -c 10 http://localhost:5000/health

# Or use wrk
wrk -t4 -c100 -d30s http://localhost:5000/health
```

### 5. **Database/Cache Setup (if needed)**

```bash
# Redis for caching (optional)
pip install redis
docker run -d -p 6379:6379 redis:latest

# MongoDB for data (optional)
docker run -d -p 27017:27017 mongo:latest
```

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Server starts without errors (`python run.py`)
- [ ] Health check passes (`curl http://localhost:5000/health`)
- [ ] Tests run successfully (`pytest`)
- [ ] Can access API documentation

---

## 🎓 Learning Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **XGBoost Guide**: https://xgboost.readthedocs.io/
- **SARIMA/Statsmodels**: https://www.statsmodels.org/
- **REST API Best Practices**: https://restfulapi.net/

---

## 📞 Quick Help

**Something not working?**

1. Check logs: `LOG_LEVEL=DEBUG python run.py`
2. Verify dependencies: `pip install --upgrade -r requirements.txt`
3. Read the docs: [Backend/docs/README.md](docs/README.md)
4. Check examples: [examples/](examples/)
5. Run tests: `pytest -v`

**Performance issues?**

1. Profile with logging: `LOG_LEVEL=DEBUG python run.py`
2. Check database queries
3. Enable caching in config
4. Use production config: `FLASK_ENV=production`

---

**Last Updated**: January 31, 2026  
**Status**: ✅ Production Ready for Hackathon
