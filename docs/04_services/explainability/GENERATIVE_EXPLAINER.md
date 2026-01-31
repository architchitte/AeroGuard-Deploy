# Generative AI Explanation Generator

## Overview

The **GenerativeExplainer** is an intelligent explanation generation system that transforms raw AQI data into human-readable, contextually-aware health guidance. It combines LLM-powered explanations with a reliable template-based fallback system to ensure consistent, accurate information regardless of API availability.

**Key Features:**
- 🤖 LLM integration with OpenAI GPT models
- 📋 Intelligent template fallback when API unavailable
- 👥 5 persona-specific health guidance profiles
- 🎯 4 explanation styles (Technical, Casual, Urgent, Reassuring)
- ⚠️ Health advisory generation with severity assessment
- 🛡️ No medical claims - preventive guidance only
- 🔧 Easy configuration and factory function

## Architecture

### System Design

```
AQI Analysis Data
        │
        ▼
┌─────────────────────────────────────────┐
│      GenerativeExplainer                │
│  (Main Orchestration Class)             │
└─────────────────────────────────────────┘
        │
        ├─── LLM Provider ──────────────────────┐
        │     (Try OpenAI API)                 │
        │     ├─ PromptBuilder                 │
        │     └─ Error Handling                │
        │                                       │
        └─── Template Provider ────────────────┐
              (Fallback)
              ├─ TemplateExplainer
              └─ HealthAdvisory Generator

Output: GeneratedExplanation + HealthAdvisory
```

### Key Components

#### 1. **LLMConfiguration**
Encapsulates all LLM settings and API configuration.

```python
@dataclass
class LLMConfiguration:
    api_key: str = ""                          # OpenAI API key
    provider: APIProvider = APIProvider.TEMPLATE  # OPENAI, TEMPLATE, or MOCK
    model: str = "gpt-3.5-turbo"              # OpenAI model
    temperature: float = 0.7                   # Explanation temperature
    advisory_temperature: float = 0.5          # Advisory temperature
    max_retries: int = 2                       # API retry attempts
    timeout: int = 10                          # Request timeout
    use_cache: bool = True                     # Cache explanations
    fallback_to_template: bool = True          # Use template fallback
```

#### 2. **PromptBuilder**
Constructs optimized prompts for the LLM while maintaining consistency.

```python
class PromptBuilder:
    @staticmethod
    def build_explanation_prompt(...) -> str
        # Creates explanation prompt with:
        # - System safety guidelines
        # - AQI interpretation guidelines
        # - Style and persona context
        # - Clear structure requirements
    
    @staticmethod
    def build_advisory_prompt(...) -> str
        # Creates health advisory prompt with:
        # - Severity assessment logic
        # - Affected population identification
        # - Action recommendation framework
    
    @staticmethod
    def get_system_prompt() -> str
        # Returns consistent system prompt enforcing:
        # - No medical claims
        # - Preventive guidance only
        # - Clear, actionable advice
```

#### 3. **TemplateExplainer**
Provides reliable template-based fallback explanations.

```python
class TemplateExplainer:
    # Comprehensive template library covering:
    # - All AQI ranges (Good, Moderate, USG, Unhealthy, Hazardous)
    # - Trend patterns (Rising, Falling, Stable)
    # - Duration categories (Temporary, Persistent)
    
    # Persona-specific recommendations for:
    # - General public
    # - Children
    # - Elderly
    # - Athletes
    # - Outdoor workers
```

#### 4. **HealthAdvisory**
Structured health guidance with metadata.

```python
@dataclass
class HealthAdvisory:
    message: str                           # Primary advisory message
    severity: str                          # "Low", "Moderate", "High", "Critical"
    affected_groups: List[str]             # Vulnerable populations
    recommended_actions: List[str]         # Specific actions to take
```

#### 5. **GeneratedExplanation**
Complete explanation output with metadata.

