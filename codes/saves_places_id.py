import googlemaps
from dotenv import load_dotenv
import requests
import os

load_dotenv()

api_key = os.getenv("GOOGLE_MAPS_API_KEY")

def get_location_from_file(file_path):
    with open(file_path, "r") as file:
        addresses = file.readlines()
    return [address.strip() for address in addresses]

def save_places_id(locations, file_path, api_key):
    with open(file_path, "w") as file:
        for location in locations:
            get_place_id(location, api_key)
            file.write(f"{get_place_id(location, api_key)}\n")

def get_place_id(location, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location}&inputtype=textquery&fields=place_id&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        if result['candidates']:
            return result['candidates'][0]['place_id']
    return None

current_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(current_dir, "data\\locations.txt")
path_to_save = os.path.join(current_dir, "data\\places_id.txt")

locations = get_location_from_file(path)

save_places_id(locations, path_to_save, api_key)
