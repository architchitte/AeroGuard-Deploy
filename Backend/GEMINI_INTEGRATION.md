# Google Gemini Integration Guide

## ✅ Changes Complete

### 1. Environment Configuration
- **Changed**: `OPENAI_API_KEY` → `GEMINI_API_KEY`
- **Changed**: `OPENAI_MODEL` → `GEMINI_MODEL`
- **Default Model**: `gemini-pro` (free tier available)
- **Location**: `.env` and `.env.example`

### 2. Dependencies Updated
- **Added**: `google-generativeai==0.3.0`
- **Removed**: OpenAI dependency
- **Install**: `pip install -r requirements.txt`

### 3. Code Changes
**File**: [app/services/generative_explainer.py](app/services/generative_explainer.py)

- Updated `APIProvider` enum: `OPENAI` → `GEMINI`
- Updated `LLMConfiguration` defaults for Gemini
- Switched API calls from `ChatCompletion` to `GenerativeModel`
- Simplified configuration (no chat format needed)
- Maintained template-based fallback for robustness

---

## 🚀 Quick Start

### Step 1: Get Your API Key
1. Visit: https://ai.google.dev/
2. Click "Get API Key" button
3. Create new project (if needed)
4. Copy your API key

### Step 2: Configure .env
```bash
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-pro
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Test Integration
```python
from app.services.generative_explainer import create_generative_explainer

explainer = create_generative_explainer(api_key="your-key-here")

result = explainer.generate_explanation(
    aqi_value=150,
    trend="rising",
    main_factors=["PM2.5", "NO2"],
    duration="persistent",
    persona="elderly"
)

print(result.explanation)
print(result.health_advisory.message)
```

---

## 📊 Available Models

| Model | Free Access | Context | Speed | Best For |
|-------|-------------|---------|-------|----------|
| **gemini-pro** | ✅ Yes | 30K tokens | Fast ⚡ | **Text (recommended)** |
| gemini-pro-vision | ✅ Yes | 30K tokens | Medium | Images + text |

---

## 🔄 Key Differences from OpenAI

### OpenAI (Old)
```python
import openai
openai.api_key = "sk-..."

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are..."},
        {"role": "user", "content": "Generate..."}
    ],
    temperature=0.7,
    max_tokens=500,
    top_p=0.95,
    frequency_penalty=0.0,
    presence_penalty=0.0
)
```

### Gemini (New)
```python
import google.generativeai as genai
genai.configure(api_key="...")

model = genai.GenerativeModel("gemini-pro")
response = model.generate_content(
    prompt,
    generation_config=genai.types.GenerationConfig(
        temperature=0.7,
        max_output_tokens=500,
        top_p=0.95
    )
)
```

**Advantages**:
- ✅ Simpler API (no chat format)
- ✅ Fewer configuration options
- ✅ Built-in safety filtering
- ✅ Better multi-language support
- ✅ Free tier for development

---

## 🛡️ Fallback Behavior

The system automatically handles failures gracefully:

```
Gemini API Called
    ↓
[Success] → Return AI-generated explanation
    ↓
[Failure] → Template-based explanation
    ↓
[Result] → Full response to user (no visible difference)
```

**Benefits**:
- ✅ No crashes if API is down
- ✅ Works without API key
- ✅ Same response format for both paths
- ✅ Transparent failover

---

## 💡 Usage Examples

### Basic Usage
```python
from app.services.generative_explainer import create_generative_explainer

# Create explainer
explainer = create_generative_explainer(
    api_key="your-gemini-key",
    model="gemini-pro"
)

# Generate explanation
explanation = explainer.generate_explanation(
    aqi_value=75,
    trend="stable",
    main_factors=["PM2.5"],
    duration="temporary"
)
```

### Health Advisory Only
```python
# Generate just the health advisory
advisory = explainer.generate_health_advisory_only(
    aqi_value=150,
    persona="children"
)

print(f"Severity: {advisory.severity}")
print(f"Message: {advisory.message}")
print(f"Actions: {advisory.recommended_actions}")
```

### Custom Configuration
```python
from app.services.generative_explainer import LLMConfiguration, APIProvider

config = LLMConfiguration(
    provider=APIProvider.GEMINI,
    api_key="your-key",
    model="gemini-pro",
    temperature=0.5,  # More deterministic
    max_tokens=300    # Shorter responses
)

explainer = GenerativeExplainer(config)
```

---

## 🔧 Configuration Options

**LLMConfiguration parameters**:

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `provider` | APIProvider | GEMINI | Use APIProvider.GEMINI |
| `api_key` | str | None | Required for Gemini |
| `model` | str | gemini-pro | Model to use |
| `temperature` | float | 0.7 | 0 (deterministic) to 1 (creative) |
| `max_tokens` | int | 500 | Max response length |
| `top_p` | float | 0.95 | Nucleus sampling |
| `use_fallback` | bool | True | Use template if API fails |
| `retry_count` | int | 2 | Retry attempts |

---

## 🐛 Troubleshooting

### Issue: "google-generativeai package not installed"
```bash
pip install google-generativeai==0.3.0
```

### Issue: "Invalid API key"
```bash
# Check your .env file
cat .env | grep GEMINI_API_KEY

# Visit https://ai.google.dev/ to get a valid key
```

### Issue: API returns empty response
```python
# Check if model is available in your region
# Fallback will automatically use template-based explanation
```

### Issue: Rate limit exceeded
```bash
# Add retry logic in your application
# Current implementation includes 2 retries by default
```

---

## 📚 Resources

- **Google Gemini API**: https://ai.google.dev/
- **API Documentation**: https://ai.google.dev/docs
- **Python Client**: https://github.com/google/generative-ai-python
- **Pricing**: Free tier available for development

---

## ✨ Summary

| Aspect | Old (OpenAI) | New (Gemini) |
|--------|--------------|-------------|
| **API** | ChatCompletion | GenerativeModel |
| **Free Tier** | ❌ No | ✅ Yes |
| **Setup** | Complex | Simple |
| **Context Window** | 4K-128K | 30K |
| **Cost** | Paid | Free (for dev) |
| **Reliability** | High | High |

All changes are backward compatible with the existing fallback system!