```python
@dataclass
class GeneratedExplanation:
    explanation: str                       # Human-readable explanation
    health_advisory: HealthAdvisory        # Structured health guidance
    explanation_style: ExplanationStyle    # Style used (if specified)
    provider_used: APIProvider             # Which provider generated this
    is_cached: bool = False                # Was this retrieved from cache?
    model_used: str = ""                   # Which LLM model was used
    generation_time_ms: int = 0            # How long generation took
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
```

#### 6. **GenerativeExplainer**
Main orchestrator class.

```python
class GenerativeExplainer:
    def generate_explanation(
        self,
        aqi_value: float,
        trend: str,
        main_factors: List[str],
        duration: str,
        persona: str = "general_public",
        explanation_style: ExplanationStyle = None,
        include_health_advisory: bool = True
    ) -> GeneratedExplanation:
        """
        Generate comprehensive explanation with health advisory.
        
        Flow:
        1. Try LLM if configured and cached not found
        2. Fall back to template on API error
        3. Generate health advisory (LLM or template)
        4. Return GeneratedExplanation with metadata
        """
    
    def generate_health_advisory_only(
        self,
        aqi_value: float,
        persona: str = "general_public",
        explanation_style: ExplanationStyle = None
    ) -> GeneratedExplanation:
        """Generate health advisory without explanation"""
```

## Usage Patterns

### Pattern 1: Basic Usage (Template Provider)

```python
from app.services.generative_explainer import (
    GenerativeExplainer,
    LLMConfiguration,
    APIProvider
)

# Create configuration (no API key needed for template)
config = LLMConfiguration(provider=APIProvider.TEMPLATE)

# Create explainer
explainer = GenerativeExplainer(config)

# Generate explanation
result = explainer.generate_explanation(
    aqi_value=100.0,
    trend="rising",
    main_factors=["traffic", "industrial"],
    duration="persistent",
    persona="general_public"
)

# Use the result
print(result.explanation)
print(result.health_advisory.message)
```

### Pattern 2: LLM Integration with API Key

```python
import os

# Configure with OpenAI API
config = LLMConfiguration(
    api_key=os.getenv("OPENAI_API_KEY"),
    provider=APIProvider.OPENAI,
    model="gpt-4",
    temperature=0.7,
    fallback_to_template=True  # Auto-fallback if API fails
)

explainer = GenerativeExplainer(config)

# Generate - will use OpenAI, fall back to template if needed
result = explainer.generate_explanation(
    aqi_value=80.0,
    trend="rising",
    main_factors=["traffic"],
    duration="temporary",
    persona="children"
)
```

### Pattern 3: Explanation Style Control

```python
from app.services.generative_explainer import ExplanationStyle

explainer = GenerativeExplainer(config)

# Casual style for general audience
result_casual = explainer.generate_explanation(
    aqi_value=90.0,
    trend="rising",
    main_factors=["dust"],
    duration="persistent",
    persona="general_public",
    explanation_style=ExplanationStyle.CASUAL
)

# Technical style for detailed analysis
result_technical = explainer.generate_explanation(
    aqi_value=90.0,
    trend="rising",
    main_factors=["dust"],
    duration="persistent",
    persona="general_public",
    explanation_style=ExplanationStyle.TECHNICAL
)

# Urgent style for hazardous conditions
result_urgent = explainer.generate_explanation(
    aqi_value=90.0,
    trend="rising",
    main_factors=["dust"],
    duration="persistent",
    persona="general_public",
    explanation_style=ExplanationStyle.URGENT
)
```

### Pattern 4: Persona-Specific Guidance

```python
# Different personas receive tailored advice
personas = ["general_public", "children", "elderly", "athletes", "outdoor_workers"]

for persona in personas:
    result = explainer.generate_explanation(
        aqi_value=100.0,
        trend="rising",
        main_factors=["industrial"],
        duration="persistent",
        persona=persona
    )
    print(f"\n{persona.upper()}:")
    print(result.health_advisory.message)
    for action in result.health_advisory.recommended_actions:
        print(f"  • {action}")
```

### Pattern 5: Health Advisory Only

