import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()
origin = (45.465422, 9.185924)
destination = (45.4723886, 9.187370399999999)
n_route = 1

def get_route(origin, destination, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin[0]},{origin[1]}&destination={destination[0]},{destination[1]}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        directions = response.json()
        if directions['status'] == 'OK':
            route = directions['routes'][0]
            encoded_polyline = route['overview_polyline']['points']
            return encoded_polyline
        else:
            print(f"Error in response: {directions['status']}")
            return None
    else:
        print(f"HTTP error: {response.status_code}")
        return None

def get_static_map_url_path(path, api_key):
    url = "https://maps.googleapis.com/maps/api/staticmap?"
    url_complete = (
        url
        + "&size=400x400&key="
        + api_key
        + path
        + "&style=feature:poi|visibility:off"
    )
    return url_complete

def get_path_from_encoded_polyline(encoded_polyline):
    path = f"&path=weight:1|enc:{encoded_polyline}"
    return path


def main(origin, destination, n_route, api_key = os.getenv("GOOGLE_MAPS_API_KEY")):
    encoded_polyline = get_route(origin, destination, api_key)
    path = get_path_from_encoded_polyline(encoded_polyline)
    url = get_static_map_url_path(path, api_key)
    r = requests.get(url)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    image_name = f"map_image{n_route}.png"
    image_path = os.path.join(output_dir, image_name)

    with open(image_path, "wb") as f:
            f.write(r.content)

if __name__ == "__main__":
    main(origin, destination, n_route)