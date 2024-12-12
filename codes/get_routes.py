import requests
import os

api_key=os.getenv("GOOGLE_MAPS_API_KEY")

def get_route(origin, destination, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin[0]},{origin[1]}&destination={destination[0]},{destination[1]}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Example usage:
origin = [45.4772399, 9.2014099]
destination = [45.4723886, 9.187370399999999]
route = get_route(origin, destination, api_key)
print(route)