```python
# Generate only advisory (when explanation provided separately)
advisory_result = explainer.generate_health_advisory_only(
    aqi_value=120.0,
    persona="children"
)

print(advisory_result.health_advisory.severity)
print(advisory_result.health_advisory.message)
```

### Pattern 6: Factory Function

```python
from app.services.generative_explainer import create_generative_explainer

# Quick creation with sensible defaults
explainer = create_generative_explainer()

# Or with custom configuration
explainer = create_generative_explainer(
    api_key="your-api-key",
    model="gpt-4",
    provider="openai"
)
```

## Configuration Guide

### OpenAI Setup

1. **Get API Key:**
   ```bash
   # Set environment variable
   export OPENAI_API_KEY="sk-..."
   ```

2. **Configure in Code:**
   ```python
   import os
   
   config = LLMConfiguration(
       api_key=os.getenv("OPENAI_API_KEY"),
       provider=APIProvider.OPENAI,
       model="gpt-3.5-turbo",  # or gpt-4
       temperature=0.7
   )
   ```

3. **Handle API Errors:**
   ```python
   config = LLMConfiguration(
       api_key="your-key",
       provider=APIProvider.OPENAI,
       fallback_to_template=True,  # Automatic fallback
       max_retries=3               # Retry on timeout
   )
   ```

### Temperature Tuning

- **Explanations** (default 0.7): Higher variability, more creative
  - Lower (0.3-0.5): More consistent, deterministic
  - Higher (0.7-0.9): More varied, conversational
  
- **Health Advisories** (default 0.5): More conservative
  - Lower (0.2-0.4): Very consistent recommendations
  - Higher (0.6-0.8): More varied suggestions

### Caching Strategy

```python
# Enable caching for repeated AQI scenarios
config = LLMConfiguration(
    use_cache=True,
    provider=APIProvider.OPENAI
)

explainer = GenerativeExplainer(config)

# Same input twice - second call uses cache
result1 = explainer.generate_explanation(...)
result2 = explainer.generate_explanation(...)  # From cache

# Check if result came from cache
if result2.is_cached:
    print("Using cached explanation")
```

## Explanation Styles

### 1. TECHNICAL
- Detailed, technical language
- Reference actual metrics
- Suitable for: Air quality professionals, detailed reporting
- Example output: "AQI of 120 indicates unhealthy conditions with primary pollutant being PM2.5..."

### 2. CASUAL
- Conversational tone
- Simpler language
- Suitable for: General public, social media
- Example output: "The air quality is pretty rough right now - it's not a great day to be outside."

### 3. URGENT
- Action-oriented language
- Emphasizes health risks
- Suitable for: Hazardous AQI levels, vulnerable groups
- Example output: "Air quality has reached hazardous levels. Limit outdoor activities immediately."

### 4. REASSURING
- Balanced, positive tone
- Acknowledges concerns but provides perspective
- Suitable for: Good air quality, recovery scenarios
- Example output: "The air quality is looking good today! Outdoor activities are safe."

## Personas and Health Guidance

### General Public
**Focus:** Basic health protection and activity guidance
**Key Actions:**
- Reduce prolonged outdoor exertion
- Keep medication accessible
- Use N95 masks if needed

### Children
**Focus:** Vulnerable respiratory system protection
**Key Actions:**
- Avoid outdoor play during peak hours
- Limit strenuous activities
- Keep indoor activities available
- Monitor for respiratory symptoms

### Elderly
**Focus:** Pre-existing condition management
**Key Actions:**
- Minimize outdoor exposure
- Keep medications refilled
- Avoid early morning/evening outdoor time
- Stay hydrated

### Athletes
**Focus:** Training adjustment and activity planning
**Key Actions:**
- Move training indoors
- Adjust intensity levels
- Reschedule outdoor competitions
- Monitor respiratory symptoms

### Outdoor Workers
**Focus:** Occupational safety and health protection
**Key Actions:**
- Use proper respiratory protection (N95/P100)
- Limit continuous outdoor time
- Increase hydration
- Monitor symptoms throughout shift
- Request duty modification if necessary

## Health Advisory Severity Levels

