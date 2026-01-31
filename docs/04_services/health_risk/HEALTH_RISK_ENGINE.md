"""
Complete Health Risk Classification Engine - Module Documentation

This documentation covers the Health Risk Classification Engine that provides
AQI-based health risk assessment with personalized guidance for different
user personas.
"""

# Health Risk Classification Engine - Complete Documentation

## Overview

The **Health Risk Classification Engine** is a comprehensive module that converts Air Quality Index (AQI) values into actionable health risk assessments with personalized recommendations for different user personas.

### Key Features

- **EPA/WHO Compliant**: Uses standard thresholds for PM2.5, PM10, NO₂, O₃, SO₂, and CO
- **Multi-Persona Support**: Tailored advice for General Public, Children, Elderly, Athletes, and Outdoor Workers
- **Structured Output**: JSON-friendly dictionary format for easy integration
- **Health Effects Mapping**: Pre-defined health effects for each risk level
- **Color Coding**: EPA standard color codes for visual identification
- **Comprehensive Advice**: Activity recommendations, precautions, and symptom monitoring

---

## Architecture

### Core Components

```
HealthRiskClassifier (Main)
├── AQIThresholds (Data)
│   ├── PM25_THRESHOLDS
│   ├── PM10_THRESHOLDS
│   ├── NO2_THRESHOLDS
│   ├── O3_THRESHOLDS
│   ├── SO2_THRESHOLDS
│   └── CO_THRESHOLDS
│
├── HealthEffectsMapping (Data)
│   └── EFFECTS[RiskCategory] -> [effects...]
│
├── PersonaHealthAdviceMapping (Data)
│   └── ADVICE[Persona][RiskCategory] -> HealthAdvice
│
├── RiskCategory (Enum)
│   ├── GOOD
│   ├── MODERATE
│   ├── UNHEALTHY_FOR_SENSITIVE
│   ├── UNHEALTHY
│   ├── VERY_UNHEALTHY
│   └── HAZARDOUS
│
└── Persona (Enum)
    ├── GENERAL_PUBLIC
    ├── CHILDREN
    ├── ELDERLY
    ├── ATHLETES
    ├── OUTDOOR_WORKERS
    └── SENSITIVE_GROUPS
```

### Data Classes

#### HealthAdvice
Represents personalized health guidance for a specific persona and risk level.

```python
@dataclass
class HealthAdvice:
    persona: str                    # "Children", "Elderly", etc.
    risk_category: str             # "Good", "Unhealthy", etc.
    aqi_range: Tuple[int, int]    # (min, max) AQI values
    activity_recommendation: str   # What activities are safe
    indoor_outdoor: str            # Recommendations for environment
    health_warning: Optional[str]  # Specific health warnings
    precautions: List[str]        # List of protective measures
    symptoms_to_watch: List[str]  # Symptoms requiring attention
```

#### HealthRiskAssessment
Complete health risk assessment with all relevant information.

```python
@dataclass
class HealthRiskAssessment:
    aqi_value: float                         # The AQI value assessed
    aqi_parameter: str                       # PM2.5, PM10, etc.
    risk_category: str                       # "Good", "Hazardous", etc.
    color_code: str                          # EPA color in hex
    general_advice: str                      # Overall guidance
    personalized_advice: Dict[str, HealthAdvice]  # Per-persona advice
    health_effects: List[str]                # Effects at this level
    at_risk_populations: List[str]           # Groups at risk
    recommended_actions: Dict[str, str]      # Action categories
    timestamp: str                           # ISO format timestamp
```

---

## Usage Guide

### Basic AQI Classification

```python
from app.services.health_risk import create_classifier

# Create classifier
classifier = create_classifier()

# Classify AQI value
risk_category = classifier.classify_aqi(75, 'PM2.5')
# Returns: RiskCategory.MODERATE

# Get color code
color = classifier.get_color_code(risk_category)
# Returns: "#FFFF00" (yellow)
```

### Health Effects Retrieval

