import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 27.7172,
    "longitude": 85.3240,
    "current_weather": True
}

response = requests.get(url, params=params)
data = response.json()
print(f"The temperature at latitude:{data['latitude']}, longitude:{data['longit gitude']} is {data['current_weather']['temperature']}.")