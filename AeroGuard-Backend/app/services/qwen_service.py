import httpx
import asyncio
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.ai_schema import ExplainForecastRequest

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = "qwen/qwen3-coder-480b-a35b-instruct"

async def _call_nvidia_api(payload: dict) -> dict:
    """
    Internal helper to call the NVIDIA API with basic retry logic for 429/503 errors.
    """
    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        for attempt in range(2): # Try twice
            try:
                response = await client.post(NVIDIA_API_URL, headers=headers, json=payload, timeout=20.0)
                
                # Check for rate limit or service overload
                if response.status_code in [429, 503] and attempt == 0:
                    print(f"DEBUG: NVIDIA API returned {response.status_code}. Retrying in 2 seconds...")
                    await asyncio.sleep(2)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == 1: # Last attempt
                    raise HTTPException(
                        status_code=503,
                        detail=f"NVIDIA API Service Unavailable: {str(e)}"
                    )
    return {} # Should not reach here

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
    
    result = await _call_nvidia_api(payload)
    if not result:
        return {"briefing": "Unable to generate briefing.", "advice": "Please check local AQI manually."}
        
    content = result["choices"][0]["message"]["content"]
    
    # Parse the strict formatting requested in the system prompt
    parts = content.split("Advice:")
    briefing = parts[0].replace("Briefing:", "").strip()
    advice = parts[1].strip() if len(parts) > 1 else "Please monitor local air quality updates."
    
    return {
        "briefing": briefing,
        "advice": advice
    }


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
    
    result = await _call_nvidia_api(payload)
    if not result:
        return "Unable to explain forecast at this time."
        
    return result["choices"][0]["message"]["content"].strip()

