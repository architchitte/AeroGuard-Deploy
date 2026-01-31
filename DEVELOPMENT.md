# AeroGuard Development Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Development Setup](#development-setup)
4. [Adding New Features](#adding-new-features)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Project Overview

AeroGuard is a production-ready Flask backend for air quality forecasting using machine learning. The project follows modular design principles with clear separation between routes, services, models, and utilities.

### Key Components

| Component | Purpose |
|-----------|---------|
| **Routes** | HTTP API endpoints |
| **Services** | Business logic |
| **Models** | ML model implementations |
| **Utils** | Validators, preprocessors, error handlers |

## Architecture

### Request Flow

```
HTTP Request
    ↓
Route Handler (routes/*.py)
    ↓
Input Validation (utils/validators.py)
    ↓
Service Layer (services/*.py)
    ↓
Model/Data Layer (models/*.py, services/data_service.py)
    ↓
Response Formatting
    ↓
JSON Response
```

### Module Responsibilities

#### Routes (`app/routes/`)
- Handle HTTP requests/responses
- Delegate to services
- Return JSON responses
- Handle basic validation

#### Services (`app/services/`)
- Implement business logic
- Orchestrate model and data operations
- Complex data transformations
- Multi-step workflows

#### Models (`app/models/`)
- ML model implementations
- Feature engineering
- Predictions
- Model persistence

#### Utils (`app/utils/`)
- Input validation
- Data preprocessing
- Error handling
- Common utilities

## Development Setup

### Initial Setup
```bash
# 1. Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env

# 4. Run application
python run.py
```

### Useful Commands

```bash
# Run development server
python run.py

# Run with environment variables
FLASK_ENV=development FLASK_DEBUG=True python run.py

# Run tests
python test_api.py

# Run quick start demo
python quickstart.py

# Run with Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

## Adding New Features

### 1. Adding a New Air Quality Parameter

**Step 1:** Update model support in `app/models/forecast_model.py`
```python
SUPPORTED_PARAMETERS = ["pm25", "pm10", "no2", "o3", "so2", "co", "new_param"]
```

**Step 2:** Update data service in `app/services/data_service.py`
```python
"new_param": np.random.uniform(0, 100),
```

**Step 3:** Add unit mapping in `app/services/forecasting_service.py`
```python
units = {
    ...
    "new_param": "unit",
}
```

### 2. Adding a New Endpoint

**Step 1:** Create new blueprint or extend existing
```python
# app/routes/my_new_route.py
from flask import Blueprint

bp = Blueprint("my_route", __name__, url_prefix="/api/v1/my_route")

@bp.route("", methods=["GET"])
def my_endpoint():
    """Endpoint description."""
    return jsonify({"status": "success"}), 200
```

**Step 2:** Register in `app/__init__.py`
```python
from app.routes import my_new_route
app.register_blueprint(my_new_route.bp)
```

**Step 3:** Add input validation
```python
from app.utils.validators import InputValidator

is_valid, msg = InputValidator.validate_location_id(location_id)
if not is_valid:
    raise ValidationError(msg)
```

### 3. Adding a New ML Model

**Step 1:** Update `ForecastModel` class
```python
from sklearn.ensemble import GradientBoostingRegressor

def _create_model(self):
    if self.model_type == "gradient_boost":
        return GradientBoostingRegressor(...)
```

**Step 2:** Update supported models list
```python
SUPPORTED_MODELS = ["random_forest", "xgboost", "ensemble", "gradient_boost"]
```

**Step 3:** Test training
```python
model = ForecastModel(model_type="gradient_boost")
metrics = model.train(X, y_dict)
```

### 4. Adding Data Preprocessing

**Step 1:** Add method to `DataPreprocessor`
```python
# app/utils/preprocessors.py
@staticmethod
def my_preprocessing(X: np.ndarray) -> np.ndarray:
    """Description."""
    # Implementation
    return processed_X
```

**Step 2:** Use in services
```python
from app.utils.preprocessors import DataPreprocessor

X_processed = DataPreprocessor.my_preprocessing(X)
```

## Best Practices

### Code Style

✅ **DO:**
```python
def get_forecast(location_id: str, days: int = 7) -> Dict:
    """
    Generate forecast.
    
    Args:
        location_id: Location identifier
        days: Number of days to forecast
        
    Returns:
        Dictionary with forecast data
    """
    # Implementation
    return result
```

❌ **DON'T:**
```python
def get_forecast(loc, d):
    # Missing docstring
    return result
```

### Error Handling

✅ **DO:**
```python
from app.utils.error_handlers import ValidationError

is_valid, msg = InputValidator.validate_location_id(location_id)
if not is_valid:
    raise ValidationError(msg)
```

❌ **DON'T:**
```python
if not location_id:
    return {"error": "Invalid"}
```

### API Responses

✅ **DO:**
```python
return jsonify({
    "status": "success",
    "data": result,
    "timestamp": datetime.now().isoformat()
}), 200
```

❌ **DON'T:**
```python
return {"result": result}  # Missing status
```

### Data Validation

✅ **DO:**
```python
# Validate in utils/validators.py
is_valid, msg = InputValidator.validate_forecast_request(data)
if not is_valid:
    raise ValidationError(msg)
```

❌ **DON'T:**
```python
# Validate inline
if not data.get("location_id"):
    raise Exception("Invalid")
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution:** Ensure you're running from project root and PYTHONPATH is set correctly.

#### 2. Model Not Trained
```
RuntimeError: Model must be trained before prediction
```
**Solution:** Train the model first via `/api/v1/model/train` endpoint.

#### 3. Port Already in Use
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>
```

#### 4. Dependencies Issues
```bash
# Clear cache and reinstall
pip install --no-cache-dir -r requirements.txt
```

### Debugging

**Enable Debug Mode:**
```bash
FLASK_ENV=development FLASK_DEBUG=True python run.py
```

**Check Logs:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

**Test Individual Components:**
```python
# test_component.py
from app.models.forecast_model import ForecastModel
import numpy as np

model = ForecastModel()
X = np.random.rand(10, 5)
y = np.random.rand(10)
model.train(X, {"pm25": y})
print(model.predict(X))
```

## Performance Optimization

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param):
    return result
```

### Batch Processing
```python
# Instead of loop
for item in items:
    process(item)

# Use vectorized operations
result = process_batch(np.array(items))
```

### Database Queries
```python
# Use joins instead of separate queries
# Use pagination for large results
# Add proper indexing
```

## Testing Guidelines

### Unit Tests
```python
# test_models.py
def test_forecast_model():
    model = ForecastModel()
    X = np.random.rand(10, 5)
    y = np.random.rand(10)
    metrics = model.train(X, {"pm25": y})
    assert "pm25" in metrics
    assert model.is_trained
```

### Integration Tests
```python
# test_api.py
def test_forecast_endpoint():
    response = requests.post("/api/v1/forecast", json={...})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
```

## Deployment Checklist

- [ ] Test all endpoints
- [ ] Update environment variables
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use Gunicorn/uWSGI
- [ ] Configure reverse proxy (nginx)
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Implement rate limiting
- [ ] Add authentication

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [NumPy Documentation](https://numpy.org/)

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes with proper documentation
3. Test thoroughly
4. Submit pull request

## Support

For issues and questions:
- Check existing issues on GitHub
- Create new issue with detailed description
- Include error logs and reproduction steps

---

**Built with ❤️ by Team 70 (CultBoyz)**