```python
# Get health effects for a risk level
effects = classifier.get_health_effects(RiskCategory.UNHEALTHY)
# Returns: ["Some members of general public may experience...", ...]

# Get at-risk populations
at_risk = classifier.get_at_risk_populations(RiskCategory.UNHEALTHY)
# Returns: ["General population", "Children and elderly", ...]
```

### Personalized Health Advice

```python
from app.services.health_risk import Persona

# Get advice for specific persona
advice = classifier.get_personalized_advice(
    RiskCategory.UNHEALTHY,
    Persona.CHILDREN
)

# Access advice properties
print(advice.activity_recommendation)  # "Avoid outdoor activity"
print(advice.precautions)              # List of protective measures
print(advice.symptoms_to_watch)        # Warning signs
```

### Complete Health Assessment

```python
# Single assessment
assessment = classifier.assess_health_risk(150, 'PM2.5')

# Access results
print(assessment.risk_category)        # "Unhealthy for Sensitive Groups"
print(assessment.color_code)           # "#FF7E00"
print(assessment.health_effects)       # List of effects
print(assessment.recommended_actions)  # Dict of recommended actions

# Assessment with specific personas
assessment = classifier.assess_health_risk(
    aqi_value=150,
    parameter='PM2.5',
    personas=[Persona.CHILDREN, Persona.ELDERLY, Persona.ATHLETES]
)
```

### JSON Output

```python
# Convert to dictionary (JSON-friendly)
dict_output = classifier.to_dict(assessment)

# Convert to JSON string
json_output = classifier.to_json(assessment)

# Use in API response
import json
response = {
    "status": "success",
    "data": classifier.to_dict(assessment)
}
json.dumps(response)
```

---

## EPA/WHO AQI Standards

### PM2.5 Thresholds (µg/m³)

| Category | Min | Max | Health Effect |
|----------|-----|-----|---|
| Good | 0 | 12 | No health concerns |
| Moderate | 12.1 | 35.4 | Acceptable air quality |
| Unhealthy for Sensitive | 35.5 | 55.4 | Members of sensitive groups may experience effects |
| Unhealthy | 55.5 | 150.4 | Health effects expected in some people |
| Very Unhealthy | 150.5 | 250.4 | Widespread health effects |
| Hazardous | 250.5+ | ∞ | Emergency conditions |

### Color Code System

- 🟢 **#00E400** - Good
- 🟡 **#FFFF00** - Moderate
- 🟠 **#FF7E00** - Unhealthy for Sensitive
- 🔴 **#FF0000** - Unhealthy
- 🟣 **#8F3F97** - Very Unhealthy
- ⬛ **#7E0023** - Hazardous

---

## Persona-Specific Guidance

### General Public

Basic guidance for most people without specific health vulnerabilities.

```
GOOD: All outdoor activities are appropriate
MODERATE: Outdoor activities are acceptable
UNHEALTHY_FOR_SENSITIVE: Continue outdoor activities
UNHEALTHY: Reduce outdoor activity
VERY_UNHEALTHY: Avoid all outdoor activity
HAZARDOUS: Remain indoors in sealed environment
```

### Children

Enhanced protection for young people with developing lungs.

```
GOOD: All outdoor activities are appropriate
MODERATE: Outdoor play acceptable with breaks
UNHEALTHY_FOR_SENSITIVE: Move vigorous activities indoors
UNHEALTHY: Keep children indoors
VERY_UNHEALTHY: Strict protection needed, sealed rooms
HAZARDOUS: Complete avoidance of outdoor exposure
```

### Elderly

Protection for adults with potentially compromised respiratory/cardiac systems.

```
GOOD: All outdoor activities are appropriate
MODERATE: Outdoor activity acceptable with awareness
UNHEALTHY_FOR_SENSITIVE: Limit outdoor exertion
UNHEALTHY: Stay indoors with good air filtration
VERY_UNHEALTHY: Remain indoors in safe environment
HAZARDOUS: Protected environment required
```

### Athletes

Recommendations for people engaging in vigorous physical activity.

