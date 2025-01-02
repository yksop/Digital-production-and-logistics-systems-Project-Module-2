from dotenv import load_dotenv
import requests
import os
import json
import numpy as np
import datetime
import get_location_info as gl

load_dotenv()

def get_next_target_weekday(target_weekday: int, target_hour: int) -> int:
    """
    Calculate the UNIX timestamp for the next occurrence of the target weekday and hour.
    
    Args:
        target_weekday (int): The target weekday (0=Monday, 6=Sunday).
        target_hour (int): The target hour (24-hour format).
    
    Returns:
        int: UNIX timestamp for the next target weekday and hour.
    """
    now = datetime.datetime.now()
    days_ahead = (target_weekday - now.weekday() + 7) % 7
    if days_ahead == 0 and now.hour >= target_hour:
        days_ahead = 7
    target_date = now + datetime.timedelta(days=days_ahead)
    target_time = target_date.replace(hour=target_hour, minute=0, second=0, microsecond=0)    
    departure_time = int(target_time.timestamp())
    return departure_time

def get_file_modification_time(file_path):
    """
    Get the modification time of a file.
    
    Args:
        file_path (str): Path to the file.
    
    Returns:
        float: The modification time of the file as a UNIX timestamp.
    """
    return os.path.getmtime(file_path)

def compare_file_modification_times(file_path1: str, file_path2: str) -> bool:
    """
    Compare the modification times of two files.
    
    Args:
        file_path1 (str): Path to the first file.
        file_path2 (str): Path to the second file.
    
    Returns:
        bool: True if the first file is older than the second file, False otherwise.
    """
    time1 = get_file_modification_time(file_path1)
    time2 = get_file_modification_time(file_path2)
    return time1 < time2

def set_url_destination_params(locations_id: list) -> str:
    """
    Create a URL parameter string for the Google Distance Matrix API from a list of place IDs.
    
    Args:
        locations_id (list): List of place IDs.
    
    Returns:
        str: URL parameter string for the locations.
    """
    url_locations = ""
    for location_id in locations_id:
        url_locations += "place_id:" + location_id + "|"
    url_locations = url_locations[:-1]    
    return url_locations

def create_time_matrix_from_file(json_file: str) -> tuple:
    """
    Reads a JSON file containing the Google Distance Matrix API response 
    and creates a time matrix.
    
    Args:
        json_file (str): Path to the JSON file.
    
    Returns:
        np.ndarray: A 2D NumPy array representing the time matrix (in minutes).
        np.ndarray: A 2D NumPy array representing the distance matrix (in minutes).
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    num_locations = len(data['rows'])
    time_matrix = np.zeros((num_locations, num_locations))
    distance_matrix = np.zeros((num_locations, num_locations))
    for i, row in enumerate(data['rows']):
        for j, element in enumerate(row['elements']):
            if i == j:
                time_matrix[i][j] = 0
                distance_matrix[i][j] = 0
            elif element['status'] == 'OK':
                time_matrix[i][j] = round(float(element['duration_in_traffic']['value']) / 60, 2)
                distance_matrix[i][j] = float(element['distance']['value'])
            else:
                time_matrix[i][j] = np.inf
                distance_matrix[i][j] = np.inf
    return time_matrix, distance_matrix

def create_url_matrix(url_locations: str, TARGET_WEEKDAY: int, TARGET_HOUR: int, api_key: str) -> str:
    """
    Create the complete URL for the Google Distance Matrix API request.
    
    Args:
        url_locations (str): URL parameter string for the locations.
        TARGET_WEEKDAY (int): The target weekday (0=Monday, 6=Sunday).
        TARGET_HOUR (int): The target hour (24-hour format).
        api_key (str): Google Maps API key.
    
    Returns:
        str: Complete URL for the API request.
    """
    print("API Call")
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
    url_complete = (
        url
        + "origins=" + url_locations
        + "&destinations=" + url_locations
        + "&departure_time=" + str(get_next_target_weekday(TARGET_WEEKDAY, TARGET_HOUR))
        + "&key=" + api_key
    )
    return url_complete

def main(TARGET_WEEKDAY: int, TARGET_HOUR: int, api_key: str) -> np.ndarray:
    """
    Main function to create a time matrix for a set of locations.
    This function checks if a time matrix JSON file is up-to-date,
    and if not, computes a new matrix.
    
    Args:
        TARGET_WEEKDAY (int): The target weekday (0=Monday, 6=Sunday).
        TARGET_HOUR (int): The target hour (24-hour format).
        api_key (str): Google Maps API key.
    
    Returns:
        np.ndarray: A 2D NumPy array representing the time matrix (in minutes).
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_loc = os.path.join(current_dir, "data\\locations.txt")
    json_file = f"time_matrix{TARGET_WEEKDAY}_{TARGET_HOUR}.json"
    json_path = os.path.join(current_dir, "data", json_file)
    
    if os.path.exists(json_path) and compare_file_modification_times(path_loc, json_path):
        # If the file exists and is up-to-date
        time_matrix, distance_matrix = create_time_matrix_from_file(json_path)
        return time_matrix, distance_matrix
    
    locations, id, geometry = gl.main(api_key)
    print("Creating a new time matrix...")
    url_locations = set_url_destination_params(id)
    url_complete = create_url_matrix(url_locations, TARGET_WEEKDAY, TARGET_HOUR,api_key)
        
    response = requests.get(url_complete)
    time_json = response.json()
    with open(json_path, "w") as outfile:
        json.dump(time_json, outfile, indent=4)

    time_matrix, distance_matrix = create_time_matrix_from_file(json_path)
    return time_matrix, distance_matrix

if __name__ == "__main__":
    main(TARGET_WEEKDAY=0, TARGET_HOUR=8, api_key=os.getenv("GOOGLE_MAPS_API_KEY"))