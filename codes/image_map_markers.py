from dotenv import load_dotenv
import requests
import os
import get_location_info as gl

load_dotenv()

def set_markers_on_map(geometry: list) -> str:
    """
    Create a string of markers for the Google Static Maps API from a list of geographical coordinates.
    
    Args:
        geometry (list): List of tuples containing latitude and longitude coordinates.
        
    Returns:
        str: URL parameter string for the markers.
    """
    markers = ""
    color = "green"
    for i, place in enumerate(geometry):
        markers += f"&markers=size:mid%7Ccolor:{color}%7Clabel:{i}%7C{place[0]},{place[1]}"
        color = "red"
    return markers

def get_static_map_url(markers: str, api_key: str) -> str:
    """
    Create the complete URL for the Google Static Maps API request.
    
    Args:
        markers (str): URL parameter string for the markers.
        api_key (str): Google Maps API key.
    
    Returns:
        str: Complete URL for the API request.
    """
    url = "https://maps.googleapis.com/maps/api/staticmap?"
    url_complete = (
        url
        # + "center="
        # + center
        # + "&zoom="
        # + str(zoom)
        + "&size=400x400&key="
        + api_key
        + markers
        + "&style=feature:poi|visibility:off"
    )
    return url_complete

def main(locations_to_plot: list, api_key: str) -> None:
    """
    Main function to create a static map image with markers for specified locations.
    This function retrieves location data, filters the locations to plot, and generates a static map image.
    
    Args:
        locations_to_plot (list): List of location names to plot.
        api_key (str): Google Maps API key.
    
    Returns:
        None
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "output\\map_image.png")

    locations, id, geometry = gl.main(api_key)

    filt_locations, filt_id, filt_geometry = [], [], []
    for index, location in enumerate(locations):
        if location in locations_to_plot:
            filt_locations.append(location)
            filt_id.append(id[index])
            filt_geometry.append(geometry[index])

    markers = set_markers_on_map(filt_geometry)
    url = get_static_map_url(markers, api_key)
    print("API Call")
    r = requests.get(url)

    with open(image_path, "wb") as f:
        f.write(r.content)
    return

if __name__ == "__main__":
    a = ["Via Lazzaretto, 1 - 3, 20124 Milano MI"]
    main(locations_to_plot=a, api_key=os.getenv("GOOGLE_MAPS_API_KEY"))