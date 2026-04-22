from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any

class ForecastRequest(BaseModel):
    features: List[List[float]] = Field(
        ..., 
        description="A 2D list of floats representing the historical lookback window data."
    )

class ForecastResponse(BaseModel):
    forecasts: Dict[str, float] = Field(
        ...,
        description="Predicted values for each pollutant target."
    )
    model_type: str = "Weighted Ensemble"
    components: Dict[str, Dict[str, float]] = Field(
        ...,
        description="Individual predictions from SARIMA, XGBoost, and LSTM for each target"
    )
    model_config = ConfigDict(protected_namespaces=())

class LocationForecastResponse(BaseModel):
    location_id: str
    forecast_days: int
    data: Dict[str, float]

class CurrentConditionsResponse(BaseModel):
    location_id: str
    current_aqi: float
    dominant_pollutant: str

class HourlyForecastResponse(BaseModel):
    location_id: str
    forecast: List[Dict[str, Any]]
    model_type: str
    model_config = ConfigDict(protected_namespaces=())
