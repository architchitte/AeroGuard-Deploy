import httpx
from fastapi import HTTPException
from app.core.config import settings

async def fetch_realtime_aqi(city: str = None, lat: float = None, lon: float = None) -> dict:
    """
    Fetch real-time AQI and meteorological data from the WAQI API.
    
    Args:
        city (str, optional): Name of the city to query.
        lat (float, optional): Latitude for geo-query.
        lon (float, optional): Longitude for geo-query.
        
    Returns:
        dict: The 'data' payload from the WAQI JSON response.
    """
    api_key = getattr(settings, "REALTIME_AQI_API_KEY", None)
    if not api_key:
        raise HTTPException(status_code=500, detail="WAQI API Key not configured.")
        
    if lat is not None and lon is not None:
        feed = f"geo:{lat};{lon}"
    elif city:
        feed = city
    else:
        raise HTTPException(status_code=400, detail="Either city or coordinates must be provided.")

    url = f"https://api.waqi.info/feed/{feed}/?token={api_key}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            
            data = response.json()
            
            # WAQI returns 200 OK even for errors, so we explicitly check the body payload
            if data.get("status") == "error":
                raise HTTPException(
                    status_code=404,
                    detail=f"WAQI Error: {data.get('data', 'Unknown station or location not found')}"
                )
                
            return data.get("data", {})
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to WAQI API: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"WAQI API returned an HTTP error: {str(e)}"
        )
