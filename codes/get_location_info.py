from dotenv import load_dotenv
import requests
import os
import pandas as pd

load_dotenv()

def get_location_from_file(file_path):
    """
    Reads a file containing addresses and returns a list of addresses.
    
    Args:
        file_path (str): Path to the file containing addresses.
        
    Returns:
        list: A list of addresses.
    """
    with open(file_path, "r") as file:
        addresses = file.readlines()
    return [address.strip() for address in addresses]

def save_place_id(location, file_path, api_key):
    """
    Retrieves the place ID and geographical coordinates for a given location
    and saves the information to a CSV file.
    
    Args:
        location (str): The location address.
        file_path (str): Path to the CSV file.
        api_key (str): Google Maps API key.
        
    Returns:
        tuple: A tuple containing the place ID, latitude, and longitude.
    """
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=["location", "place_id", "latitude", "longitude"])
    t_place_id, t_latitude, t_longitude = get_place_id(location, api_key)
    if t_place_id and t_latitude and t_longitude:
        new_data = pd.DataFrame(
            [{"location": location, "place_id": t_place_id, "latitude": t_latitude, "longitude": t_longitude}]
        )
        new_data = new_data.dropna(how="all")  # Exclude empty or all-NA entries
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(file_path, index=False)
    return t_place_id, t_latitude, t_longitude

def get_data_from_df(file_path):
    """
    Reads a CSV file and returns lists of locations, place IDs, and geographical coordinates.
    
    Args:
        file_path (str): Path to the CSV file.
        
    Returns:
        tuple: A tuple containing three lists:
            - locations (list of str): List of location names.
            - place_ids (list of str): List of place IDs.
            - geometries (list of tuple): List of tuples containing latitude and longitude.
    """
    df = pd.read_csv(file_path)
    locations = df["location"].tolist()
    place_ids = df["place_id"].tolist()
    geometries = df[["latitude", "longitude"]].values.tolist()
    return locations, place_ids, geometries

def get_place_id(location, api_key):
    """
    Retrieves the place ID and geographical coordinates for a given location using the Google Maps API.
    
    Args:
        location (str): The location address.
        api_key (str): Google Maps API key.
        
    Returns:
        tuple: A tuple containing the place ID, latitude, and longitude.
    """
    print("API Call")
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location}&inputtype=textquery&fields=place_id,geometry&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        if result["candidates"]:
            place_id = result["candidates"][0]["place_id"]
            geometry = result["candidates"][0]["geometry"]["location"]
            return place_id, geometry["lat"], geometry["lng"]
    return None

def main(api_key):
    """
    Main function to retrieve and save location information.
    This function reads new locations from the locations file, checks if they are already 
    present in the database, and if not, retrieves their place ID and 
    geographical coordinates. The new information is saved ino the database.
    
    Args:
        api_key (str): Google Maps API key.
                       
    Returns:
        tuple: A tuple containing three lists:
            - locations (list of str): List of location names.
            - id (list of str): List of place IDs corresponding to the locations.
            - geometry (list of tuple): List of tuples containing latitude and 
                                        longitude coordinates for each location.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_loc = os.path.join(current_dir, "data\\locations.txt")
    path_id = os.path.join(current_dir, "data\\places_id.csv")

    new_locations = get_location_from_file(path_loc)
    if os.path.exists(path_id) and os.path.getsize(path_id) > 0:
        locations, id, geometry = get_data_from_df(path_id)
    else:
        locations, id, geometry = [], [], []
    # We check if the location is already in the file and if not we save it
    for t_loc in new_locations:
        if t_loc not in locations:
            t_place_id, t_latitude, t_longitude = save_place_id(t_loc, path_id, api_key)
            locations.append(t_loc)
            id.append(t_place_id)
            geometry.append((t_latitude, t_longitude))
    return locations, id, geometry

if __name__ == "__main__":
    main(api_key=os.getenv("GOOGLE_MAPS_API_KEY"))
