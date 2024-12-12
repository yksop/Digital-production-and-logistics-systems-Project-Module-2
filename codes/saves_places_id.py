from dotenv import load_dotenv
import requests
import os

load_dotenv()



def get_location_from_file(file_path):
    with open(file_path, "r") as file:
        addresses = file.readlines()
    return [address.strip() for address in addresses]

def save_places_id(locations, file_path, path_geometry, api_key):
    with open(file_path, "w") as file_id, open(path_geometry, "w") as file_geometry:
        for location in locations:
            place_id, geometry = get_place_id(location, api_key)
            if place_id and geometry:
                file_id.write(f"{place_id}\n")
                file_geometry.write(f"{geometry}\n")

def get_place_id(location, api_key):
    # url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location}&inputtype=textquery&fields=place_id&key={api_key}"
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location}&inputtype=textquery&fields=place_id,geometry&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        if result['candidates']:
            place_id = result['candidates'][0]['place_id']
            geometry = result['candidates'][0]['geometry']['location']
            return place_id, geometry
    return None

def main(api_key=os.getenv("GOOGLE_MAPS_API_KEY")):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_loc = os.path.join(current_dir, "data\\locations.txt")
    path_id = os.path.join(current_dir, "data\\places_id.txt")
    path_geometry = os.path.join(current_dir, "data\\places_geometry.txt")
    locations = get_location_from_file(path_loc)
    save_places_id(locations, path_id, path_geometry, api_key)


if __name__ == "__main__":
    main()
