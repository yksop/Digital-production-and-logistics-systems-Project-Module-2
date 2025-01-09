from dotenv import load_dotenv
import distance_matrix as dm
import requests
import os

load_dotenv()

def get_route(origin: tuple, destination: tuple, TARGET_WEEKDAY: int, TARGET_HOUR: int, api_key: str) -> str:
    """
    Retrieves the encoded polyline for the route between the origin and destination using the Google Directions API.
    
    Args:
        origin (tuple): Tuple containing the latitude and longitude of the origin.
        destination (tuple): Tuple containing the latitude and longitude of the destination.
        TARGET_WEEKDAY (int): The target weekday (0=Monday, 6=Sunday).
        TARGET_HOUR (int): The target hour (24-hour format).
        api_key (str): Google Maps API key.
        
    Returns:
        str: Encoded polyline for the route.
    """
    print("API Call")
    url = "https://maps.googleapis.com/maps/api/directions/json?"
    url_complete = (
        url
        + "origin="
        + str(origin[0]) + "," + str(origin[1])
        + "&destination=" 
        + str(destination[0]) + "," + str(destination[1])
        + "&departure_time="
        + str(dm.get_next_target_weekday(TARGET_WEEKDAY, TARGET_HOUR))
        + "&key="
        + api_key
    )
    response = requests.get(url_complete)
    if response.status_code == 200:
        directions = response.json()
        if directions["status"] == "OK":
            route = directions["routes"][0]
            encoded_polyline = route["overview_polyline"]["points"]
            return encoded_polyline
        else:
            print(f"Error in response: {directions['status']}")
            return None
    else:
        print(f"HTTP error: {response.status_code}")
        return None

def get_static_map_url_path(path: str, api_key: str) -> str:
    """
    Create the complete URL for the Google Static Maps API request with the route path.
    
    Args:
        path (str): URL parameter string for the path.
        api_key (str): Google Maps API key.
    
    Returns:
        str: Complete URL for the API request.
    """
    url = "https://maps.googleapis.com/maps/api/staticmap?"
    url_complete = url + "&size=400x400&key=" + api_key + path + "&style=feature:poi|visibility:off"
    return url_complete

def get_path_from_encoded_polyline(encoded_polyline: str) -> str:
    """
    Create a URL parameter string for the path from the encoded polyline.
    
    Args:
        encoded_polyline (str): Encoded polyline for the route.
    
    Returns:
        str: URL parameter string for the path.
    """
    path = f"&path=weight:2|color:red|enc:{encoded_polyline}"
    return path

def main(origin: tuple, destination: tuple, n_route: int, TARGET_WEEKDAY: int, TARGET_HOUR: int, api_key: str) -> None:
    """
    Main function to create a static map image with the route between the origin and destination.
    This function retrieves the route, generates the static map image, and saves it to a file.
    
    Args:
        origin (tuple): Tuple containing the latitude and longitude of the origin.
        destination (tuple): Tuple containing the latitude and longitude of the destination.
        n_route (int): Route number for naming the output file.
        TARGET_WEEKDAY (int): The target weekday (0=Monday, 6=Sunday).
        TARGET_HOUR (int): The target hour (24-hour format).
        api_key (str): Google Maps API key.
    
    Returns:
        None
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_name = f"route{n_route}.png"
    image_path = os.path.join(current_dir, "images", image_name)
    
    encoded_polyline = get_route(origin, destination, TARGET_WEEKDAY, TARGET_HOUR, api_key)
    path = get_path_from_encoded_polyline(encoded_polyline)
    url = get_static_map_url_path(path, api_key)
    r = requests.get(url)
    print("API Call")
    with open(image_path, "wb") as f:
        f.write(r.content)

if __name__ == "__main__":
    main(
        origin=(45.465422, 9.185924),
        destination=(45.4723886, 9.187370399999999),
        n_route=1,
        TARGET_WEEKDAY=0,
        TARGET_HOUR=8,
        api_key=os.getenv("GOOGLE_MAPS_API_KEY"),
    )
