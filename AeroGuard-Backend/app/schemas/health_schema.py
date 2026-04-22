from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class PersonaEnum(str, Enum):
    CHILDREN_ELDERLY = 'Children / Elderly'
    OUTDOOR_WORKERS_ATHLETES = 'Outdoor Workers / Athletes'
    GENERAL_PUBLIC = 'General Public'

class HealthRiskRequest(BaseModel):
    aqi: int = Field(..., ge=0, description="The Air Quality Index value")
    persona: PersonaEnum = Field(..., description="The target persona for the health advice")

class HealthRiskResponse(BaseModel):
    aqi: int
    risk_category: str
    persona: str
    actionable_advice: List[str]
