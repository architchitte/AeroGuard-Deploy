import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.ai_schema import ExplainForecastRequest

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = "qwen/qwen3-coder-480b-a35b-instruct"

async def generate_health_briefing(city: str, persona: str) -> dict:
    """
    Generate an empathetic health briefing and actionable advice using NVIDIA's Qwen API.
    
    Args:
        city (str): The location context.
        persona (str): The target demographic (e.g., 'Children / Elderly').
        
    Returns:
        dict: Contains 'briefing' and 'advice' strings.
    """
    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are an empathetic health advisor. Provide a concise health briefing and clear, "
        "actionable advice based on air quality. IMPORTANT: Use a conversational, empathetic, "
        "and non-technical human tone. Do not output any code blocks or technical jargon. "
        "Format your response exactly like this:\n"
        "Briefing: [your briefing here]\n"
        "Advice: [your advice here]"
    )
    
    user_prompt = f"Provide a health briefing for {persona} in {city}."
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 250
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(NVIDIA_API_URL, headers=headers, json=payload, timeout=15.0)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse the strict formatting requested in the system prompt
            parts = content.split("Advice:")
            briefing = parts[0].replace("Briefing:", "").strip()
            advice = parts[1].strip() if len(parts) > 1 else "Please monitor local air quality updates."
            
            return {
                "briefing": briefing,
                "advice": advice
            }
            
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"NVIDIA API Service Unavailable: {str(e)}"
        )

async def explain_forecast(request: ExplainForecastRequest) -> str:
    """
    Generate a scientific, human-readable forecast explanation using NVIDIA's Qwen API.
    
    Args:
        request (ExplainForecastRequest): Contains aqi_value, trend, and factors.
        
    Returns:
        str: The generated explanation string.
    """
    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are an environmental scientist. Given an AQI value, a trend, and contributing factors, "
        "explain the forecast clearly and concisely to the general public in 2-3 sentences. "
        "IMPORTANT: Use a conversational, non-technical human tone. Do not output any code "
        "blocks or technical formulas."
    )
    
    factors_str = ", ".join(request.factors)
    user_prompt = f"AQI Value: {request.aqi_value}, Trend: {request.trend}, Factors: {factors_str}."
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 250
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(NVIDIA_API_URL, headers=headers, json=payload, timeout=15.0)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"NVIDIA API Service Unavailable: {str(e)}"
        )