```
┌──────────┬───────┬────────────────────────────────┐
│ AQI      │ Level │ Severity in Advisory           │
├──────────┼───────┼────────────────────────────────┤
│ 0-50     │ Good  │ "Low" - Normal activity safe   │
│ 51-100   │ Mod   │ "Low" - Sensitive groups limit │
│ 101-150  │ USG   │ "Moderate" - Most limit        │
│ 151-200  │ Unhhy │ "High" - Avoid outdoor         │
│ 201+     │ Haz   │ "Critical" - Stay indoors      │
└──────────┴───────┴────────────────────────────────┘
```

## Error Handling and Fallback

### Automatic Fallback Behavior

```python
# LLM → Template → Default Message

result = explainer.generate_explanation(...)

# Result will include which provider was actually used
print(f"Used: {result.provider_used}")  # OPENAI, TEMPLATE, or MOCK

# On API error with fallback enabled:
# 1. Try OpenAI API (max 3 retries)
# 2. Fall back to template on failure
# 3. Return reliable explanation
# 4. Log provider used
```

### Retry Logic

```python
config = LLMConfiguration(
    api_key="your-key",
    provider=APIProvider.OPENAI,
    max_retries=3,
    timeout=10
)

# Will automatically retry up to 3 times on:
# - Connection timeout
# - Rate limit (with exponential backoff)
# - Server errors (5xx)

# Won't retry on:
# - Invalid API key (falls back immediately)
# - Malformed input
```

## Integration with Explainability Module

### Typical Workflow

```python
from app.services.explainability import create_health_risk_classifier
from app.services.generative_explainer import (
    GenerativeExplainer,
    LLMConfiguration,
    APIProvider,
    ExplanationStyle
)

# Step 1: Analyze with explainability module
classifier = create_health_risk_classifier()
aqi_value = 95.0

health_risk = classifier.classify_health_risk(aqi_value)
print(f"Risk Level: {health_risk.level}")
print(f"Main Factors: {health_risk.main_factors}")

# Step 2: Generate explanation with generative explainer
config = LLMConfiguration(provider=APIProvider.TEMPLATE)
explainer = GenerativeExplainer(config)

result = explainer.generate_explanation(
    aqi_value=aqi_value,
    trend="rising",
    main_factors=health_risk.main_factors,
    duration="temporary",
    persona="general_public"
)

# Step 3: Present combined output to user
print(f"\n{result.explanation}\n")
print(f"⚠️ {result.health_advisory.message}\n")
print("Recommended Actions:")
for action in result.health_advisory.recommended_actions:
    print(f"  • {action}")
```

## API Reference

### GenerativeExplainer.generate_explanation()

```python
def generate_explanation(
    self,
    aqi_value: float,
    trend: str,
    main_factors: List[str],
    duration: str,
    persona: str = "general_public",
    explanation_style: ExplanationStyle = None,
    include_health_advisory: bool = True
) -> GeneratedExplanation:
    """
    Generate human-readable explanation with health advisory.
    
    Parameters:
        aqi_value (float): AQI value (0-500+)
        trend (str): "rising", "falling", or "stable"
        main_factors (List[str]): Primary pollution factors
            - Valid: "traffic", "industrial", "dust", "wildfire", etc.
        duration (str): "temporary" or "persistent"
        persona (str): One of:
            - "general_public" (default)
            - "children"
            - "elderly"
            - "athletes"
            - "outdoor_workers"
        explanation_style (ExplanationStyle): Optional style override
            - TECHNICAL, CASUAL, URGENT, REASSURING
        include_health_advisory (bool): Include health advisory in result
    
    Returns:
        GeneratedExplanation: Complete explanation with advisory
    
    Raises:
        ValueError: Invalid parameters
        APIError: API failure (if fallback disabled)
    """
```

### GenerativeExplainer.generate_health_advisory_only()

```python
def generate_health_advisory_only(
    self,
    aqi_value: float,
    persona: str = "general_public",
    explanation_style: ExplanationStyle = None
) -> GeneratedExplanation:
    """
    Generate only health advisory without explanation.
    
    Parameters:
        aqi_value (float): AQI value
        persona (str): Target population
        explanation_style (ExplanationStyle): Style override
    
    Returns:
        GeneratedExplanation: Advisory only (explanation field empty)
    """
```

