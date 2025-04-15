import folium
from geopy.geocoders import Nominatim
from data_fetcher import get_route_polyline, fetch_weather_pollution_data
from model import load_trained_model, predict_congestion

_model = load_trained_model()

def geocode(location):
    geolocator = Nominatim(user_agent="smart_app")
    loc = geolocator.geocode(location)
    return (loc.latitude, loc.longitude) if loc else None

def create_map(origin_name, dest_name, origin, dest):
    weather_pollution = fetch_weather_pollution_data(*dest)

    temp = weather_pollution['temp']
    humidity = weather_pollution['humidity']
    aqi = weather_pollution['aqi']
    pm25 = weather_pollution['pm25']
    pm10 = weather_pollution['pm10']

    # Extract features for prediction
    features = [
         temp,
         humidity,
         aqi,
         pm25,
         pm10
    ]
    prediction = predict_congestion(_model, features)

    popup = f"""
    <b>Destination:</b> {dest_name}<br>
    <b>Weather:</b> {temp:.1f}°C, Humidity: {humidity}%<br>
    <b>AQI:</b> {aqi} (PM2.5: {pm25}, PM10: {pm10})<br>
    <b>Prediction:</b> {prediction:.4f}
    """

    m = folium.Map(location=dest, zoom_start=13)
    folium.Marker(origin, tooltip="Start: " + origin_name, icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(dest, tooltip="Destination: " + dest_name, icon=folium.Icon(color="red")).add_to(m)
    road_coords = get_route_polyline(origin, dest)
    folium.PolyLine(road_coords, color='blue', weight=6).add_to(m)
    m.save("static/map.html")
