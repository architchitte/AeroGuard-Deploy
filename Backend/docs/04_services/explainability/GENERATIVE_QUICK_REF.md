# Generative Explainer - Quick Reference

## 30-Second Quickstart

```python
from app.services.generative_explainer import GenerativeExplainer, LLMConfiguration, APIProvider

# Create with templates (no API key needed)
config = LLMConfiguration(provider=APIProvider.TEMPLATE)
explainer = GenerativeExplainer(config)

# Generate explanation
result = explainer.generate_explanation(
    aqi_value=100.0,
    trend="rising",
    main_factors=["traffic"],
    duration="persistent"
)

print(result.explanation)
print(result.health_advisory.message)
```

## Common Patterns

### Template Provider (Offline)
```python
config = LLMConfiguration(provider=APIProvider.TEMPLATE)
explainer = GenerativeExplainer(config)
```

### OpenAI Integration
```python
config = LLMConfiguration(
    api_key="sk-...",
    provider=APIProvider.OPENAI,
    fallback_to_template=True
)
explainer = GenerativeExplainer(config)
```

### Factory Function
```python
from app.services.generative_explainer import create_generative_explainer

explainer = create_generative_explainer()  # Template provider by default
```

## Explanation Styles

| Style | Use Case | Tone |
|-------|----------|------|
| TECHNICAL | Professionals, detailed reports | Formal, specific metrics |
| CASUAL | General public, social media | Conversational, simple |
| URGENT | Hazardous conditions | Action-oriented, warnings |
| REASSURING | Good air quality | Balanced, positive |

## Personas

| Persona | Focus | Key Action |
|---------|-------|-----------|
| general_public | Basic protection | Limit outdoor time |
| children | Respiratory protection | Avoid outdoor play |
| elderly | Pre-existing conditions | Minimize exposure |
| athletes | Training adjustment | Move indoors |
| outdoor_workers | Occupational safety | Use N95 masks |

## Parameters

```python
explainer.generate_explanation(
    aqi_value=100.0,          # Required: 0-500+
    trend="rising",           # Required: "rising", "falling", "stable"
    main_factors=["traffic"], # Required: list of pollution sources
    duration="persistent",    # Required: "temporary", "persistent"
    persona="general_public", # Optional: persona for guidance
    explanation_style=None,   # Optional: override style
    include_health_advisory=True  # Optional: include advisory
)
```

## Severity Levels

```
AQI 0-50:   Good           → "Low" severity
AQI 51-100: Moderate       → "Low" severity
AQI 101-150: Unhealthy SG  → "Moderate" severity
AQI 151-200: Unhealthy     → "High" severity
AQI 201+:   Hazardous      → "Critical" severity
```

## Output Structure

```python
result.explanation              # str: Human-readable explanation
result.health_advisory.message  # str: Primary health message
result.health_advisory.severity # str: "Low", "Moderate", "High", "Critical"
result.health_advisory.affected_groups     # List[str]
result.health_advisory.recommended_actions # List[str]
result.explanation_style       # ExplanationStyle: Style used
result.provider_used           # APIProvider: Which provider generated this
result.is_cached              # bool: Was cached?
result.model_used             # str: Model name if LLM
result.generation_time_ms     # int: Generation time
```

## Configuration Cheatsheet

```python
config = LLMConfiguration(
    # API Settings
    api_key="sk-...",                      # OpenAI API key
    provider=APIProvider.OPENAI,           # OPENAI, TEMPLATE, MOCK
    
    # Model Settings
    model="gpt-3.5-turbo",                 # or "gpt-4"
    temperature=0.7,                       # Explanation: 0.3-0.9
    advisory_temperature=0.5,              # Advisory: 0.2-0.8
    
    # Resilience
    max_retries=2,                         # Retry attempts on API error
    timeout=10,                            # Request timeout (seconds)
    fallback_to_template=True,             # Auto-fallback on error
    
    # Optimization
    use_cache=True,                        # Cache explanations
)
```

## Debug Information

```python
# Check which provider was used
print(f"Provider: {result.provider_used.value}")

# Check generation time
print(f"Generated in {result.generation_time_ms}ms")

# Check if cached
if result.is_cached:
    print("Using cached explanation")

# Check model used
print(f"Model: {result.model_used}")

# Convert to JSON
json_output = result.to_dict()
```

## Health Advisory Reference

### Children Recommendations
- Avoid outdoor play during peak pollution
- Keep inhalers accessible
- Stay hydrated
- Watch for coughing/breathing difficulty

### Elderly Recommendations
- Minimize outdoor exposure
- Keep medications refilled
- Avoid early morning/evening outdoor time
- Consider air purifier indoors

### Athletes Recommendations
- Move training indoors
- Reduce intensity/duration
- Reschedule competitions
- Monitor respiratory symptoms

### Outdoor Workers Recommendations
- Use N95/P100 respirators
- Limit continuous outdoor time
- Increase hydration
- Monitor symptoms during shift
- Request duty modification if needed

## Prompt Examples

