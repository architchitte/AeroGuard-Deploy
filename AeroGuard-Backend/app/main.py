from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Initialize the FastAPI application
app = FastAPI(
    title="AeroGuard API",
    description="Hyper-Local Air Quality & Health Risk Forecaster",
    version="2.0.0"
)

# Configure CORS using settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base health-check route
@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "success",
        "message": "AeroGuard API is running",
        "version": "2.0.0"
    }

# Register Routers
from app.api.routers import ai, health_risk, forecast, realtime, models, historical, analytics
app.include_router(ai.router)
app.include_router(health_risk.router)
app.include_router(forecast.router)
app.include_router(realtime.router)
app.include_router(models.router)
app.include_router(historical.router)
app.include_router(analytics.router)
