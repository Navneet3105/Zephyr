import requests

API_KEY = "4be49932c8a1c5f275994e7af0aebeeb"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_data(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_weather_icon_url(icon_code):
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