### What the system sends to LLM

**Explanation Prompt:**
```
System: [Safety guidelines, AQI interpretation rules, style context]

User: Generate an explanation for AQI 100 with rising trend, 
traffic as main factor, persistent duration, for general public 
in casual style.
```

**Advisory Prompt:**
```
System: [Health advisory guidelines, severity rules]

User: Generate health advisory for AQI 100, children persona,
with recommended actions.
```

## Error Handling

```python
try:
    result = explainer.generate_explanation(...)
except ValueError as e:
    # Invalid parameters
    print(f"Invalid input: {e}")
except Exception as e:
    # API or other error (fallback already attempted)
    print(f"Generation error: {e}")
    # Result still returned if fallback enabled
```

## Performance Tips

| Optimization | Time Saving | Implementation |
|--------------|-------------|-----------------|
| Enable cache | 50x faster | `use_cache=True` |
| Use templates | 100x faster | `provider=TEMPLATE` |
| Lower temperature | Faster API | `temperature=0.3` |
| Batch requests | Network savings | Process multiple at once |
| Async calls | Non-blocking | (Future enhancement) |

## Cost Calculation

```python
# OpenAI pricing (as of 2024)
gpt_3_5_turbo_cost = 0.0005  # USD per explanation
gpt_4_cost = 0.003            # USD per explanation

# For 10,000 explanations:
cost_3_5 = 10000 * gpt_3_5_turbo_cost  # $5.00
cost_4 = 10000 * gpt_4_cost             # $30.00
```

## Integration Checklist

- [ ] Import GenerativeExplainer
- [ ] Create LLMConfiguration
- [ ] Initialize GenerativeExplainer
- [ ] Call generate_explanation()
- [ ] Handle result.explanation
- [ ] Display result.health_advisory.message
- [ ] Show recommended_actions list
- [ ] Monitor result.provider_used
- [ ] Test with different personas
- [ ] Test with different styles

## Testing Command

```bash
# Run all tests
python -m pytest tests/test_generative_explainer.py -v

# Run specific test
python -m pytest tests/test_generative_explainer.py::TestGenerativeExplainer -v

# Run with coverage
python -m pytest tests/test_generative_explainer.py --cov=app.services.generative_explainer
```

## Running Examples

```bash
cd /path/to/AeroGuard
python examples/generative_explainer_examples.py
```

Runs 11 comprehensive examples showing:
1. Basic template usage
2. Children persona guidance
3. Athletes persona guidance
4. Different explanation styles
5. Outdoor workers guidance
6. Elderly persona guidance
7. Hazardous AQI level handling
8. Good air quality messaging
9. Factory function usage
10. Integration with explainability module
11. Health advisory only generation

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key not working | Verify format: `sk-...` |
| Falling back unexpectedly | Check `provider` setting and API key |
| Explanations too generic | Use specific factors, increase temperature |
| Cache not working | Verify `use_cache=True` |
| Timeout errors | Increase `timeout` parameter |
| Rate limiting | Set `max_retries`, use fallback |

## API Endpoints Mapping

If integrating into REST API:

```python
POST /api/explanations
{
    "aqi_value": 100.0,
    "trend": "rising",
    "main_factors": ["traffic"],
    "duration": "persistent",
    "persona": "general_public",
    "explanation_style": "casual"
}

Response:
{
    "explanation": "...",
    "health_advisory": {
        "message": "...",
        "severity": "High",
        "affected_groups": [...],
        "recommended_actions": [...]
    },
    "provider_used": "template",
    "generation_time_ms": 45
}
```

## Environment Setup

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# Or in Python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

# In code
config = LLMConfiguration(
    api_key=os.getenv("OPENAI_API_KEY"),
    provider=APIProvider.OPENAI
)
```

## Safety Checklist

✅ Module enforces:
- No medical diagnoses
- No treatment recommendations
- No medication advice
- Only preventive guidance
- Clear disclaimer language
- Reference to healthcare professionals

## Constants Reference

```python
# Explanation Styles
ExplanationStyle.TECHNICAL    # Detailed, metrics-focused
ExplanationStyle.CASUAL       # Conversational, simple
ExplanationStyle.URGENT       # Action-oriented, warnings
ExplanationStyle.REASSURING   # Balanced, positive

# API Providers
APIProvider.OPENAI            # OpenAI GPT models
APIProvider.TEMPLATE          # Template fallback
APIProvider.MOCK              # For testing

# Trend Values
"rising"     # AQI getting worse
"falling"    # AQI improving
"stable"     # AQI unchanged

# Duration Values
"temporary"  # Expected to improve soon
"persistent" # Expected to last hours/days

# Persona Values
"general_public"
"children"
"elderly"
"athletes"
"outdoor_workers"
```

## See Also

- [Full Documentation](GENERATIVE_EXPLAINER.md)
- [Usage Examples](../../examples/generative_explainer_examples.py)
- [Test Suite](../../tests/test_generative_explainer.py)
- [Explainability Module](EXPLAINABILITY.md)
