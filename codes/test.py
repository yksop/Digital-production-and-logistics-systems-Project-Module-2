import distance_matrix as dm
import image_map_markers as imm
import get_routes as gr
import os

TARGET_WEEKDAY = 0  # Monday
TARGET_HOUR = 8
origin = (45.4772399, 9.2014099)
# destination = (45.4723886, 9.187370399999999)
# destination = (45.465549, 9.1756057)
# destination = (45.4630824, 9.1864809)
# destination = (45.4594456, 9.1828919)
destination = (45.462311, 9.183534)
n_route = 3

api_key= os.getenv("GOOGLE_MAPS_API_KEY")

# print(dm.main(TARGET_WEEKDAY, TARGET_HOUR, api_key))
# imm.main(api_key)
gr.main(origin, destination, n_route, api_key)


