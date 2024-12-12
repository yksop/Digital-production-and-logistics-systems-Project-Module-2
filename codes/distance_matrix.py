import googlemaps
from dotenv import load_dotenv
import requests
import os
import json
import numpy as np
import datetime
import saves_places_id as spi

TARGET_WEEKDAY = 0  # Monday
TARGET_HOUR = 8  # 8:00 AM


load_dotenv()

# gmaps = googlemaps.Client(key=api_key)

def get_next_target_weekday(target_weekday, target_hour):
    now = datetime.datetime.now()
    # Find the next target_weekday
    days_ahead = (target_weekday - now.weekday() + 7) % 7
    if days_ahead == 0 and now.hour >= target_hour:  # If today is the day but time has passed
        days_ahead = 7
    target_date = now + datetime.timedelta(days=days_ahead)
    # Set the target time
    target_time = target_date.replace(hour=target_hour, minute=0, second=0, microsecond=0)    
    # Convert to UNIX timestamp
    departure_time = int(target_time.timestamp())
    return departure_time

def get_file_modification_time(file_path):
    return os.path.getmtime(file_path)

def compare_file_modification_times(file_path1, file_path2):
    time1 = get_file_modification_time(file_path1)
    time2 = get_file_modification_time(file_path2)
    return time1 < time2

def set_url_destination_params(locations_id):
    url_locations = ""
    for location_id in locations_id:
        url_locations += "place_id:" + location_id + "|"
    url_locations = url_locations[:-1]    
    return url_locations

def create_time_matrix_from_file(json_file):
    """
    Reads a JSON file containing the Google Distance Matrix API response 
    and creates a time matrix.
    
    Args:
        json_file (str): Path to the JSON file.
    
    Returns:
        np.ndarray: A 2D NumPy array representing the time matrix (in seconds).
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    num_locations = len(data['rows'])
    
    time_matrix = np.zeros((num_locations, num_locations))
    
    for i, row in enumerate(data['rows']):
        for j, element in enumerate(row['elements']):
            if i == j:
                time_matrix[i][j] = 0  # Ensure the diagonal is 0
            elif element['status'] == 'OK':
                time_matrix[i][j] = round(float(element['duration_in_traffic']['value']) / 60, 2)  # Time in minutes with 2 decimal places
            else:
                time_matrix[i][j] = np.inf  # Use infinity if no valid time is available
    
    return time_matrix

def create_url_matrix(url_locations, api_key):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
    url_complete = (
        url
        + "origins=" + url_locations
        + "&destinations=" + url_locations
        + "&departure_time=" + str(get_next_target_weekday(TARGET_WEEKDAY, TARGET_HOUR))
        + "&key=" + api_key
    )
    return url_complete

def main(TARGET_WEEKDAY, TARGET_HOUR, api_key=os.getenv("GOOGLE_MAPS_API_KEY")):
    # api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_loc = os.path.join(current_dir, "data\\locations.txt")
    path_id = os.path.join(current_dir, "data\\places_id.txt")
    json_file = f"time_matrix{TARGET_WEEKDAY}_{TARGET_HOUR}.json"
    json_path = os.path.join(current_dir, "data", json_file)
    if not compare_file_modification_times(path_loc, path_id):
        print("Updating the places ID file...")
        locations = spi.get_location_from_file(path_loc)
        spi.save_places_id(locations, path_id, api_key)
    if not os.path.exists(json_path) or not compare_file_modification_times(path_id, json_path):
        print("Creating a new time matrix...")
        location_id = spi.get_location_from_file(path_id)
        url_locations = set_url_destination_params(location_id)
        url_complete = create_url_matrix(url_locations, api_key)
        response = requests.get(url_complete)
        time_json = response.json()
        with open(json_path, "w") as outfile:
            json.dump(time_json, outfile, indent=4)

    time_matrix = create_time_matrix_from_file(json_path)
    return time_matrix
    

if __name__ == "__main__":
    main(TARGET_WEEKDAY, TARGET_HOUR)