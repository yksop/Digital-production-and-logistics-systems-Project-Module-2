import numpy as np
import os
import get_routes as gr
from dotenv import load_dotenv
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(current_dir, "output")
image_path = os.path.join(current_dir, "images")

load_dotenv()
api_key=os.getenv("GOOGLE_MAPS_API_KEY")

TARGET_WEEKDAY = 0
TARGET_HOUR = 8

db = pd.read_csv(os.path.join(current_dir, "data", "places_id.csv"))


def remove_images(image_path: str) -> None:
    """
    Remove all files and directories in the given path.
    
    Args:
        image_path (str): The path to the directory to remove.
    """
    for filename in os.listdir(image_path):
        file_path = os.path.join(image_path, filename)
        if os.path.isfile(file_path):
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

alpha = 0.0
vehicles = {}
for filename in os.listdir(out_path):
    if filename.endswith('.npy'):
        parts = filename.split('_')
        vehicle_number = int(parts[0].replace('vehicle', ''))
        alpha_value = float(parts[1].replace('alpha', '').replace('.npy', ''))
        if alpha_value == alpha:
            array = np.load(os.path.join(out_path, filename))
            vehicles[vehicle_number] = array


n_v = {}
for k in sorted(vehicles.keys(), reverse=True):
    if k == 0:
        n_v[k] = vehicles[k]
    else:    
        for item in vehicles[k]:
            if item not in vehicles[k-1]:
                if k not in n_v:
                    n_v[k] = np.array([item])
                else:
                    n_v[k] = np.vstack((n_v[k], np.array(item)))



remove_images(image_path)
for k in sorted(n_v.keys()):
    # print(f"Vehicle {k}:")
    n_v[k] = n_v[k][n_v[k][:, 2].argsort()]
    # print(n_v[k])

for v in sorted(n_v.keys()):
    imag_p = os.path.join(image_path, str(v))
    os.mkdir(imag_p)
    for i, item in enumerate(n_v[v]):
        origin, destination = get_cordinates(db, int(item[0]), int(item[1]))
        print(f"Vehicle {v}, route {i+1}: {origin} - {destination}")
        gr.main(origin, destination, i, 0, 8, api_key, imag_p)