### GeneratedExplanation.to_dict()

```python
def to_dict(self) -> Dict[str, Any]:
    """
    Convert to JSON-serializable dictionary.
    
    Returns:
        Dict with keys:
        - explanation (str)
        - health_advisory (dict with keys: message, severity, affected_groups, recommended_actions)
        - explanation_style (str)
        - provider_used (str)
        - is_cached (bool)
        - model_used (str)
        - generation_time_ms (int)
    """
```

## Performance and Optimization

### Response Times

- **Template Provider:** 10-50ms
- **OpenAI API (cached):** 50-100ms
- **OpenAI API (fresh):** 500-2000ms

### Cost Estimation (OpenAI)

```
GPT-3.5-turbo:
- ~0.0005 USD per explanation
- ~0.0002 USD per advisory
- ~1000 explanations per dollar

GPT-4:
- ~0.003 USD per explanation
- ~0.001 USD per advisory
- ~300 explanations per dollar
```

### Optimization Tips

1. **Enable Caching:** Reduces API calls for repeated scenarios
2. **Batch Requests:** Generate multiple explanations in one session
3. **Use Templates for:** High-volume, time-sensitive applications
4. **Use OpenAI for:** Personalization, special cases, training
5. **Monitor Costs:** Track API usage, set spending alerts

## Troubleshooting

### Issue: API Key Not Working

```python
# Solution: Verify key is set correctly
import os

api_key = os.getenv("OPENAI_API_KEY")
assert api_key, "OPENAI_API_KEY not set"
assert api_key.startswith("sk-"), "Invalid key format"

config = LLMConfiguration(api_key=api_key)
```

### Issue: Explanations Too Generic

```python
# Solution: Use specific factors and tune temperature
result = explainer.generate_explanation(
    aqi_value=100,
    trend="rising",
    main_factors=["wildfire_smoke"],  # Specific factor
    duration="persistent",
    explanation_style=ExplanationStyle.TECHNICAL  # More detailed
)

# Or adjust temperature for more variation
config = LLMConfiguration(temperature=0.8)  # Higher = more creative
```

### Issue: Falling Back to Template Unexpectedly

```python
# Solution: Check API configuration
config.api_key  # Verify key is set
config.provider  # Should be OPENAI if using API
config.fallback_to_template  # True allows fallback

# Debug: Check which provider was used
print(f"Provider used: {result.provider_used}")
print(f"Model used: {result.model_used}")
```

## Testing

The module includes 35 comprehensive tests covering:
- Configuration management
- Prompt building
- Template generation
- Health advisory generation
- LLM integration
- Style handling
- Persona-specific guidance
- Edge cases
- Factory function

Run tests:
```bash
python -m pytest tests/test_generative_explainer.py -v
```

## Best Practices

1. **Always Set Fallback:** Enable `fallback_to_template=True` for production
2. **Validate Input:** Check AQI values, trends, and factors before generation
3. **Cache Results:** Enable caching for improved performance
4. **Monitor Errors:** Log provider used and generation time
5. **Test Personas:** Verify your target audience's guidance is appropriate
6. **Regular Audits:** Review generated explanations for accuracy
7. **Cost Control:** Set API spending limits with OpenAI
8. **Version Pin:** Specify model version for reproducibility

## Safety Guidelines

The system enforces:
- ✅ No medical diagnoses
- ✅ No treatment recommendations
- ✅ No medication advice
- ✅ Only preventive guidance
- ✅ Clear disclaimer language
- ✅ Emphasis on consulting healthcare professionals

## Future Enhancements

- [ ] Multi-language support
- [ ] Voice output integration
- [ ] Custom persona creation
- [ ] A/B testing framework
- [ ] Advanced caching with Redis
- [ ] Streaming response support
- [ ] Custom prompt templates
- [ ] Analytics and monitoring dashboard
