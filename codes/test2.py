import matplotlib.pyplot as plt
import networkx as nx

# Data
routes = {
    "Vehicle_1": [("A", "B", 10), ("B", "C", 8)],
    "Vehicle_2": [("D", "E", 15), ("E", "F", 10)],
}

# Create a graph
G = nx.DiGraph()

# Add edges with loads as weights
for vehicle, route in routes.items():
    for node1, node2, load in route:
        G.add_edge(node1, node2, weight=load, label=f"{vehicle} ({load})")

# Draw the graph
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=3000, font_size=10)
labels = nx.get_edge_attributes(G, "label")
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color="red")

plt.title("Vehicle Routes")
plt.show()
