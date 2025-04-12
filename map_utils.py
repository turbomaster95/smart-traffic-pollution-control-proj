import folium
import json
import time
from geopy.geocoders import Nominatim
from data_fetcher import (
    fetch_traffic_data,
    fetch_weather_pollution_data,
    get_route_polyline
)
from model import load_trained_model, predict_congestion

# Load and reuse model
_model = load_trained_model()

def geocode(location):
    geolocator = Nominatim(user_agent="smart_app")
    loc = geolocator.geocode(location)
    return (loc.latitude, loc.longitude) if loc else None

def get_congestion_color(current_speed, free_flow_speed):
    ratio = current_speed / free_flow_speed
    if ratio > 0.8:
        return 'green'
    elif ratio >= 0.5:
        return 'orange'
    else:
        return 'red'

def create_segment_colored_route(m, road_coords):
    segment_step = 10
    for i in range(0, len(road_coords) - 1, segment_step):
        p1 = road_coords[i]
        p2 = road_coords[min(i + segment_step, len(road_coords) - 1)]
        mid_lat = (p1[0] + p2[0]) / 2
        mid_lon = (p1[1] + p2[1]) / 2

        try:
            traffic = fetch_traffic_data(mid_lat, mid_lon)
            seg = traffic["flowSegmentData"]
            color = get_congestion_color(seg["currentSpeed"], seg["freeFlowSpeed"])
        except Exception as e:
            print("❌ Traffic segment fetch failed:", e)
            color = "gray"

        folium.PolyLine([p1, p2], color=color, weight=6).add_to(m)
        time.sleep(0.1)  # respect API rate limit

def create_map(origin_name, dest_name, origin, dest):
    weather, pollution = fetch_weather_pollution_data(*dest)
    traffic = fetch_traffic_data(*dest)
    segment = traffic['flowSegmentData']

    # LSTM model input
    features = [
        segment['currentSpeed'],
        segment['freeFlowSpeed'],
        weather['main']['temp'],
        weather['main']['humidity'],
        pollution['list'][0]['main']['aqi'],
        pollution['list'][0]['components']['pm2_5'],
        pollution['list'][0]['components']['pm10']
    ]
    prediction = predict_congestion(_model, features)

    temp = weather['main']['temp'] - 273.15
    desc = weather['weather'][0]['description']
    aqi = pollution['list'][0]['main']['aqi']
    pm25 = pollution['list'][0]['components']['pm2_5']
    pm10 = pollution['list'][0]['components']['pm10']

    popup = f"""
    <b>Destination:</b> {dest_name}<br>
    <b>Weather:</b> {desc.capitalize()}, {temp:.1f}°C<br>
    <b>AQI:</b> {aqi} (PM2.5: {pm25}, PM10: {pm10})<br>
    <b>Traffic:</b> {segment['currentSpeed']} km/h (free: {segment['freeFlowSpeed']} km/h)<br>
    <b>Prediction:</b> {prediction:.4f}
    """

    m = folium.Map(location=dest, zoom_start=13)
    folium.Marker(origin, tooltip="Start: " + origin_name, icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(dest, tooltip="Destination: " + dest_name, popup=popup, icon=folium.Icon(color="red")).add_to(m)

    road_coords = get_route_polyline(origin, dest)
    create_segment_colored_route(m, road_coords)

    m.save("static/map.html")