```
GOOD: All outdoor training is appropriate
MODERATE: Outdoor training is acceptable
UNHEALTHY_FOR_SENSITIVE: Reduce outdoor training intensity
UNHEALTHY: Move training indoors
VERY_UNHEALTHY: Avoid strenuous training
HAZARDOUS: No physical training recommended
```

### Outdoor Workers

Protection for people exposed to ambient air for work.

```
GOOD: No work restrictions
MODERATE: Normal outdoor work with breaks
UNHEALTHY_FOR_SENSITIVE: Reduce outdoor work time
UNHEALTHY: Significantly reduce outdoor work
VERY_UNHEALTHY: Minimal outdoor work
HAZARDOUS: No outdoor work
```

---

## API Integration Examples

### Flask Route Integration

```python
from flask import Flask, request, jsonify
from app.services.health_risk import create_classifier, Persona

app = Flask(__name__)
classifier = create_classifier()

@app.route('/api/v1/health-risk', methods=['POST'])
def assess_health_risk():
    """Health risk assessment endpoint"""
    data = request.json
    
    aqi_value = data.get('aqi_value')
    parameter = data.get('parameter', 'PM2.5')
    persona_names = data.get('personas', [])
    
    # Convert persona names to enums
    personas = [Persona[p.upper()] for p in persona_names] if persona_names else None
    
    # Perform assessment
    assessment = classifier.assess_health_risk(aqi_value, parameter, personas)
    
    return jsonify({
        'status': 'success',
        'data': classifier.to_dict(assessment)
    })
```

### Batch Assessment

```python
def batch_assess_locations(locations):
    """Assess multiple locations"""
    classifier = create_classifier()
    results = {}
    
    for location, aqi_value in locations.items():
        assessment = classifier.assess_health_risk(aqi_value)
        results[location] = classifier.to_dict(assessment)
    
    return results

# Usage
locations = {
    "Downtown": 125,
    "Suburbs": 85,
    "Industrial": 200,
}
results = batch_assess_locations(locations)
```

---

## Advanced Usage

### Custom Persona Assessment

```python
def assess_for_vulnerable_groups(aqi_value):
    """Custom assessment for especially vulnerable population"""
    classifier = create_classifier()
    
    vulnerable_personas = [
        Persona.CHILDREN,
        Persona.ELDERLY,
        Persona.SENSITIVE_GROUPS
    ]
    
    return classifier.assess_health_risk(
        aqi_value=aqi_value,
        parameter='PM2.5',
        personas=vulnerable_personas
    )
```

### Air Quality Tracking

```python
def track_pollution_event(hourly_aqi_data):
    """Track pollution event throughout the day"""
    classifier = create_classifier()
    timeline = []
    
    for time, aqi in hourly_aqi_data:
        assessment = classifier.assess_health_risk(aqi)
        timeline.append({
            'time': time,
            'aqi': aqi,
            'risk_level': assessment.risk_category,
            'color': assessment.color_code
        })
    
    return timeline

# Usage
hourly_data = [
    ("06:00", 45),
    ("12:00", 125),
    ("18:00", 200),
]
timeline = track_pollution_event(hourly_data)
```

### Health Advisory Generation

```python
def generate_health_advisory(aqi_value, parameter='PM2.5'):
    """Generate text advisory for public health department"""
    classifier = create_classifier()
    assessment = classifier.assess_health_risk(aqi_value, parameter)
    
    advisory = f"""
    HEALTH ADVISORY
    ===============
    Risk Level: {assessment.risk_category}
    AQI Value: {assessment.aqi_value} {parameter}
    
    At-Risk Groups:
    {', '.join(assessment.at_risk_populations) or 'None'}
    
    Health Effects:
    {chr(10).join('- ' + e for e in assessment.health_effects[:3])}
    
    Recommendations:
    {chr(10).join(f"- {k}: {v}" for k, v in assessment.recommended_actions.items())}
    """
    
    return advisory
```

---

## Error Handling

### Supported Parameters

