# Real-time AQI API Documentation

## Overview

The Real-time AQI API provides access to real-time air quality data for multiple locations across India using the WAQI (World Air Quality Index) API.

**Base URL:** `http://localhost:5000/api/v1/realtime-aqi`

**Authentication:** None required (API key is handled server-side)

---

## Endpoints

### 1. Get AQI for a Specific City

**Endpoint:** `GET /api/v1/realtime-aqi/city/{city_name}`

**Description:** Fetch real-time air quality data for a specific city in India.

**Parameters:**
- `city_name` (path, required): Name of the city (e.g., 'Delhi', 'Mumbai', 'Bangalore')

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/realtime-aqi/city/Delhi"
```

**Example Response (Success):**
```json
{
  "status": "success",
  "data": {
    "city": "Delhi",
    "aqi": 152,
    "category": "Unhealthy for Sensitive Groups",
    "latitude": 28.7041,
    "longitude": 77.1025,
    "pollutants": {
      "PM2.5": 125,
      "PM10": 152,
      "NO2": 45,
      "O3": 12,
      "SO2": 8,
      "CO": null
    },
    "url": "https://waqi.info/...",
    "last_updated": "2026-01-31T15:00:00Z",
    "source": "CPCB (Central Pollution Control Board)",
    "timestamp": "2026-01-31T15:01:23.456Z"
  }
}
```

**Status Codes:**
- `200 OK` - Successful request
- `400 Bad Request` - Invalid city name
- `404 Not Found` - City data not found
- `500 Internal Server Error` - Server error

---

### 2. Get AQI by Coordinates

**Endpoint:** `GET /api/v1/realtime-aqi/coordinates`

**Description:** Get real-time AQI data for the nearest monitoring station to given coordinates.

**Query Parameters:**
- `latitude` (required): Latitude of the location
- `longitude` (required): Longitude of the location

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/realtime-aqi/coordinates?latitude=28.7041&longitude=77.1025"
```

**Response:** Same format as single city endpoint

---

### 3. Get AQI for Multiple Cities

**Endpoint:** `POST /api/v1/realtime-aqi/multiple-cities`

**Description:** Fetch real-time AQI data for multiple cities in a single request.

**Request Body:**
```json
{
  "cities": ["Delhi", "Mumbai", "Bangalore", "Hyderabad"]
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/v1/realtime-aqi/multiple-cities" \
  -H "Content-Type: application/json" \
  -d '{"cities": ["Delhi", "Mumbai", "Bangalore"]}'
```

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "Delhi": {
      "city": "Delhi",
      "aqi": 152,
      "category": "Unhealthy for Sensitive Groups",
      ...
    },
    "Mumbai": {
      "city": "Mumbai",
      "aqi": 98,
      "category": "Moderate",
      ...
    },
    "Bangalore": {
      "city": "Bangalore",
      "aqi": 65,
      "category": "Moderate",
      ...
    }
  },
  "timestamp": "2026-01-31T15:01:23.456Z"
}
```

**Constraints:**
- Maximum 50 cities per request
- If a city's data cannot be fetched, it will be `null` in the response

---

### 4. Get AQI for Popular Indian Cities

**Endpoint:** `GET /api/v1/realtime-aqi/popular-cities`

**Description:** Get real-time AQI data for all major cities in India in one request.

**Popular Cities Include:**
- Delhi, Mumbai, Bangalore, Hyderabad, Chennai
- Kolkata, Pune, Ahmedabad, Jaipur, Lucknow
- Chandigarh, Indore, Surat, Visakhapatnam, Nagpur

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/realtime-aqi/popular-cities"
```

**Response Format:** Same as multiple cities endpoint

---

### 5. Health Check

**Endpoint:** `GET /api/v1/realtime-aqi/health`

