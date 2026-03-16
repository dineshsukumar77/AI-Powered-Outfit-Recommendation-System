"""
Weather API integration (OpenWeatherMap).
Returns a short description for outfit context.
"""
import requests
from django.conf import settings


def get_weather_for_location(city: str = None, lat: float = None, lon: float = None) -> str:
    """
    Fetch current weather. Use city name or (lat, lon).
    Returns a short string like "Sunny, 72°F" or "Cloudy, 55°F, light rain".
    """
    api_key = (getattr(settings, 'OPENWEATHER_API_KEY', None) or '').strip()
    if not api_key:
        return 'Weather unknown (set OPENWEATHER_API_KEY in backend/.env for live data)'

    params = {'appid': api_key, 'units': 'imperial'}
    if city:
        params['q'] = city.strip()
    elif lat is not None and lon is not None:
        params['lat'] = lat
        params['lon'] = lon
    else:
        return 'Weather unknown (provide city or coordinates)'

    try:
        r = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params, timeout=10)
        if r.status_code == 401:
            return 'Weather error: Invalid OpenWeatherMap API key (check backend/.env)'
        if r.status_code == 404:
            return 'Weather error: City not found. Try "City, Country" (e.g. London, UK)'
        if r.status_code != 200:
            return f'Weather error: API returned {r.status_code}'
        data = r.json()
        temp = int(data.get('main', {}).get('temp', 0))
        desc = (data.get('weather') or [{}])[0].get('description', '')
        return f'{desc.capitalize()}, {temp}°F'
    except requests.exceptions.Timeout:
        return 'Weather error: Request timed out'
    except requests.exceptions.RequestException as e:
        return f'Weather error: {str(e)[:80]}'
    except Exception as e:
        return f'Weather error: {str(e)[:80]}'
