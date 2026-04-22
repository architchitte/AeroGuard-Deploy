from fastapi import APIRouter
from fastapi.responses import Response

from app.services.waqi_service import fetch_realtime_aqi

router = APIRouter(prefix="/api/v1/realtime-aqi", tags=["Realtime AQI"])

@router.get("/city/{city_name}")
async def get_city_aqi(city_name: str):
    """
    Fetch real-time AQI data for a specific city via WAQI.
    """
    data = await fetch_realtime_aqi(city=city_name)
    return {"status": "success", "city": city_name, "data": data}

@router.get("/coordinates")
async def get_coordinates_aqi(latitude: float, longitude: float):
    """
    Fetch real-time AQI data based on coordinates via WAQI.
    """
    data = await fetch_realtime_aqi(lat=latitude, lon=longitude)
    return {"status": "success", "data": data}


@router.get("/popular-cities")
async def get_popular_cities():
    return {"status": "success", "data": ["Delhi", "Mumbai", "London", "New York"]}

@router.get("/history/{city}")
async def get_history(city: str, days: int = 7):
    return {"status": "success", "city": city, "data": []}

@router.get("/nationwide")
async def get_nationwide_heatmap():
    return {"status": "success", "data": [{"lat": 28.6, "lon": 77.2, "aqi": 150}]}

@router.get("/search")
async def search_location(q: str):
    return {"status": "success", "results": [{"name": q, "lat": 0.0, "lon": 0.0}]}

@router.get("/tiles/{z}/{x}/{y}.png")
async def get_map_tile(z: int, x: int, y: int):
    # Placeholder returning an empty transparent PNG
    # In a real app, this proxies the WAQI tile service
    dummy_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    return Response(content=dummy_png, media_type="image/png")
