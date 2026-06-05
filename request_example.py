import requests

url1 = "https://geocoding-api.open-meteo.com/v1/search"
url2 = "https://api.open-meteo.com/v1/forecast"
def getcity(CityName):
    
    params = {
        "name" : CityName,
        "count" : 1
    }
    return params

def getCoordinates(cc):
    response = requests.get(url1, params=getcity(cc))
    data = response.json()
    if 'results' not in data:
        print(f"Error: city: '{cc}' could not be found.")
        return None
    
    first_match = data['results'][0]

    coor = [first_match['latitude'], first_match['longitude'], first_match['name']]
    return coor
    
    
def weatherout(cc):
    coors = getCoordinates(cc)
    param1 = {
        "latitude": coors[0],
        "longitude": coors[1],
        "current": "temperature_2m,wind_speed_10m,wind_direction_10m"
    }
    cityy = coors[2]
    response = requests.get(url2, params=param1)
    data = response.json()

    current_weather = data['current']
    return current_weather, cityy

