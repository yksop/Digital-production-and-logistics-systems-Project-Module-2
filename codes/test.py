from dotenv import load_dotenv
import get_location_info as gli
import distance_matrix as dm
import image_map_markers as imm
import get_routes as gr
import os

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))


def test_get_location_info(api_key: str) -> None:
    """
    The file locations.txt can be changed and when executed this function, the database in places_id.csv will be updated.
    """
    gli.main(api_key)


def test_distance_matrix(api_key: str) -> None:
    """
    This function will create a time matrix in minutes for all the locations in the database.
    Args:
        TARGET_WEEKDAY (int): The target weekday (0=Monday, 6=Sunday).
        TARGET_HOUR (int): The target hour (24-hour format).
        api_key (str): Google Maps API key.

    """
    TARGET_WEEKDAY = 0  # Day of the week (0=Monday, 6=Sunday)
    TARGET_HOUR = 8  # Hour of the day (24-hour format)s
    matrix_time, matrix_distance = dm.main(TARGET_WEEKDAY, TARGET_HOUR, api_key)
    print(matrix_time)
    print("\n\n")
    print(matrix_distance)


def test_image_map_markers(api_key: str) -> None:
    """
    This function will create a map with markers of the points passed as argument.
    The points need to be in the database. Or can be added in locations.txt and executing get_location_info.main(api_key)
    Args:
        locations_to_plot (list): List of location names to plot.
        api_key (str): Google Maps API key.
    """
    path_loc = os.path.join(current_dir, "data\\locations.txt")
    locations_to_plot = gli.get_location_from_file(path_loc)
    imm.main(locations_to_plot, api_key)


def test_get_routes(api_key: str) -> None:
    """
    This function will create a map with the route between two points.
    Args:
        origin (tuple): Tuple containing latitude and longitude of the origin.
        destination (tuple): Tuple containing latitude and longitude of the destination.
        n_route (int): Number of the route to be saved.
        TARGET_WEEKDAY (int): The target weekday (0=Monday, 6=Sunday).
        TARGET_HOUR (int): The target hour (24-hour format).
        api_key (str): Google Maps API key.
    """
    origin = (45.4772399, 9.2014099)
    destination = (45.462311, 9.183534)
    n_route = 1
    TARGET_WEEKDAY = 0
    TARGET_HOUR = 8
    gr.main(origin, destination, n_route, TARGET_WEEKDAY, TARGET_HOUR, api_key)


def main() -> None:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    # test_get_location_info(api_key)  # run this when locations.txt is changed
    # test_distance_matrix(api_key)
    test_image_map_markers(api_key)
    # test_get_routes(api_key)


if __name__ == "__main__":
    main()
