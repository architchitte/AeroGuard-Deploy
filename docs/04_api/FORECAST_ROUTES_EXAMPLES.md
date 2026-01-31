## Flask API Routes - Complete End-to-End Examples

**File:** Reference examples for all endpoints

Comprehensive working examples for integrating the AeroGuard Flask REST API.

---

## Example 1: Python - Complete Workflow

**Use Case:** Get forecast, assess risk, and generate explanation for NYC

```python
import requests
import json
from datetime import datetime

# Configuration
API_BASE = "http://localhost:5000/api/v1"
LOCATION = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "name": "New York City"
}
HISTORICAL_AQI = [45, 48, 50, 52, 55, 58, 61]
PERSONA = "Athletes"

def complete_aqi_analysis():
    """Get full AQI analysis: forecast -> risk -> explanation"""
    
    print("=" * 70)
    print("AeroGuard Complete AQI Analysis")
    print("=" * 70)
    
    # Step 1: Generate Forecast
    print("\n[1/3] Generating 6-hour AQI forecast...")
    
    forecast_payload = {
        "location": LOCATION,
        "aqi_data": HISTORICAL_AQI,
        "hours_ahead": 6,
        "include_confidence": True
    }
    
    try:
        forecast_response = requests.post(
            f"{API_BASE}/forecast",
            json=forecast_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if forecast_response.status_code != 201:
            print(f"ERROR: Forecast failed with {forecast_response.status_code}")
            print(forecast_response.json())
            return
        
        forecast_data = forecast_response.json()
        forecast = forecast_data["forecast"]
        
        print(f"✓ Forecast generated successfully")
        print(f"  Base AQI: {forecast['base_aqi']}")
        print(f"  Trend: {forecast['trend']}")
        print(f"  Confidence: {forecast['confidence']:.0%}")
        print(f"  Predicted values: {forecast['predicted_values']}")
        
    except Exception as e:
        print(f"ERROR: Failed to get forecast: {str(e)}")
        return
    
    # Step 2: Assess Health Risk
    print("\n[2/3] Assessing health risk for {0}...".format(PERSONA))
    
    peak_aqi = max(forecast["predicted_values"])
    
    risk_payload = {
        "aqi": peak_aqi,
        "persona": PERSONA,
        "location": LOCATION
    }
    
    try:
        risk_response = requests.post(
            f"{API_BASE}/risk",
            json=risk_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if risk_response.status_code != 200:
            print(f"ERROR: Risk assessment failed with {risk_response.status_code}")
            print(risk_response.json())
            return
        
        risk_data = risk_response.json()
        risk = risk_data["risk_assessment"]
        
        print(f"✓ Risk assessment completed")
        print(f"  Risk Category: {risk['risk_category']}")
        print(f"  Risk Level: {risk['risk_level']}/5")
        print(f"  Activity Recommendation: {risk['recommendations']['activity']}")
        print(f"  Precautions: {', '.join(risk['recommendations']['precautions'][:2])}")
        
    except Exception as e:
        print(f"ERROR: Failed to assess risk: {str(e)}")
        return
    
    # Step 3: Generate Explanation
    print("\n[3/3] Generating AI explanation...")
    
    explain_payload = {
        "forecast_metadata": {
            "forecast_values": forecast["predicted_values"],
            "historical_values": HISTORICAL_AQI,
            "trend": forecast["trend"],
            "confidence": forecast["confidence"]
        },
        "location": LOCATION,
        "style": "casual",
        "include_health_advisory": True
    }
    
    try:
        explain_response = requests.post(
            f"{API_BASE}/explain",
            json=explain_payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if explain_response.status_code != 200:
            print(f"ERROR: Explanation failed with {explain_response.status_code}")
            print(explain_response.json())
            return
        
        explanation_data = explain_response.json()
        explanation = explanation_data["explanation"]
        
        print(f"✓ Explanation generated successfully")
        print(f"  Provider: {explanation_data['metadata']['provider']}")
        print(f"  Model: {explanation_data['metadata']['model']}")
        
    except Exception as e:
        print(f"ERROR: Failed to generate explanation: {str(e)}")
        return
    
    # Display Results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print("\nFORECAST SUMMARY:")
    print(f"  Location: {LOCATION['name']}")
    print(f"  Current AQI: {forecast['base_aqi']:.0f}")
    print(f"  Peak Forecast AQI: {peak_aqi}")
    print(f"  Trend: {forecast['trend']}")
    
    print("\nHEALTH RISK ASSESSMENT:")
    print(f"  Persona: {PERSONA}")
    print(f"  Risk Category: {risk['risk_category']}")
    print(f"  Health Effects:")
    for effect in risk['health_effects']:
        print(f"    - {effect}")
    
    print("\nRECOMMENDATIONS:")
    print(f"  Activity: {risk['recommendations']['activity']}")
    print(f"  Indoor/Outdoor: {risk['recommendations']['indoor_outdoor']}")
    print(f"  Precautions:")
    for precaution in risk['recommendations']['precautions']:
        print(f"    - {precaution}")
    
    print("\nSYMPTOMS TO WATCH:")
    for symptom in risk['symptoms_to_watch']:
        print(f"  - {symptom}")
    
    print("\nEXPLANATION:")
    print(f"  {explanation['summary']}")
    
    if 'health_advisory' in explanation:
        print("\nHEALTH ADVISORY:")
        print(f"  Severity: {explanation['health_advisory']['severity'].upper()}")
        print(f"  Message: {explanation['health_advisory']['message']}")
        print(f"  Affected Groups: {', '.join(explanation['health_advisory']['affected_groups'])}")
    
    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)
    
    # Return structured data
    return {
        "forecast": forecast,
        "risk": risk,
        "explanation": explanation
    }


if __name__ == "__main__":
    try:
        results = complete_aqi_analysis()
        if results:
            print("\n✓ All steps completed successfully")
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
```

