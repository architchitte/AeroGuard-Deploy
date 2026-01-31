<<<<<<<< HEAD:Backend/README.md
# AeroGuard

**Air Quality Forecasting System with Machine Learning**

A production-ready Flask backend for predicting air quality (AQI, PM2.5, PM10, etc.) using ensemble ML models and SARIMA time-series forecasting.

## 📁 Project Structure

```
AeroGuard/
├── app/                      # Flask application package
│   ├── __init__.py          # App factory and configuration
│   ├── config.py            # Environment-based settings
│   ├── models/              # ML model implementations
│   │   ├── forecast_model.py    # Sklearn ensemble (RF + XGBoost)
│   │   ├── sarima_model.py      # SARIMA time-series model
│   │   └── xgboost_model.py     # XGBoost gradient boosting model
│   ├── services/            # Business logic layer
│   │   ├── forecasting_service.py   # Forecast orchestration (ensemble, SARIMA, XGBoost)
│   │   ├── model_selector.py        # Model comparison & selection (Judge Favorite ⭐)
│   │   ├── data_service.py          # Data retrieval
│   │   └── data_preprocessing.py    # Data ingestion & preprocessing
│   ├── routes/              # REST API endpoints
│   │   ├── health.py        # Health check endpoint
│   │   ├── forecast.py      # Forecast endpoints
│   │   └── model.py         # Model management endpoints
│   └── utils/               # Utilities and helpers
│       ├── validators.py    # Input validation
│       ├── error_handlers.py    # Error handling
│       ├── preprocessors.py     # Feature engineering
│       └── timeseries_preprocessor.py  # Time-series specific
│
├── tests/                   # Test suite
│   ├── test_api.py         # API integration tests
│   ├── test_timeseries.py  # Time-series module tests
│   ├── test_sarima_model.py    # SARIMA model tests
│   ├── test_xgboost_model.py   # XGBoost model tests
│   ├── test_forecasting_service_xgboost.py  # XGBoost service integration
│   └── test_model_selector.py  # Model comparison service tests (29 tests)
│
├── examples/               # Example scripts and sample data
│   ├── timeseries_examples.py  # Time-series usage examples
│   ├── sample_*.csv        # Sample datasets
│   └── preprocessed_aq_data.*  # Example preprocessed outputs
│
├── docs/                   # Documentation
│   ├── DEVELOPMENT.md      # Development guide
│   ├── GETTING_STARTED.md  # Quick start guide
│   ├── PROJECT_STRUCTURE.md    # Detailed structure
│   ├── MODEL_SELECTOR.md       # Model comparison & selection guide
│   ├── XGBOOST_MODEL.md        # XGBoost model documentation
│   ├── TIMESERIES_PREPROCESSING.md     # Time-series preprocessing API
│   └── TIMESERIES_QUICK_REFERENCE.md   # Quick lookup
│
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Container image definition
├── requirements.txt        # Python dependencies
├── run.py                  # Development server starter
├── wsgi.py                 # Production WSGI entry point
├── quickstart.py           # Quick demo script
├── .env.example            # Environment variables template
└── INDEX.md                # Project index
``` - Production-Ready Flask Backend

AI-based air quality forecasting system with machine learning predictions for PM2.5, PM10, NO₂, O₃, SO₂, and CO.

## 🚀 Features

- **ML-Powered Forecasting**: Ensemble models (Random Forest + XGBoost) for accurate predictions
- **REST API**: Clean, well-documented JSON-only endpoints
- **Modular Architecture**: Separate services, models, utils, and routes
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Production-Ready**: WSGI-compatible, environment configuration, logging
- **Data Processing**: Feature engineering, normalization, outlier detection
- **Model Management**: Train, save, load, and inspect models via API

## 📁 Project Structure

```
AeroGuard/
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── config.py                   # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── forecast_model.py       # ML model wrapper (Random Forest, XGBoost, Ensemble)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── forecasting_service.py # Business logic for forecasting
│   │   └── data_service.py         # Data retrieval and management
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py          # Input validation
│   │   ├── preprocessors.py       # Data preprocessing & feature engineering
│   │   └── error_handlers.py      # Centralized error handling
│   └── routes/
│       ├── __init__.py
│       ├── health.py              # Health check endpoints
│       ├── forecast.py            # Forecasting endpoints
│       └── model.py               # Model management endpoints
├── requirements.txt               # Python dependencies
├── run.py                        # Development entry point
├── wsgi.py                       # Production WSGI entry point
└── README.md                     # This file
```

## 🔧 Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/AIColegion-VESIT/team-70-cultboyz.git
cd AeroGuard
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # Linux/Mac
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## 🏃 Running the Application

### Development
```bash
python run.py
```
Server runs on `http://localhost:5000`

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### With Environment Variables
```bash
FLASK_ENV=production FLASK_DEBUG=False FLASK_PORT=8000 python run.py
```

## 📡 API Endpoints

### Health Check
```
GET /api/v1/health
GET /api/v1/health/ready
GET /api/v1/health/live
```

