import requests
from dotenv import load_dotenv
import os

load_dotenv()

TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def fetch_traffic_data(lat, lon):
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json?point={lat}%2C{lon}&key={TOMTOM_API_KEY}"
    r = requests.get(url)
    return r.json()

def fetch_weather_pollution_data(lat, lon):
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    weather = requests.get(weather_url).json()
    pollution = requests.get(pollution_url).json()
    return weather, pollution

def get_route_polyline(origin, destination):
    url = "https://router.project-osrm.org/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson".format(
        origin[1], origin[0], destination[1], destination[0]
    )
    res = requests.get(url)
    data = res.json()
    coords = data['routes'][0]['geometry']['coordinates']
    return [(lat, lon) for lon, lat in coords]  # reverse for folium (lat, lon)

def get_elevation_for_coords(coords):
    url = "https://api.open-elevation.com/api/v1/lookup"
    locations = [{"latitude": lat, "longitude": lon} for lat, lon in coords]
    res = requests.post(url, json={"locations": locations})
    data = res.json()["results"]
    return [point["elevation"] for point in data]
