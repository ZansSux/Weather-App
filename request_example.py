import requests

url1 = "https://geocoding-api.open-meteo.com/v1/search"
url2 = "https://api.open-meteo.com/v1/forecast"
def getcity(CityName):
    
    params = {
        "name" : CityName,
        "count" : 1
    }
    return params

def getCoordinates():
    cc = input("Enter city to search: ")
    response = requests.get(url1, params=getcity(cc))
    data = response.json()
    if 'results' not in data:
        print(f"Error: city: '{cc}' could not be found.")
        return None
    first_match = data['results'][0]
    coor = [first_match['latitude'], first_match['longitude']]
    return coor
    
    
def weatherout():
    coors = getCoordinates()
    param1 = {
        "latitude": coors[0],
        "longitude": coors[1],
        "current": "temperature_2m,wind_speed_10m,wind_direction_10m"
    }
    response = requests.get(url2, params=param1)
    data = response.json()

    current_weather = data['current']

    print(('=')*40)
    print(("WEATHER DETAILS").center(40,"*"))
    print(('=')*40)
    print(f'''Temperature: {current_weather['temperature_2m']}°C
Wind Speed: {current_weather['wind_speed_10m']} km/h
Wind Direction: {current_weather['wind_direction_10m']}°''')
print(('=')*40)
print(("CITY SEARCH").center(40,"*"))
print(('=')*40)
weatherout()