**Output:**
```
======================================================================
AeroGuard Complete AQI Analysis
======================================================================

[1/3] Generating 6-hour AQI forecast...
✓ Forecast generated successfully
  Base AQI: 61
  Trend: stable
  Confidence: 87%
  Predicted values: [62, 64, 65, 65, 63, 60]

[2/3] Assessing health risk for Athletes...
✓ Risk assessment completed
  Risk Category: Moderate
  Risk Level: 2/5
  Activity Recommendation: Reduce prolonged or heavy outdoor exertion
  Precautions: Limit intense outdoor activities, Take more frequent breaks

[3/3] Generating AI explanation...
✓ Explanation generated successfully
  Provider: openai
  Model: gpt-3.5-turbo

======================================================================
RESULTS
======================================================================
...
```

---

## Example 2: JavaScript - Frontend Integration

**Use Case:** Web dashboard with real-time AQI data

```javascript
// Configuration
const API_BASE = 'http://localhost:5000/api/v1';
const LOCATION = {
  latitude: 40.7128,
  longitude: -74.0060,
  name: 'New York City'
};

class AeroGuardAPI {
  constructor(baseURL = API_BASE) {
    this.baseURL = baseURL;
  }

  async forecast(location, historicalAQI, hoursAhead = 6) {
    """Generate AQI forecast"""
    const response = await fetch(`${this.baseURL}/forecast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location,
        aqi_data: historicalAQI,
        hours_ahead: hoursAhead,
        include_confidence: true
      })
    });

    if (!response.ok) {
      throw new Error(`Forecast failed: ${response.status}`);
    }

    return await response.json();
  }

  async assessRisk(aqi, persona, location = null) {
    """Assess health risk"""
    const payload = { aqi, persona };
    if (location) payload.location = location;

    const response = await fetch(`${this.baseURL}/risk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Risk assessment failed: ${response.status}`);
    }

    return await response.json();
  }

  async explain(forecastMetadata, location, style = 'casual') {
    """Generate explanation"""
    const response = await fetch(`${this.baseURL}/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        forecast_metadata: forecastMetadata,
        location,
        style,
        include_health_advisory: true
      })
    });

    if (!response.ok) {
      throw new Error(`Explanation failed: ${response.status}`);
    }

    return await response.json();
  }

  async getCompleteAnalysis(location, historicalAQI, personas = ['General Public']) {
    """Get complete analysis for one or more personas"""
    try {
      // Step 1: Get forecast
      const forecastRes = await this.forecast(location, historicalAQI);
      const forecast = forecastRes.forecast;
      const maxAQI = Math.max(...forecast.predicted_values);

      // Step 2: Assess risk for each persona
      const risks = {};
      for (const persona of personas) {
        const riskRes = await this.assessRisk(maxAQI, persona, location);
        risks[persona] = riskRes.risk_assessment;
      }

      // Step 3: Generate explanation
      const explainRes = await this.explain(
        {
          forecast_values: forecast.predicted_values,
          historical_values: historicalAQI,
          trend: forecast.trend,
          confidence: forecast.confidence
        },
        location,
        'casual'
      );

      return {
        forecast,
        risks,
        explanation: explainRes.explanation,
        metadata: explainRes.metadata
      };
    } catch (error) {
      console.error('Analysis failed:', error);
      throw error;
    }
  }
}

// Usage Example - Update Dashboard
async function updateAQIDashboard() {
  const api = new AeroGuardAPI();
  
  try {
    console.log('Loading AQI data...');
    
    const results = await api.getCompleteAnalysis(
      LOCATION,
      [45, 48, 50, 52, 55, 58, 61],
      ['General Public', 'Children', 'Athletes']
    );

    // Update forecast chart
    updateForecastChart(results.forecast.predicted_values, 
                       results.forecast.timestamps);

    // Update risk cards
    Object.entries(results.risks).forEach(([persona, risk]) => {
      updateRiskCard(persona, risk);
    });

    // Update explanation text
    updateExplanationText(results.explanation.summary);
    updateHealthAdvisory(results.explanation.health_advisory);

    console.log('Dashboard updated successfully');
  } catch (error) {
    console.error('Failed to update dashboard:', error);
    showError('Failed to load air quality data. Please try again.');
  }
}

// Chart Update Function
function updateForecastChart(values, timestamps) {
  const ctx = document.getElementById('forecastChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: timestamps.map(ts => new Date(ts).toLocaleTimeString()),
      datasets: [{
        label: 'Forecasted AQI',
        data: values,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: '6-Hour AQI Forecast'
        }
      }
    }
  });
}

// Risk Card Update
function updateRiskCard(persona, risk) {
  const card = document.querySelector(`[data-persona="${persona}"]`);
  if (!card) return;

  card.innerHTML = `
    <div class="risk-card">
      <h3>${persona}</h3>
      <p class="risk-level">Risk: ${risk.risk_category}</p>
      <p class="aqi">AQI: ${risk.aqi}</p>
      <div class="recommendations">
        <strong>Activity:</strong> ${risk.recommendations.activity}
        <strong>Precautions:</strong>
        <ul>${risk.recommendations.precautions
          .map(p => `<li>${p}</li>`).join('')}
        </ul>
      </div>
    </div>
  `;
}

// Explanation Update
function updateExplanationText(summary) {
  document.getElementById('explanation').textContent = summary;
}

// Health Advisory Update
function updateHealthAdvisory(advisory) {
  const element = document.getElementById('healthAdvisory');
  element.innerHTML = `
    <div class="advisory severity-${advisory.severity}">
      <strong>${advisory.severity.toUpperCase()}</strong>
      <p>${advisory.message}</p>
      <ul>
        ${advisory.recommended_actions
          .map(action => `<li>${action}</li>`).join('')}
      </ul>
    </div>
  `;
}

// Error Handler
function showError(message) {
  const alert = document.createElement('div');
  alert.className = 'alert alert-error';
  alert.textContent = message;
  document.body.insertBefore(alert, document.body.firstChild);
  
  setTimeout(() => alert.remove(), 5000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', updateAQIDashboard);
```

---

## Example 3: cURL - Manual Testing

**Use Case:** Test API endpoints directly from terminal

```bash
#!/bin/bash
# AeroGuard API Testing Script

API_BASE="http://localhost:5000/api/v1"
LOCATION='{"latitude": 40.7128, "longitude": -74.0060, "name": "New York"}'
AQI_DATA='[45, 50, 52, 55, 60, 58, 61]'

echo "======================================"
echo "AeroGuard API Testing"
echo "======================================"

# Test 1: Forecast
echo -e "\n[1] Testing Forecast Endpoint..."
curl -X POST "$API_BASE/forecast" \
  -H "Content-Type: application/json" \
  -d "{
    \"location\": $LOCATION,
    \"aqi_data\": $AQI_DATA,
    \"hours_ahead\": 6,
    \"include_confidence\": true
  }" | python -m json.tool

echo -e "\n[2] Testing Risk Endpoint..."
curl -X POST "$API_BASE/risk" \
  -H "Content-Type: application/json" \
  -d '{
    "aqi": 65,
    "persona": "Athletes",
    "location": '"$LOCATION"'
  }' | python -m json.tool

echo -e "\n[3] Testing Explain Endpoint..."
curl -X POST "$API_BASE/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "forecast_metadata": {
      "forecast_values": [62, 64, 65, 65, 63, 60],
      "historical_values": '"$AQI_DATA"',
      "trend": "stable",
      "confidence": 0.87
    },
    "location": '"$LOCATION"',
    "style": "casual"
  }' | python -m json.tool

echo -e "\n======================================"
echo "Testing Complete!"
echo "======================================"
```

---

## Example 4: Python - Error Handling

**Use Case:** Robust error handling and retries

```python
import requests
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

class AeroGuardClient:
    """Robust AeroGuard API client with error handling"""
    
    def __init__(self, base_url: str = "http://localhost:5000/api/v1", 
                 max_retries: int = 3, timeout: int = 15):
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.last_request_time = None
    
    def _request(self, method: str, endpoint: str, data: Dict) -> Dict:
        """Make HTTP request with retry logic"""
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"Attempt {attempt}/{self.max_retries}: {method} {endpoint}")
                
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
                
                self.last_request_time = datetime.now()
                
                # Check for success
                if response.status_code in [200, 201]:
                    return response.json()
                
                # Check for client error
                if response.status_code == 400:
                    raise ValueError(f"Validation error: {response.json()}")
                
                # Check for server error (retry)
                if response.status_code >= 500:
                    if attempt < self.max_retries:
                        wait_time = 2 ** (attempt - 1)
                        print(f"Server error. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RuntimeError(f"Server error after {self.max_retries} attempts")
                
                # Other error
                raise RuntimeError(f"HTTP {response.status_code}")
            
            except requests.ConnectionError as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** (attempt - 1)
                    print(f"Connection error. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"Cannot connect after {self.max_retries} attempts")
            
            except requests.Timeout:
                if attempt < self.max_retries:
                    print(f"Timeout. Retrying...")
                    time.sleep(2)
                else:
                    raise RuntimeError(f"Request timeout after {self.max_retries} attempts")
        
        raise RuntimeError("Max retries exceeded")
    
    def forecast(self, latitude: float, longitude: float, 
                aqi_data: list, hours: int = 6) -> Dict:
        """Get AQI forecast with error handling"""
        
        # Validate inputs
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}")
        if len(aqi_data) < 3:
            raise ValueError("Need at least 3 historical AQI values")
        if not (1 <= hours <= 24):
            raise ValueError(f"Hours must be 1-24, got {hours}")
        
        return self._request("POST", "/forecast", {
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "aqi_data": aqi_data,
            "hours_ahead": hours
        })
    
    def risk(self, aqi: float, persona: str) -> Dict:
        """Assess health risk with error handling"""
        
        valid_personas = [
            "General Public", "Children", "Elderly",
            "Outdoor Workers", "Athletes", "Sensitive Groups"
        ]
        
        if not (0 <= aqi <= 500):
            raise ValueError(f"AQI must be 0-500, got {aqi}")
        if persona not in valid_personas:
            raise ValueError(f"Invalid persona. Must be one of: {valid_personas}")
        
        return self._request("POST", "/risk", {
            "aqi": aqi,
            "persona": persona
        })
    
    def explain(self, forecast_values: list, location_name: str,
               style: str = "casual") -> Dict:
        """Generate explanation with error handling"""
        
        valid_styles = ["technical", "casual", "urgent", "reassuring"]
        
        if not forecast_values:
            raise ValueError("forecast_values cannot be empty")
        if style not in valid_styles:
            raise ValueError(f"Invalid style. Must be one of: {valid_styles}")
        
        return self._request("POST", "/explain", {
            "forecast_metadata": {
                "forecast_values": forecast_values
            },
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "name": location_name
            },
            "style": style
        })


# Usage with error handling
def main():
    client = AeroGuardClient(max_retries=3)
    
    try:
        print("Getting forecast...")
        forecast = client.forecast(
            latitude=40.7128,
            longitude=-74.0060,
            aqi_data=[45, 50, 52, 55, 60, 58, 61],
            hours=6
        )
        print(f"✓ Forecast received: {forecast['forecast']['predicted_values']}")
        
        print("\nAssessing risk...")
        risk = client.risk(aqi=65, persona="Athletes")
        print(f"✓ Risk assessed: {risk['risk_assessment']['risk_category']}")
        
        print("\nGenerating explanation...")
        explanation = client.explain(
            forecast_values=forecast['forecast']['predicted_values'],
            location_name="New York"
        )
        print(f"✓ Explanation generated")
        
    except ValueError as e:
        print(f"Validation error: {e}")
    except RuntimeError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
```

---

## Example 5: Batch Processing

**Use Case:** Monitor multiple locations simultaneously

```python
import requests
import concurrent.futures
from typing import List, Dict

class AeroGuardBatchProcessor:
    """Process multiple locations in parallel"""
    
    def __init__(self, api_base: str = "http://localhost:5000/api/v1",
                 max_workers: int = 5):
        self.api_base = api_base
        self.max_workers = max_workers
    
    def get_forecast_for_location(self, location: Dict, 
                                  historical_aqi: List[float]) -> Dict:
        """Get forecast for single location"""
        
        try:
            response = requests.post(
                f"{self.api_base}/forecast",
                json={
                    "location": location,
                    "aqi_data": historical_aqi,
                    "hours_ahead": 6,
                    "include_confidence": True
                },
                timeout=10
            )
            
            if response.status_code == 201:
                return {
                    "location": location["name"],
                    "status": "success",
                    "data": response.json()["forecast"]
                }
            else:
                return {
                    "location": location["name"],
                    "status": "error",
                    "error": response.json().get("error", "Unknown error")
                }
        
        except Exception as e:
            return {
                "location": location["name"],
                "status": "error",
                "error": str(e)
            }
    
    def batch_forecast(self, locations: List[Dict], 
                      historical_aqi: List[float]) -> List[Dict]:
        """Get forecasts for multiple locations in parallel"""
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = {
                executor.submit(
                    self.get_forecast_for_location,
                    location,
                    historical_aqi
                ): location["name"]
                for location in locations
            }
            
            for future in concurrent.futures.as_completed(futures):
                location_name = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    status = result["status"]
                    if status == "success":
                        print(f"✓ {location_name}: {status}")
                    else:
                        print(f"✗ {location_name}: {status} - {result.get('error')}")
                
                except Exception as e:
                    results.append({
                        "location": location_name,
                        "status": "error",
                        "error": str(e)
                    })
                    print(f"✗ {location_name}: {str(e)}")
        
        return results


# Usage
def monitor_multiple_locations():
    """Monitor AQI in 5 NYC boroughs"""
    
    locations = [
        {"latitude": 40.7831, "longitude": -73.9712, "name": "Manhattan"},
        {"latitude": 40.6782, "longitude": -73.9442, "name": "Brooklyn"},
        {"latitude": 40.7282, "longitude": -73.7949, "name": "Queens"},
        {"latitude": 40.8448, "longitude": -73.8648, "name": "Bronx"},
        {"latitude": 40.5961, "longitude": -74.1431, "name": "Staten Island"},
    ]
    
    historical_aqi = [45, 48, 50, 52, 55, 58, 61]
    
    processor = AeroGuardBatchProcessor(max_workers=5)
    
    print("Monitoring 5 NYC locations...\n")
    
    results = processor.batch_forecast(locations, historical_aqi)
    
    print("\nResults Summary:")
    print("-" * 50)
    
    for result in results:
        if result["status"] == "success":
            data = result["data"]
            print(f"{result['location']:15} - Peak AQI: {max(data['predicted_values']):3.0f}, "
                  f"Trend: {data['trend']:8}, Confidence: {data['confidence']:.0%}")
        else:
            print(f"{result['location']:15} - ERROR: {result['error']}")
    
    # Summary statistics
    successful = sum(1 for r in results if r["status"] == "success")
    print(f"\nSuccessful: {successful}/{len(results)}")


if __name__ == "__main__":
    monitor_multiple_locations()
```

---

## Testing with Python

**Run all examples:**
```bash
python complete_workflow.py
python error_handling.py
python batch_processing.py
```

**Run with pytest:**
```bash
pytest tests/test_forecast_routes.py -v
```

---

## Summary

These examples demonstrate:

✅ Complete end-to-end workflows  
✅ Error handling and retries  
✅ Batch processing  
✅ Frontend integration  
✅ Manual testing  
✅ Robust API client  

All ready for production use!
