#!/usr/bin/env python3
import cv2
import matplotlib.pyplot as plt
import matplotlib
import pickle
import networkx as nx 

matplotlib.use('Qt5Agg')

def onclick(event):
    global current_node, edge_in_progress
    if event.xdata is not None and event.ydata is not None:
        x, y = int(event.xdata), int(event.ydata)
        
        if current_node is not None:
            edge_in_progress.append((x, y))
            print(f"({x}, {y})")
            ax.plot(x, y, 'ro')  
            if len(edge_in_progress) > 1:
                x_vals, y_vals = zip(*edge_in_progress)
                ax.plot(x_vals, y_vals, 'b-') 
            fig.canvas.draw()
        else:
            nearest_node = find_nearest_node(x, y)
            if nearest_node:
                current_node = nearest_node 
                edge_in_progress = [nearest_node]
                print(f"Start new edge from node: {nearest_node}")
                ax.plot(nearest_node[0], nearest_node[1], 'yo')
                fig.canvas.draw()

def find_nearest_node(x, y):
    """Find the nearest node within a given radius, or return None."""
    for node in nodes:
        if distance((x, y), node) <= node_radius:
            return node
    return None

def distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def save_to_sav(route_points, filename="route_points.sav"):
    with open(filename, 'wb') as file:
        pickle.dump(route_points, file)  
    print(f"Route points saved to {filename}")

def load_road_network(filename="route_points.sav"):
    with open(filename, 'rb') as file:
        data = pickle.load(file)
    return data

# Load the image
image_path = "../Track2025_2.png" 
image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

network_data = load_road_network("road_network.sav")

if isinstance(network_data, nx.Graph):
    nodes = list(network_data.nodes) 
    print(f"Nodes in the network: {nodes}")  
else:
    try:
        nodes = network_data["nodes"]
    except KeyError:
        print("Error: No 'nodes' key found in the data. Please check the structure of the .sav file.")
        exit()

current_node = None
edge_in_progress = []
node_radius = 30 

# Display the image
fig, ax = plt.subplots(figsize=(16, 10))  # Adjust figsize as needed
ax.imshow(image)
ax.set_title("Click to create a route. Close the window to finish.")

for i, node in enumerate(nodes):
    x, y = node  
    ax.plot(x, y, 'go')
    
    # Display the node number with white color (numbering starts from 1)
    ax.text(x + 5, y + 5, str(i + 1), color='white', fontsize=12, ha='center', va='center')

cid = fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()

save_to_sav(edge_in_progress)
