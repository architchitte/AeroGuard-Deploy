from fastapi import APIRouter, Query
from app.schemas.ai_schema import BriefingResponse, ExplainForecastRequest, ExplainForecastResponse
from app.services.qwen_service import generate_health_briefing, explain_forecast

router = APIRouter(prefix="/api/v1/ai", tags=["AI Explainability"])

@router.get("/briefing", response_model=BriefingResponse)
async def get_briefing(
    city: str = Query(..., description="The city to generate the briefing for"),
    persona: str = Query(..., description="The target persona (e.g., 'elderly', 'athlete', 'general_public')")
):
    """
    Generate a personalized AI-powered health briefing for a given city and persona.
    """
    result = await generate_health_briefing(city=city, persona=persona)
    
    return BriefingResponse(
        city=city,
        persona=persona,
        briefing=result.get("briefing", ""),
        advice=result.get("advice", "")
    )

@router.post("/explain-forecast", response_model=ExplainForecastResponse)
async def explain_forecast_endpoint(request: ExplainForecastRequest):
    """
    Explain a complex AQI forecast using AI in human-readable language.
    """
    explanation = await explain_forecast(request)
    return ExplainForecastResponse(explanation=explanation)
