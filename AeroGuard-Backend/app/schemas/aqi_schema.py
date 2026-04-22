from pydantic import BaseModel
from typing import List, Optional

class PollutantValue(BaseModel):
    v: float

class IaqiNode(BaseModel):
    pm25: Optional[PollutantValue] = None
    pm10: Optional[PollutantValue] = None
    no2: Optional[PollutantValue] = None
    o3: Optional[PollutantValue] = None
    so2: Optional[PollutantValue] = None
    co: Optional[PollutantValue] = None

class CityNode(BaseModel):
    name: str
    geo: List[float]
    url: str

class ForecastDay(BaseModel):
    avg: float
    day: str
    max: float
    min: float

class DailyForecast(BaseModel):
    pm25: Optional[List[ForecastDay]] = None
    pm10: Optional[List[ForecastDay]] = None
    o3: Optional[List[ForecastDay]] = None
    uvi: Optional[List[ForecastDay]] = None

class ForecastNode(BaseModel):
    daily: Optional[DailyForecast] = None

class WaqiDataNode(BaseModel):
    aqi: int
    idx: int
    city: CityNode
    dominentpol: str
    iaqi: IaqiNode
    forecast: Optional[ForecastNode] = None

class WaqiResponse(BaseModel):
    status: str
    data: WaqiDataNode
