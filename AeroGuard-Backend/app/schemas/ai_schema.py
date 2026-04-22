from pydantic import BaseModel, Field
from typing import List

class BriefingResponse(BaseModel):
    city: str
    persona: str
    briefing: str
    advice: str

class ExplainForecastRequest(BaseModel):
    aqi_value: int = Field(..., description="The forecasted AQI value")
    trend: str = Field(..., description="Trend of the AQI, e.g., 'rising', 'falling', 'stable'")
    factors: List[str] = Field(..., description="List of factors affecting the AQI")

class ExplainForecastResponse(BaseModel):
    explanation: str
