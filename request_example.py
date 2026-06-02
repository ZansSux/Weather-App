import requests

url = "https://api.open-meteo.com/v1/forecast?latitude=27.7&longitude=85.3&current_weather=true"

response = requests.get(url)
data = response.json()
print(f"The temperature at latitude:{data['latitude']}, longitude:{data['longit gitude']} is {data['current_weather']['temperature']}.")