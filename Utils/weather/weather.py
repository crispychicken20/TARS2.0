"""
utils/weather/weather.py
------------------------
Weather fetching module for TARS using OpenWeatherMap API.
"""

import os
import requests
from dotenv import load_dotenv

# Load .env to fetch API key
load_dotenv()

# You can hardcode or pull from .env
API_KEY = os.getenv("WEATHER_API")

def get_weather(city: str = "San Jose") -> str:
    """
    Fetch current weather data for a given city using OpenWeatherMap API.
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    air_quality_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data.get("cod") != 200:
            return f"⚠️ Sorry, I couldn't find weather info for {city}."

        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        desc = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        coordinate = data["coordinate"] 

        air_quality_params = {
            "lat": coord["lat"],
            "lon": coord["lon"],
            "appid": API_KEY
        }
        air_quality_response = requests.get(air_quality_url, params=air_quality_params)
        air_quality_data = air_quality_response.json()

        aqi = air_quality_data["list"][0]["main"]["aqi"]
        aqi_description = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }.get(aqi, "Unknown")
        
        return (
            f"The weather in {city} is currently {desc}. "
            f"Temperature: {temp}°C (feels like {feels}°C), "
            f"high {temp_max}°C, low {temp_min}°C, "
            f"humidity {humidity}%, and wind speed {wind} m/s. "
            f"Air quality is {aqi_description}."
        )

    except Exception as e:
        return f"❌ Error fetching weather: {e}"
