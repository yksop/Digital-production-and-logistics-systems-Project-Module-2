import googlemaps
from dotenv import load_dotenv
import requests
import os
import saves_places_id as spi

load_dotenv()

center = "Milan"
zoom = 13


def set_markers_on_map(latitudes, longitudes):
    markers = ""
    for i in range(len(latitudes)):
        markers += f"&markers=size:mid%7Ccolor:red%7Clabel:{i}%7C{latitudes[i]},{longitudes[i]}"
    # markers = markers[:-1]  # Remove the trailing '|'
    return markers

def get_latitudes_longitudes(locations):
    latitudes = []
    longitudes = []
    for location in locations:
        location_dict = eval(location)
        latitudes.append(location_dict["lat"])
        longitudes.append(location_dict["lng"])
    return latitudes, longitudes

def get_static_map_url(center, zoom, markers, api_key):
    url = "https://maps.googleapis.com/maps/api/staticmap?"
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
    return url_complete

def main(api_key=os.getenv("GOOGLE_MAPS_API_KEY")):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_geometry = os.path.join(current_dir, "data\\places_geometry.txt")
    image_path = os.path.join(current_dir, "output\\map_image.png")
    locations = spi.get_location_from_file(path_geometry)
    lattitudes, longitude = get_latitudes_longitudes(locations)

    markers = set_markers_on_map(lattitudes, longitude)
    url = get_static_map_url(center, zoom, markers, api_key)
    print(url)
    r = requests.get(url)

    with open(image_path, "wb") as f:
        f.write(r.content)

if __name__ == "__main__":
    main()