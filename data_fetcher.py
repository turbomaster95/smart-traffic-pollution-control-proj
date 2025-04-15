import os
import requests
import polyline
from dotenv import load_dotenv
from google.cloud import bigquery

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize BigQuery client
client = bigquery.Client()

def get_route_polyline(origin, destination):
    origin_str = f"{origin[0]},{origin[1]}"
    dest_str = f"{destination[0]},{destination[1]}"
    url = (
        f"https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={origin_str}&destination={dest_str}&key={GOOGLE_API_KEY}"
    )
    res = requests.get(url).json()
    points = res['routes'][0]['overview_polyline']['points']
    return polyline.decode(points)  # list of (lat, lon)

def get_elevation(lat, lon):
    url = (
        f"https://maps.googleapis.com/maps/api/elevation/json"
        f"?locations={lat},{lon}&key={GOOGLE_API_KEY}"
    )
    res = requests.get(url).json()
    return res['results'][0]['elevation'] if res['results'] else None

def fetch_weather_pollution_data(lat, lon):
    # Fetch weather data from NOAA GSOD
    weather_query = f"""
    SELECT
        mean_temp, humidity
    FROM
        `bigquery-public-data.noaa_gsod.gsod2022`
    WHERE
        latitude BETWEEN {lat - 0.5} AND {lat + 0.5}
        AND longitude BETWEEN {lon - 0.5} AND {lon + 0.5}
        AND mean_temp IS NOT NULL
        AND humidity IS NOT NULL
    ORDER BY
        date DESC
    LIMIT 1
    """
    weather_job = client.query(weather_query)
    weather_row = list(weather_job)[0]
    temp_c = (weather_row.mean_temp - 32) * 5.0 / 9.0  # Convert F to C
    humidity = weather_row.humidity

    # Fetch air quality data from OpenAQ
    pollution_query = f"""
    SELECT
        value,
        parameter
    FROM
        `bigquery-public-data.openaq.global_air_quality`
    WHERE
        latitude BETWEEN {lat - 0.5} AND {lat + 0.5}
        AND longitude BETWEEN {lon - 0.5} AND {lon + 0.5}
        AND parameter IN ('pm25', 'pm10')
    ORDER BY
        timestamp DESC
    LIMIT 2
    """
    pollution_job = client.query(pollution_query)
    pollution_rows = list(pollution_job)
    pm25 = next((row.value for row in pollution_rows if row.parameter == 'pm25'), None)
    pm10 = next((row.value for row in pollution_rows if row.parameter == 'pm10'), None)
    aqi = max(pm25 or 0, pm10 or 0)  # Simplified AQI estimation

    return {
        "temp": temp_c,
        "humidity": humidity,
        "aqi": aqi,
        "pm25": pm25,
        "pm10": pm10
    }
