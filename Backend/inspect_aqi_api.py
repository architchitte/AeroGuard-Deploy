"""
AQI API Data Inspector
----------------------
Fetches and displays the full range of data available from the WAQI Real-time API.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

def inspect_api(city="Delhi"):
    # The .env uses REALTIME_WAQI_API_KEY, while the service uses REALTIME_AQI_API_KEY
    # We'll try both to be safe
    api_key = os.getenv('REALTIME_WAQI_API_KEY') or os.getenv('REALTIME_AQI_API_KEY')
    base_url = os.getenv('REALTIME_WAQI_BASE_URL') or os.getenv('REALTIME_AQI_BASE_URL', 'https://api.waqi.info')
    
    if not api_key:
        print("Error: REALTIME_WAQI_API_KEY not found in .env")
        return

    print(f"--- Fetching Real-time Data for: {city} ---")
    
    # Try configured key first
    url = f"{base_url}/feed/{city}/?token={api_key}"
    try:
        response = requests.get(url, timeout=10)
        full_data = response.json()
        
        if full_data.get('status') != 'ok':
            print(f"Primary key failed ({full_data.get('data')}), attempting with 'demo' token...")
            url = f"{base_url}/feed/{city}/?token=demo"
            response = requests.get(url, timeout=10)
            full_data = response.json()
            
        if full_data.get('status') != 'ok':
            print(f"API Error: {full_data.get('data')}")
            return

        data = full_data.get('data', {})
        
        print("\n[✔] RAW API STRUCTURE (Top-level keys):")
        print(json.dumps(list(data.keys()), indent=2))
        
        print("\n[✔] BASIC INFO:")
        print(f"  City: {data.get('city', {}).get('name')}")
        print(f"  Station Coordinates: {data.get('city', {}).get('geo')}")
        print(f"  Dominant Pollutant: {data.get('dominanent')}")
        print(f"  Overall AQI: {data.get('aqi')}")
        
        print("\n[✔] INDIVIDUAL POLLUTANTS (IAQI):")
        iaqi = data.get('iaqi', {})
        for key, value in iaqi.items():
            print(f"  - {key:8}: {value.get('v')}")
            
        print("\n[✔] METEOROLOGICAL DATA:")
        iaqi = data.get('iaqi', {})
        met_params = ['t', 'p', 'h', 'w', 'wg']
        met_labels = {'t': 'Temperature', 'p': 'Pressure', 'h': 'Humidity', 'w': 'Wind', 'wg': 'Wind Gust'}
        for p in met_params:
            if p in iaqi:
                print(f"  - {met_labels.get(p, p):12}: {iaqi[p].get('v')}")

        print("\n[✔] FORECAST DATA (Available for):")
        daily_forecast = data.get('forecast', {}).get('daily', {})
        print(f"  - {', '.join(daily_forecast.keys())}")
        
        print("\n[✔] FULL DATA SNIPPET (First level):")
        # Print a clean version of the first level data for inspection
        clean_data = {k: v for k, v in data.items() if k != 'forecast'}
        print(json.dumps(clean_data, indent=2))

    except Exception as e:
        print(f"Error connecting to API: {e}")

if __name__ == "__main__":
    city_to_test = sys.argv[1] if len(sys.argv) > 1 else "Delhi"
    inspect_api(city_to_test)