### Forecasting
```
POST /api/v1/forecast
GET  /api/v1/forecast/{location_id}?days_ahead=7
GET  /api/v1/forecast/{location_id}/current
```

### Model Management
```
POST   /api/v1/model/train
POST   /api/v1/model/save
POST   /api/v1/model/load
GET    /api/v1/model/status
GET    /api/v1/model/{parameter}/feature-importance
```

## 📚 API Usage Examples

### 1. Health Check
```bash
curl http://localhost:5000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-31T10:30:00.123456",
  "version": "1.0.0",
  "service": "AeroGuard"
}
```

### 2. Generate Forecast
```bash
curl -X POST http://localhost:5000/api/v1/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": "mumbai_center",
    "days_ahead": 7
  }'
```

**Response:**
```json
{
  "location_id": "mumbai_center",
  "forecast_date": "2024-01-31T10:30:00.123456",
  "days_ahead": 7,
  "forecasts": {
    "pm25": {
      "parameter": "pm25",
      "unit": "µg/m³",
      "status": "success",
      "predictions": [
        {
          "date": "2024-02-01",
          "value": 45.23,
          "confidence": 0.87
        }
      ]
    }
  }
}
```

### 3. Get Current Conditions
```bash
curl http://localhost:5000/api/v1/forecast/mumbai_center/current
```

### 4. Train Model
```bash
curl -X POST http://localhost:5000/api/v1/model/train \
  -H "Content-Type: application/json" \
  -d '{
    "X": [[1,2,3,...], [4,5,6,...]],
    "y": {"pm25": [45, 50, ...], "pm10": [60, 65, ...]},
    "model_type": "ensemble"
  }'
```

### 5. Save Model
```bash
curl -X POST http://localhost:5000/api/v1/model/save \
  -H "Content-Type: application/json" \
  -d '{"model_path": "models/saved/model_v1"}'
```

### 6. Get Model Status
```bash
curl http://localhost:5000/api/v1/model/status
```

## 🔑 Supported Parameters

Air quality parameters supported by AeroGuard:

| Parameter | Unit | Description |
|-----------|------|-------------|
| PM2.5     | µg/m³ | Fine particulate matter |
| PM10      | µg/m³ | Coarse particulate matter |
| NO₂       | ppb   | Nitrogen dioxide |
| O₃        | ppb   | Ozone |
| SO₂       | ppb   | Sulfur dioxide |
| CO        | ppm   | Carbon monoxide |

## 🤖 ML Models

### Supported Model Types
- **Ensemble**: Hybrid approach (Random Forest + XGBoost averaged)
- **SARIMA**: Seasonal Auto-Regressive Integrated Moving Average for statistical forecasting
- **XGBoost**: Gradient boosting regression with lag-based features for short-term forecasting

### Model Comparison

| Model | Best For | Horizon | Training | Interpretability |
|-------|----------|---------|----------|-----------------|
| **Ensemble** | General purpose | Medium | Fast | Medium |
| **SARIMA** | Seasonal patterns | 7-14 days | Slow | High |
| **XGBoost** | Non-linear patterns | 6-48 hours | Very fast | Medium |

### Model Usage

#### Ensemble (Default)
```python
from app.services.forecasting_service import ForecastingService

service = ForecastingService(model_type="ensemble")
forecast = service.generate_forecast("location_id", days_ahead=7)
```

#### SARIMA (Statistical)
```python
import pandas as pd

service = ForecastingService(model_type="sarima")
historical_series = pd.Series(data, index=date_index)
service.train_sarima(historical_series)
forecast = service.generate_sarima_forecast("location_id", days_ahead=7)
```

#### XGBoost (Gradient Boosting)
```python
service = ForecastingService(model_type="xgboost")
metrics = service.train_xgboost(preprocessed_df)
forecast = service.generate_xgboost_forecast("location_id", days_ahead=7)
```

### Model Features
- **Feature scaling**: StandardScaler for ensemble models
- **Time-series features**: Lag features and rolling statistics for XGBoost
- **Data normalization**: Automatic preprocessing
- **Feature importance**: Analyze model decisions
- **Model persistence**: Save/load with joblib

### Model Comparison & Selection (Judge Favorite ⭐)

**Automated model selection service** that trains multiple models and selects the best performer based on validation metrics.

```python
from app.services.model_selector import ModelSelector
from app.models.sarima_model import SARIMAModel
from app.models.xgboost_model import XGBoostModel

# Create selector
selector = ModelSelector()
selector.add_model("SARIMA", SARIMAModel())
selector.add_model("XGBoost", XGBoostModel())

# Run comparison - trains both models and returns winner
result = selector.select_best(df, target_col="PM2.5", forecast_steps=6)

# Get results
best_model = result['best_model']      # "SARIMA" or "XGBoost"
metrics = result['metrics']             # MAE/RMSE for each model
predictions = result['predictions']     # Forecasts from all models
```

**Features:**
- Automatically trains all models in parallel
- Compares using MAE and RMSE metrics
- Selects best model based on validation performance
- Generates detailed comparison reports
- Extensible design: Add new models without modification
- Support for different forecast horizons