```python
supported = ['PM2.5', 'PM10', 'NO2', 'O3', 'SO2', 'CO']

classifier = create_classifier()
try:
    classifier.classify_aqi(100, 'InvalidGas')
except ValueError as e:
    print(f"Error: {e}")  # "Unsupported parameter: InvalidGas"
```

### Negative Values

```python
try:
    classifier.classify_aqi(-50, 'PM2.5')
except ValueError as e:
    print(f"Error: {e}")  # "AQI value must be non-negative: -50"
```

### Missing Personas

```python
# Non-existent persona returns None
advice = classifier.get_personalized_advice(
    RiskCategory.GOOD,
    'InvalidPersona'  # Doesn't exist
)
if advice is None:
    print("No advice available for specified persona")
```

---

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| classify_aqi | O(1) | O(1) |
| get_personalized_advice | O(1) | O(1) |
| assess_health_risk | O(n) | O(n) |
| to_dict | O(n) | O(n) |

where n = number of personas requested

---

## Best Practices

### 1. Cache Classifier Instance

```python
# Good - reuse single instance
classifier = create_classifier()

def handle_multiple_requests():
    for aqi_value in aqi_values:
        assessment = classifier.assess_health_risk(aqi_value)
```

### 2. Specify Relevant Personas

```python
# Better - only assess relevant personas
vulnerable_personas = [Persona.CHILDREN, Persona.ELDERLY]
assessment = classifier.assess_health_risk(
    100, 
    personas=vulnerable_personas
)
```

### 3. Validate Input

```python
# Validate before assessment
if 0 <= aqi_value <= 500:
    assessment = classifier.assess_health_risk(aqi_value)
else:
    return error_response("Invalid AQI value")
```

### 4. Use Appropriate Parameters

```python
# Match parameter to your data source
if data_source == 'EPA_PM25':
    assessment = classifier.assess_health_risk(value, 'PM2.5')
elif data_source == 'EPA_PM10':
    assessment = classifier.assess_health_risk(value, 'PM10')
```

---

## Extending the Engine

### Adding New Pollutant

```python
# In AQIThresholds class
NEW_GAS_THRESHOLDS = {
    RiskCategory.GOOD: (0, 50),
    RiskCategory.MODERATE: (51, 100),
    # ... add all categories
}

# In HealthRiskClassifier.__init__
self.thresholds['NEW_GAS'] = AQIThresholds.NEW_GAS_THRESHOLDS
```

### Adding New Persona

```python
# In Persona enum
DOCTORS = "Doctors"

# In PersonaHealthAdviceMapping.ADVICE
Persona.DOCTORS: {
    RiskCategory.GOOD: HealthAdvice(...),
    # ... add all risk categories
}
```

---

## Testing

```python
import pytest
from app.services.health_risk import create_classifier, RiskCategory, Persona

def test_aqi_classification():
    classifier = create_classifier()
    assert classifier.classify_aqi(10) == RiskCategory.GOOD
    assert classifier.classify_aqi(100) == RiskCategory.UNHEALTHY

def test_personalized_advice():
    classifier = create_classifier()
    advice = classifier.get_personalized_advice(
        RiskCategory.UNHEALTHY,
        Persona.CHILDREN
    )
    assert advice is not None
    assert len(advice.precautions) > 0
```

---

## Troubleshooting

### No Advice for Persona
**Issue**: `get_personalized_advice()` returns None
**Solution**: Verify persona is valid Persona enum value

### Classification Returns Hazardous
**Issue**: All high values return Hazardous
**Solution**: Check AQI is within reasonable range (0-500 typically)

### JSON Serialization Error
**Issue**: Can't serialize assessment to JSON
**Solution**: Use `classifier.to_dict()` before `json.dumps()`

---

## Summary

The Health Risk Classification Engine provides:

✅ **EPA/WHO Compliant** AQI classification
✅ **Multi-Persona** personalized guidance  
✅ **Structured Output** for easy integration
✅ **Complete Information** for health decisions
✅ **Error Handling** for invalid inputs
✅ **JSON Export** for API use

For questions or extensions, see the source code in `app/services/health_risk.py`.
