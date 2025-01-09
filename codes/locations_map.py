import numpy as np
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(current_dir, "output")

alpha = 0.0
vehicles = {}
for filename in os.listdir(out_path):
    if filename.endswith('.npy'):
        parts = filename.split('_')
        vehicle_number = int(parts[0].replace('vehicle', ''))
        alpha_value = float(parts[1].replace('alpha', '').replace('.npy', ''))
        if alpha_value == alpha:
            array = np.load(os.path.join(out_path, filename))
            print(array)
            vehicles[vehicle_number] = array

# print(vehicles[2])



# for k in vehicles.keys():
#     print(f"Vehicle {k}: {vehicles[k]}")