**Benefits:**
- Reduce decision paralysis - automatic model selection
- Fair model comparison on held-out test data
- Detailed metrics for model evaluation
- Easy to extend with new models
- Production-ready error handling

### Documentation
- [Model Comparison Guide](docs/MODEL_SELECTOR.md)
- [XGBoost Model Guide](docs/XGBOOST_MODEL.md)
- [SARIMA Implementation](docs/TIMESERIES_PREPROCESSING.md)
- [Feature Engineering](docs/PROJECT_STRUCTURE.md)
- [Examples](examples/model_comparison_example.py)

## ⚙️ Configuration

### Environment Variables
```bash
FLASK_ENV=production          # production/development
FLASK_DEBUG=False             # True/False
FLASK_HOST=0.0.0.0           # Server host
FLASK_PORT=5000              # Server port
FLASK_CORS_ORIGINS=*         # CORS origins
LOG_LEVEL=INFO               # Logging level
MODEL_CACHE_TIMEOUT=3600     # Cache timeout (seconds)
```

### Configuration Files
- `app/config.py`: Main configuration class
- `app/config.Config`: Base configuration
- `app/config.DevelopmentConfig`: Development overrides
- `app/config.ProductionConfig`: Production overrides

## 🛡️ Error Handling

All endpoints return JSON responses with consistent error format:

```json
{
  "status": "error",
  "message": "Descriptive error message",
  "code": 400
}
```

### Error Types
- **ValidationError (400)**: Input validation failed
- **ModelNotTrainedError (400)**: Model must be trained first
- **DataServiceError (500)**: Data retrieval failed
- **ModelLoadError (500)**: Model loading failed

## 📊 Data Preprocessing

### Features
- **Missing Value Handling**: Mean, forward fill, or drop methods
- **Outlier Detection**: Z-score method
- **Feature Normalization**: Z-score and min-max scaling
- **Feature Engineering**: Rolling means, trends, volatility

### Usage
```python
from app.utils.preprocessors import DataPreprocessor

preprocessor = DataPreprocessor()

# Prepare features for forecasting
features = preprocessor.prepare_features(historical_data, days_ahead=7)

# Normalize data
X_normalized, mean, std = preprocessor.normalize_features(X)
```

## 🧪 Testing

Create a test file `test_aeroguard.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

# Test health check
response = requests.get(f"{BASE_URL}/health")
print("Health Check:", response.json())

# Test forecast
payload = {"location_id": "test_loc", "days_ahead": 7}
response = requests.post(f"{BASE_URL}/forecast", json=payload)
print("Forecast:", response.json())

# Test model status
response = requests.get(f"{BASE_URL}/model/status")
print("Model Status:", response.json())
```

Run tests:
```bash
python test_aeroguard.py
```

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3.3 | Web framework |
| pandas | 2.0.3 | Data manipulation |
| numpy | 1.24.3 | Numerical computing |
| scikit-learn | 1.3.0 | ML algorithms |
| xgboost | 2.0.0 | Gradient boosting |
| statsmodels | 0.14.0 | Statistical modeling |
| joblib | 1.3.1 | Model serialization |
| gunicorn | 21.2.0 | WSGI server |

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:app"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aeroguard
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: aeroguard
        image: aeroguard:latest
        ports:
        - containerPort: 8000
        env:
        - name: FLASK_ENV
          value: production
```

## 📝 Best Practices

✅ **Implemented**
- ✓ Modular architecture with separation of concerns
- ✓ Comprehensive error handling
- ✓ JSON-only responses
- ✓ Input validation for all endpoints
- ✓ Detailed docstrings
- ✓ Environment-based configuration
- ✓ Model persistence and serialization
- ✓ Feature engineering and preprocessing

## 🔐 Security Considerations

- Validate all user inputs
- Sanitize sensitive parameters
- Use environment variables for secrets
- Implement rate limiting for production
- Add authentication/authorization layer
- Enable HTTPS in production
- Implement request size limits

## 🐛 Troubleshooting

### Model not trained error
```
Solution: Train the model first via /api/v1/model/train
```

### Import errors
```
Solution: Ensure all dependencies are installed
pip install -r requirements.txt
```

### Port already in use
```bash
# Find process on port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

## 📈 Performance Tips

1. Use production WSGI server (Gunicorn)
2. Enable response caching
3. Use ensemble models for better accuracy
4. Batch process forecasts
5. Monitor model performance

## 🤝 Contributing

Contributions are welcome! Please:
1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Team

**AeroGuard Development Team - Team 70 (CultBoyz)**
- AIColegion-VESIT

## 📞 Support

For issues and questions:
- GitHub Issues: [Report Bug](https://github.com/AIColegion-VESIT/team-70-cultboyz/issues)
- Email: team70@aeroguard.ai

---

**Built with ❤️ for clean air**
========
>>>>>>>> 8c54ff8f4b221926af47f7c98e54f66361c00e5d:README.md
