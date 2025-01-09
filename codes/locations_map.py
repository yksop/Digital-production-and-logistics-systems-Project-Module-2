import numpy as np
import os
import get_routes as gr
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

current_dir = os.path.dirname(os.path.abspath(__file__))


load_dotenv()
api_key=os.getenv("GOOGLE_MAPS_API_KEY")


def get_database() -> pd.DataFrame:
    """
    Get the database with the locations.
    
    Returns:
        pd.DataFrame: The database with the locations.
    """
    return pd.read_csv(os.path.join(current_dir, "data", "places_id.csv"))

def remove_images(image_path: str) -> None:
    """
    Remove all files and directories in the given path.
    
    Args:
        image_path (str): The path to the directory to remove.
    """
    for filename in os.listdir(image_path):
        file_path = os.path.join(image_path, filename)
        if os.path.isfile(file_path):
            if filename != "map_image.png":
            os.remove(file_path)
        elif os.path.isdir(file_path):
            for f in os.listdir(file_path):
                os.remove(os.path.join(file_path, f))
            os.rmdir(file_path)
    return None

def get_cordinates(database: pd.DataFrame, origin: int, destination: int) -> tuple:
    """
    Get the coordinates of the origin and destination from the database.
    
    Args:
        database (pd.DataFrame): The database with the locations.
        origin (int): The index of the origin location.
        destination (int): The index of the destination location.
    
    Returns:
        tuple: A tuple containing the coordinates of the origin and destination.
    """
    origin_cordinates = (database.loc[origin, "latitude"], database.loc[origin, "longitude"])
    destination_cordinates = (database.loc[destination, "latitude"], database.loc[destination, "longitude"])
    return origin_cordinates, destination_cordinates

def save_data() -> None:
    """
    Loads and returns vehicle data from .npy files in the output directory.
    This function searches for .npy files in the 'output' directory located
    in the current directory. It assumes that the filenames follow the 
    pattern 'vehicle<number>.npy', where <number> is an integer representing
    the vehicle number. The function loads the numpy arrays from these files
    and stores them in a dictionary with the vehicle number as the key.
    Returns:
        dict: A dictionary where the keys are vehicle numbers (int) and the 
              values are numpy arrays containing the vehicle data.
    """
    out_path = os.path.join(current_dir, "output")
    vehicles = {}
    for filename in os.listdir(out_path):
        if filename.endswith('.npy'):
            parts = filename.split('_')
            vehicle_number = int(filename.replace('vehicle', '').replace('.npy', ''))
            array = np.load(os.path.join(out_path, filename))
            vehicles[vehicle_number] = array
    return vehicles

def order_data(vehicles: dict) -> dict:
    """
    Orders the data of each vehicle in the input dictionary by the third column and removes any empty entries.

    Args:
        vehicles (dict): A dictionary where keys are vehicle identifiers and values are numpy arrays.
                         Each numpy array represents data associated with a vehicle, where the third column
                         is used for sorting.

    Returns:
        dict: A dictionary with the same structure as the input, but with the data of each vehicle sorted
              by the third column and any empty entries removed.
    """
    for k in sorted(vehicles.keys()):
        vehicles[k] = vehicles[k][vehicles[k][:, 2].argsort()]
        if vehicles[k].shape[0] == 0:
            del vehicles[k]
    return vehicles

def print_data(vehicles: dict) -> None:
    """
    Prints the data of vehicles in a sorted order by vehicle keys.
    Args:
        vehicles (dict): A dictionary where keys are vehicle identifiers and values are the corresponding vehicle data.
    Returns:
        None
    """
    for k in sorted(vehicles.keys()):
        print(f"Vehicle {k}:")
        print(vehicles[k])

def save_images(vehicles: dict, target_weekday: int, target_hour: int) -> None:
    """
    Saves images of vehicle routes.

    This function creates a directory for each vehicle in the provided dictionary,
    removes any existing images in the target directory, and saves new images of
    the routes taken by each vehicle. The routes are determined by the coordinates
    obtained from the database.

    Args:
        vehicles (dict): A dictionary where keys are vehicle identifiers and values
                         are lists of tuples representing routes. Each tuple contains
                         two elements: the origin and destination identifiers.

    Returns:
        None
    """
    image_path = os.path.join(current_dir, "images")
    remove_images(image_path)
    db = get_database()
    for v in sorted(vehicles.keys()):
        imag_p = os.path.join(image_path, str(v))
        os.mkdir(imag_p)
        for i, item in enumerate(vehicles[v]):
            origin, destination = get_cordinates(db, int(item[0]), int(item[1]))
            # print(f"Vehicle {v}, route {i+1}: {origin} - {destination}")
            gr.main(origin, destination, i, target_weekday, target_hour, api_key, imag_p)

def get_grapgh(vehicles: dict) -> None:
    """
    Generates and visualizes a directed graph representing vehicle routes.
    Parameters:
    vehicles (dict): A dictionary where keys are vehicle identifiers and values are lists of tuples.
                     Each tuple represents a route segment with the format (start_node, end_node, _, load).
    The function performs the following steps:
    1. Creates a directed graph using NetworkX.
    2. Adds edges to the graph based on the vehicle routes.
    3. Assigns labels to the edges indicating the load.
    4. Identifies cycles in the graph and assigns unique colors to edges forming cycles.
    5. Draws the graph with nodes, edges, and edge labels.
    6. Creates a legend mapping vehicle identifiers to colors.
    7. Displays the graph with a title "Vehicle Routes".
    Note:
    - The function uses a spring layout for node positioning.
    - Edge colors are assigned using the tab20 colormap from Matplotlib.
    - The function does not return any value; it displays the graph using Matplotlib.
    """
    G = nx.DiGraph()
    for v in sorted(vehicles.keys()):
        for i, item in enumerate(vehicles[v]):
            G.add_edge(int(item[0]), int(item[1]), label=f"Load: {round(item[3])}")
    pos = nx.shell_layout(G)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=1000, font_size=10)
    labels = nx.get_edge_attributes(G, "label")
    
    edge_colors = []
    for cycle in nx.simple_cycles(G):
        if cycle[0] == 0:
            color = plt.cm.tab20(len(edge_colors) / 20)
            for i in range(len(cycle) - 1):
                edge_colors.append((cycle[i], cycle[i + 1], color))
            edge_colors.append((cycle[-1], cycle[0], color))
    edge_colors_dict = {(u, v): color for u, v, color in edge_colors}
    edge_colors = [edge_colors_dict.get((u, v), 'black') for u, v in G.edges()]
    unique_labels = list(set(edge_colors))
    color_map = {label: plt.cm.tab20(i / len(unique_labels)) for i, label in enumerate(unique_labels)}
    edge_colors = [color_map[label] for label in edge_colors]
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=3)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color="red", font_size=8)

    legend_labels = {v: k for k, v in color_map.items()}
    handles = [plt.Line2D([0], [0], color=color, lw=2) for color in legend_labels.keys()]
    
    labels = [f"Vehicle {i}" for i in sorted(vehicles.keys())]
    plt.legend(handles, labels, title="Vehicles")


    plt.title("Vehicle Routes")
    plt.show()


def main() -> None:
    TARGET_WEEKDAY = 0
    TARGET_HOUR = 8
    
    vehicles = save_data()
    o_vehicles = order_data(vehicles)
    print_data(o_vehicles)
    # save_images(o_vehicles, TARGET_WEEKDAY, TARGET_HOUR)
    get_grapgh(o_vehicles)
    return None



if __name__ == "__main__":
    main()