**Description:** Check if the real-time AQI service is operational.

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/realtime-aqi/health"
```

**Example Response:**
```json
{
  "status": "operational",
  "service": "Real-time AQI",
  "timestamp": "2026-01-31T15:01:23.456Z"
}
```

**Status Values:**
- `operational` - Service is operational and configured
- `not_configured` - Service is available but API key not set

---

## AQI Categories

The API returns an AQI category based on the numerical AQI value:

| AQI Value | Category | Health Impact |
|-----------|----------|--------------|
| 0-50 | Good | No health impact |
| 51-100 | Moderate | Acceptable air quality |
| 101-150 | Unhealthy for Sensitive Groups | Members of sensitive groups may experience health effects |
| 151-200 | Unhealthy | General public may experience health effects |
| 201-300 | Very Unhealthy | Health alert: entire population may experience effects |
| 301+ | Hazardous | Health warning of emergency conditions |

---

## Pollutant Details

Each response includes pollutant concentrations (in µg/m³):

- **PM2.5**: Fine particulate matter
- **PM10**: Respirable suspended particulate matter
- **NO2**: Nitrogen dioxide
- **O3**: Ozone
- **SO2**: Sulfur dioxide
- **CO**: Carbon monoxide

---

## Error Handling

**Error Response Format:**
```json
{
  "status": "error",
  "message": "Error description"
}
```

**Common Error Codes:**
- `400`: Invalid request parameters
- `404`: City not found or data unavailable
- `500`: Server error during data fetching

---

## Rate Limiting

- No explicit rate limiting on frontend
- Backend API respects WAQI rate limits
- Recommend caching results for 1-5 minutes

---

## Data Source

**WAQI (World Air Quality Index)**
- URL: https://waqi.info
- Provides real-time air quality data globally
- Aggregates data from multiple government and private sources

---

## Example Frontend Integration

```javascript
// Fetch AQI for Delhi
fetch('http://localhost:5000/api/v1/realtime-aqi/city/Delhi')
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      const aqi = data.data.aqi;
      const category = data.data.category;
      console.log(`Delhi AQI: ${aqi} (${category})`);
    }
  });

// Fetch AQI for multiple cities
fetch('http://localhost:5000/api/v1/realtime-aqi/multiple-cities', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    cities: ['Delhi', 'Mumbai', 'Bangalore']
  })
})
  .then(response => response.json())
  .then(data => {
    Object.entries(data.data).forEach(([city, aqi_data]) => {
      if (aqi_data) {
        console.log(`${city}: ${aqi_data.aqi} - ${aqi_data.category}`);
      }
    });
  });

// Fetch AQI by coordinates
const lat = 28.7041;
const lon = 77.1025;
fetch(`http://localhost:5000/api/v1/realtime-aqi/coordinates?latitude=${lat}&longitude=${lon}`)
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## Configuration

Add the following to your `.env` file:

```env
# Real-time AQI API Configuration
REALTIME_AQI_API_KEY=your-waqi-api-key-here
REALTIME_AQI_BASE_URL=https://api.waqi.info/v2
```

Get your API key from: https://aqicn.org/api/

---

## Troubleshooting

**Issue:** "API key not configured"
- **Solution:** Add `REALTIME_AQI_API_KEY` to your `.env` file

**Issue:** 404 for valid city names
- **Solution:** Try with city name from the popular cities list
- **Note:** Some smaller cities may not have monitoring stations

**Issue:** All cities return null
- **Solution:** Verify API key is correct and active
- **Check:** Use the `/health` endpoint to verify service status

---

## Performance Tips

1. **Cache Results**: Store AQI data client-side for 5-10 minutes
2. **Batch Requests**: Use `/multiple-cities` instead of multiple single requests
3. **Use Coordinates**: If you don't know the exact city name, use coordinates
4. **Error Handling**: Gracefully handle null responses for unavailable cities

---

## Future Enhancements

- [ ] Historical AQI trends
- [ ] AQI forecasting
- [ ] Alert thresholds per user
- [ ] Geofencing for location-based alerts
- [ ] Export to CSV/Excel

---

Last Updated: January 31, 2026
