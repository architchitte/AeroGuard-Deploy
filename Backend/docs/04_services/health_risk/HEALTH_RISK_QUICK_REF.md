"""
Health Risk Classification Engine - Quick Reference Guide
"""

# Health Risk Classification Engine - Quick Reference

## 🎯 Quick Start

### Import and Create

```python
from app.services.health_risk import create_classifier, Persona, RiskCategory

classifier = create_classifier()
```

### Basic Usage

```python
# Classify AQI value
risk = classifier.classify_aqi(100, 'PM2.5')
# Returns: RiskCategory.UNHEALTHY

# Get color code
color = classifier.get_color_code(risk)
# Returns: "#FF0000" (red)

# Get health effects
effects = classifier.get_health_effects(risk)
# Returns: List of health effect descriptions

# Get advice for specific persona
advice = classifier.get_personalized_advice(risk, Persona.CHILDREN)
# Returns: HealthAdvice with recommendations

# Full assessment
assessment = classifier.assess_health_risk(100, 'PM2.5')
# Returns: HealthRiskAssessment with complete information
```

---

## 📊 AQI Classification Ranges (PM2.5)

| AQI Range | Category | Risk Level | Color |
|-----------|----------|-----------|-------|
| 0-12 | Good | Low | 🟢 Green |
| 12.1-35.4 | Moderate | Low | 🟡 Yellow |
| 35.5-55.4 | Unhealthy for Sensitive | Medium | 🟠 Orange |
| 55.5-150.4 | Unhealthy | High | 🔴 Red |
| 150.5-250.4 | Very Unhealthy | Very High | 🟣 Purple |
| 250.5+ | Hazardous | Critical | ⬛ Maroon |

---

## 👥 Personas Available

```python
Persona.GENERAL_PUBLIC     # Default population
Persona.CHILDREN           # Young people
Persona.ELDERLY            # Older adults
Persona.ATHLETES           # Active individuals
Persona.OUTDOOR_WORKERS    # Work-exposed individuals
```

---

## 🔧 Supported Air Quality Parameters

- `'PM2.5'` - Fine particulate matter
- `'PM10'` - Coarse particulate matter
- `'NO2'` - Nitrogen dioxide
- `'O3'` - Ozone
- `'SO2'` - Sulfur dioxide
- `'CO'` - Carbon monoxide

---

## 📋 Persona-Specific Activities by Risk Level

### Children

```
Good                   → All outdoor activities appropriate
Moderate              → Outdoor play acceptable with breaks
Unhealthy for Sensitive → Move vigorous activities indoors
Unhealthy             → Keep children indoors
Very Unhealthy        → Strict protection needed
Hazardous             → Complete indoor confinement
```

### Athletes

```
Good                   → All outdoor training appropriate
Moderate              → Outdoor training acceptable
Unhealthy for Sensitive → Reduce outdoor training intensity
Unhealthy             → Move training indoors
Very Unhealthy        → Avoid strenuous training
Hazardous             → No physical training
```

### Outdoor Workers

```
Good                   → No work restrictions
Moderate              → Normal outdoor work with breaks
Unhealthy for Sensitive → Reduce outdoor work time
Unhealthy             → Significantly reduce outdoor work
Very Unhealthy        → Minimal outdoor work
Hazardous             → No outdoor work
```

---

## 🎯 Common Use Cases

### Case 1: Single AQI Assessment

```python
classifier = create_classifier()

# Assess air quality
aqi_value = 85
assessment = classifier.assess_health_risk(aqi_value)

print(f"Risk Level: {assessment.risk_category}")
print(f"Color: {assessment.color_code}")
print(f"Effects: {assessment.health_effects[0]}")
```

### Case 2: Multi-Persona Assessment for Vulnerable Groups

```python
vulnerable = [Persona.CHILDREN, Persona.ELDERLY, Persona.OUTDOOR_WORKERS]
assessment = classifier.assess_health_risk(150, personas=vulnerable)

for persona, advice in assessment.personalized_advice.items():
    print(f"{persona}:")
    print(f"  Activity: {advice.activity_recommendation}")
    print(f"  Precautions: {advice.precautions}")
```

### Case 3: Pollution Event Timeline

```python
hourly_aqi = [30, 75, 125, 180, 150, 100]
timeline = []

for aqi in hourly_aqi:
    assessment = classifier.assess_health_risk(aqi)
    timeline.append({
        'aqi': aqi,
        'risk': assessment.risk_category,
        'color': assessment.color_code
    })

# Use timeline for visualization
```

### Case 4: API Response

```python
from flask import Flask, request, jsonify

@app.route('/health-risk', methods=['POST'])
def assess():
    data = request.json
    classifier = create_classifier()
    
    assessment = classifier.assess_health_risk(
        data['aqi_value'],
        data.get('parameter', 'PM2.5')
    )
    
    return jsonify({
        'status': 'success',
        'data': classifier.to_dict(assessment)
    })
```

