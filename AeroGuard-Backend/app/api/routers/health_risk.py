from fastapi import APIRouter, Depends
from app.schemas.health_schema import HealthRiskRequest, HealthRiskResponse
from app.services.health_logic import calculate_health_risk

router = APIRouter(prefix="/api/v1/health-risk", tags=["Health Risk Assessment"])

@router.get("/", response_model=HealthRiskResponse)
async def get_health_risk(request: HealthRiskRequest = Depends()):
    """
    Get a persona-specific health risk assessment based on the provided AQI.
    """
    result = calculate_health_risk(aqi=request.aqi, persona=request.persona.value)
    
    return HealthRiskResponse(
        aqi=request.aqi,
        risk_category=result["risk_category"],
        persona=request.persona.value,
        actionable_advice=result["actionable_advice"]
    )
