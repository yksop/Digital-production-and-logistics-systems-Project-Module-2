import googlemaps
from dotenv import load_dotenv
import requests
import os

load_dotenv()

api_key = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=api_key)


def get_latitudes_longitudes(addresses):
    latitudes = []
    longitudes = []
    for address in addresses:
        location = gmaps.geocode(address)[0]["geometry"]["location"]
        latitudes.append(location["lat"])
        longitudes.append(location["lng"])
    return latitudes, longitudes


def get_location_from_file(file_path):
    with open(file_path, "r") as file:
        addresses = file.readlines()
    return [address.strip() for address in addresses]


def set_markers_on_map(latitudes, longitudes):
    markers = "&markers="
    for i in range(len(latitudes)):
        markers += f"size:mid%7Ccolor:red%7C{latitudes[i]},{longitudes[i]}|"
    markers = markers[:-1]  # Remove the trailing '|'
    return markers


path = "locations.txt"
latitudes, longitudes = get_latitudes_longitudes(get_location_from_file(path))
markers = set_markers_on_map(latitudes, longitudes)

url = "https://maps.googleapis.com/maps/api/staticmap?"
center = "Milan"
zoom = 13

url_complete = (
    url
    + "center="
    + center
    + "&zoom="
    + str(zoom)
    + "&size=400x400&key="
    + api_key
    + markers
    + "&style=feature:poi|visibility:off"
)

r = requests.get(url_complete)

# Save the map image
with open("map_image.png", "wb") as f:
    f.write(r.content)