---

## 🔍 HealthRiskAssessment Object Structure

```python
assessment = classifier.assess_health_risk(100)

# Access properties
assessment.aqi_value              # float - Input AQI value
assessment.aqi_parameter          # str - 'PM2.5', 'PM10', etc.
assessment.risk_category          # str - 'Good', 'Unhealthy', etc.
assessment.color_code             # str - '#FF0000', etc.
assessment.general_advice         # str - Overall recommendation
assessment.personalized_advice    # dict - Persona-specific advice
assessment.health_effects         # list - Health effect descriptions
assessment.at_risk_populations    # list - Groups at risk
assessment.recommended_actions    # dict - Action recommendations
assessment.timestamp              # str - ISO format datetime
```

---

## 📤 Output Formats

### Dictionary Format

```python
result_dict = classifier.to_dict(assessment)
# Fully JSON-serializable
```

### JSON Format

```python
json_string = classifier.to_json(assessment)
# Ready for API response
```

---

## ⚠️ Error Handling

### Invalid Parameter

```python
try:
    risk = classifier.classify_aqi(100, 'INVALID')
except ValueError as e:
    print(f"Error: {e}")  # Unsupported parameter: INVALID
```

### Negative AQI

```python
try:
    risk = classifier.classify_aqi(-50)
except ValueError as e:
    print(f"Error: {e}")  # AQI value must be non-negative
```

### Missing Persona Advice

```python
advice = classifier.get_personalized_advice(
    RiskCategory.GOOD, 
    'NonExistentPersona'
)
if advice is None:
    print("No advice available for specified persona")
```

---

## 🎯 Decision Tree: Activity Recommendations

```
AQI Measurement
    ↓
Classify Risk (classify_aqi)
    ↓
Get At-Risk Groups (get_at_risk_populations)
    ↓
Check Personas of Interest
    ↓
Get Personalized Advice (get_personalized_advice)
    ↓
Extract Recommendations
    ├── activity_recommendation
    ├── indoor_outdoor
    ├── precautions
    └── symptoms_to_watch
```

---

## 📚 Data Classes

### HealthAdvice

```python
@dataclass
class HealthAdvice:
    persona: str                    # Persona name
    risk_category: str             # Risk level
    aqi_range: Tuple[int, int]    # AQI range
    activity_recommendation: str   # What to do
    indoor_outdoor: str            # Where to be
    health_warning: Optional[str]  # Specific warning
    precautions: List[str]        # Protective measures
    symptoms_to_watch: List[str]  # Warning signs
```

### HealthRiskAssessment

```python
@dataclass
class HealthRiskAssessment:
    aqi_value: float                    # Input value
    aqi_parameter: str                  # Parameter type
    risk_category: str                  # Category name
    color_code: str                     # Hex color
    general_advice: str                 # Overall recommendation
    personalized_advice: Dict           # Persona-specific advice
    health_effects: List[str]           # Effect descriptions
    at_risk_populations: List[str]      # Groups at risk
    recommended_actions: Dict[str, str] # Action items
    timestamp: str                      # Assessment time
```

---

## 🚀 Performance

| Operation | Time | Complexity |
|-----------|------|-----------|
| classify_aqi | <1ms | O(1) |
| get_personalized_advice | <1ms | O(1) |
| assess_health_risk | <2ms | O(n) |
| to_dict | <2ms | O(n) |
| to_json | <3ms | O(n) |

n = number of personas requested

---

## 💡 Best Practices

1. **Reuse Classifier Instance**
   ```python
   classifier = create_classifier()  # Create once
   # Use repeatedly
   ```

2. **Specify Relevant Personas**
   ```python
   # Good - only assess needed personas
   assessment = classifier.assess_health_risk(
       100,
       personas=[Persona.CHILDREN, Persona.ELDERLY]
   )
   ```

3. **Validate Input**
   ```python
   if 0 <= aqi_value <= 500:
       assessment = classifier.assess_health_risk(aqi_value)
   ```

4. **Use Appropriate Parameter**
   ```python
   # Match data source
   if source == 'EPA':
       assessment = classifier.assess_health_risk(value, 'PM2.5')
   ```

---

## 🔗 Related Documentation

- **Full Reference**: See `docs/HEALTH_RISK_ENGINE.md`
- **Code Examples**: See `examples/health_risk_examples.py`
- **Tests**: See `tests/test_health_risk.py`

---

## 📞 Support

For issues or questions:
1. Check `HEALTH_RISK_ENGINE.md` documentation
2. Review usage examples
3. Check test cases for patterns
4. See troubleshooting section in full docs
