from fastapi import APIRouter, HTTPException
from app.schemas.forecast_schema import (
    ForecastRequest, ForecastResponse, LocationForecastResponse, 
    CurrentConditionsResponse, HourlyForecastResponse
)
from app.ml.inference import generate_ensemble_forecast

router = APIRouter(prefix="/api/v1/forecast", tags=["Forecasting"])

@router.post("/", response_model=ForecastResponse)
async def get_forecast(request: ForecastRequest):
    """
    Generate a multi-pollutant Weighted Ensemble AQI forecast based on historical lookback data.
    """
    try:
        # Await the asynchronous inference engine
        results = await generate_ensemble_forecast(features=request.features)
        
        # Extract the multi-target dictionary into our new schema format
        forecasts = {target: data["ensemble_prediction"] for target, data in results.items()}
        components = {target: data["components"] for target, data in results.items()}
        
        return ForecastResponse(
            forecasts=forecasts,
            components=components
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=503,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating forecast: {str(e)}"
        )

@router.get("/{loc_id}", response_model=LocationForecastResponse)
async def get_location_forecast(loc_id: str, days_ahead: int = 7):
    # Placeholder service logic call
    return LocationForecastResponse(location_id=loc_id, forecast_days=days_ahead, data={"pm25": 45.0, "o3": 30.2})

@router.get("/{loc_id}/current", response_model=CurrentConditionsResponse)
async def get_current_conditions(loc_id: str):
    # Placeholder service logic call
    return CurrentConditionsResponse(location_id=loc_id, current_aqi=50.0, dominant_pollutant="pm25")

@router.get("/{loc_id}/6h", response_model=HourlyForecastResponse)
async def get_hourly_forecast(loc_id: str, latitude: float = None, longitude: float = None):
    # Placeholder service logic call for hybrid model
    return HourlyForecastResponse(
        location_id=loc_id, 
        forecast=[{"hour": "10 AM", "aqi": 120.0, "trend": "up"}], 
        model_type="hybrid"
    )
