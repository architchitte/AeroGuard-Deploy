import httpx
from fastapi import HTTPException
from app.core.config import settings

async def fetch_realtime_aqi(city: str) -> dict:
    """
    Fetch real-time AQI and meteorological data from the WAQI API.
    
    Args:
        city (str): Name of the city to query.
        
    Returns:
        dict: The 'data' payload from the WAQI JSON response.
        
    Raises:
        fastapi.HTTPException: 
            - 404 if WAQI returns an 'error' status (e.g., 'Unknown station').
            - 503 for network/timeout errors.
            - 502/Other for HTTP status errors from the server.
    """
    # Assuming the config variable is named REALTIME_AQI_API_KEY 
    # based on earlier iterations (or WAQI_API_KEY as per the prompt).
    # Using REALTIME_AQI_API_KEY since it was defined in app/core/config.py
    api_key = getattr(settings, "REALTIME_AQI_API_KEY", None)
    if not api_key:
        raise HTTPException(status_code=500, detail="WAQI API Key not configured.")
        
    url = f"https://api.waqi.info/feed/{city}/?token={api_key}"
    
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
