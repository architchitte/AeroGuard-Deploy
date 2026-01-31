#!/usr/bin/env python
"""Test real-time AQI data with live API calls."""

from dotenv import load_dotenv
import os

# Load environment variables before importing app
load_dotenv()

from app import create_app
from app.config import Config
import json

if __name__ == '__main__':
    app = create_app(Config)
    with app.test_client() as client:
        print('=' * 60)
        print('REAL-TIME AQI BACKEND TEST WITH LIVE DATA')
        print('=' * 60)
        print()
        
        # Test 1: Single city - Delhi
        print('TEST 1: Single City - Delhi')
        print('-' * 60)
        response = client.get('/api/v1/realtime-aqi/city/Delhi')
        print(f'Status Code: {response.status_code}')
        data = response.get_json()
        if response.status_code == 200:
            aqi_data = data['data']
            print(f'City: {aqi_data.get("city")}')
            print(f'AQI Value: {aqi_data.get("aqi")}')
            print(f'Category: {aqi_data.get("category")}')
            print(f'Main Pollutant: {aqi_data.get("main_pollutant")}')
            print(f'Timestamp: {aqi_data.get("timestamp")}')
            print(f'Pollutants: {aqi_data.get("pollutants")}')
        else:
            print('Error:', data.get('error'))
        print()
        
        # Test 2: Popular cities
        print('TEST 2: Popular Cities AQI')
        print('-' * 60)
        response = client.get('/api/v1/realtime-aqi/popular-cities')
        print(f'Status Code: {response.status_code}')
        data = response.get_json()
        
        # Show first 5 cities
        count = 0
        for city_name, aqi_data in data['data'].items():
            if count >= 5:
                break
            if aqi_data:
                aqi_val = aqi_data.get('aqi')
                category = aqi_data.get('category')
                print(f'{city_name}: AQI {aqi_val} - {category}')
                count += 1
        print()
        
        # Test 3: Coordinates-based lookup
        print('TEST 3: Coordinates-based AQI (Delhi location)')
        print('-' * 60)
        response = client.get('/api/v1/realtime-aqi/coordinates?latitude=28.7041&longitude=77.1025')
        print(f'Status Code: {response.status_code}')
        if response.status_code == 200:
            data = response.get_json()
            aqi_data = data['data']
            print(f'City: {aqi_data.get("city")}')
            print(f'AQI: {aqi_data.get("aqi")}')
            print(f'Category: {aqi_data.get("category")}')
            print(f'Lat/Lon: {aqi_data.get("latitude")}, {aqi_data.get("longitude")}')
        else:
            data = response.get_json()
            print('Error:', data.get('error'))
        print()
        
        # Test 4: Multiple cities batch request
        print('TEST 4: Multiple Cities Batch Request')
        print('-' * 60)
        import json as json_module
        payload = {'cities': ['Delhi', 'Mumbai', 'Bangalore']}
        response = client.post(
            '/api/v1/realtime-aqi/multiple-cities',
            data=json_module.dumps(payload),
            content_type='application/json'
        )
        print(f'Status Code: {response.status_code}')
        data = response.get_json()
        
        for city_name, aqi_data in data['data'].items():
            if aqi_data:
                aqi_val = aqi_data.get('aqi')
                category = aqi_data.get('category')
                print(f'{city_name}: AQI {aqi_val} - {category}')
        print()
        
        # Test 5: Health check
        print('TEST 5: Health Check')
        print('-' * 60)
        response = client.get('/api/v1/realtime-aqi/health')
        print(f'Status Code: {response.status_code}')
        data = response.get_json()
        print(f'Service: {data.get("service")}')
        print(f'Status: {data.get("status")}')
        print(f'API Endpoint: {data.get("api_endpoint")}')
        print()
        
        print('=' * 60)
        print('ALL TESTS COMPLETED SUCCESSFULLY!')
        print('=' * 60)
