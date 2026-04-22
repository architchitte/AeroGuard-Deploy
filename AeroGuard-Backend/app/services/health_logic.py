def calculate_health_risk(aqi: int, persona: str) -> dict:
    """
    Translates raw AQI values into persona-specific health recommendations
    based on standard EPA AQI breakpoints.
    """
    # 1. Determine Risk Category based on EPA standards
    if aqi <= 50:
        category = "Good"
    elif aqi <= 100:
        category = "Moderate"
    elif aqi <= 150:
        category = "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        category = "Unhealthy"
    elif aqi <= 300:
        category = "Very Unhealthy"
    else:
        category = "Hazardous"

    # 2. Generate persona-specific actionable advice
    advice = []
    
    if category == "Good":
        advice.append("Air quality is considered satisfactory, and air pollution poses little or no risk.")
        advice.append("It's a great day to be active outside.")
        
    elif category == "Moderate":
        if persona == 'Children / Elderly':
            advice.append("Unusually sensitive individuals should consider limiting prolonged outdoor exertion.")
        elif persona == 'Outdoor Workers / Athletes':
            advice.append("Consider reducing prolonged or heavy outdoor exertion if you experience symptoms like coughing or shortness of breath.")
        else: # General Public
            advice.append("Air quality is acceptable. You can enjoy your normal outdoor activities.")
            
    elif category == "Unhealthy for Sensitive Groups":
        if persona == 'Children / Elderly':
            advice.append("Reduce prolonged or heavy outdoor exertion.")
            advice.append("Take more breaks and do less intense activities.")
            advice.append("Watch for symptoms such as coughing or shortness of breath.")
        elif persona == 'Outdoor Workers / Athletes':
            advice.append("Reduce prolonged or heavy outdoor exertion.")
            advice.append("Schedule heavy activities for times when air quality is better.")
        else: # General Public
            advice.append("The general public is not likely to be affected.")
            advice.append("Enjoy your outdoor activities, but be mindful if you experience any unusual symptoms.")
            
    elif category == "Unhealthy":
        if persona == 'Children / Elderly':
            advice.append("Avoid prolonged or heavy outdoor exertion.")
            advice.append("Move activities indoors or reschedule to a time when air quality is better.")
        elif persona == 'Outdoor Workers / Athletes':
            advice.append("Avoid prolonged or heavy outdoor exertion.")
            advice.append("Consider moving activities indoors or rescheduling.")
        else: # General Public
            advice.append("Reduce prolonged or heavy outdoor exertion.")
            advice.append("Take more breaks during all outdoor activities.")
            
    elif category == "Very Unhealthy":
        if persona == 'Children / Elderly':
            advice.append("Avoid all physical activity outdoors.")
            advice.append("Remain indoors and keep activity levels low.")
        elif persona == 'Outdoor Workers / Athletes':
            advice.append("Avoid all physical activity outdoors.")
            advice.append("Reschedule all heavy outdoor work or athletic events.")
        else: # General Public
            advice.append("Avoid prolonged or heavy outdoor exertion.")
            advice.append("Consider moving activities indoors or rescheduling.")
            
    else: # Hazardous
        advice.append("Health warning of emergency conditions: everyone is more likely to be affected.")
        if persona == 'Children / Elderly' or persona == 'Outdoor Workers / Athletes':
            advice.append("Avoid all outdoor physical activities.")
            advice.append("Remain indoors in a clean environment.")
        else: # General Public
            advice.append("Avoid all outdoor physical activities.")
            advice.append("Remain indoors and keep windows closed if possible.")

    return {
        "risk_category": category,
        "actionable_advice": advice
    }
