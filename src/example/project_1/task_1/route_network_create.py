#!/usr/bin/env python3
import cv2
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pickle
crossroad_counter = 0

# Initialize graph
road_network = nx.Graph()  # Use nx.DiGraph() for directed roads

# Data structures
crossroads = []  # All crossroads
selected_nodes = []  # Nodes selected for route creation
edges = []
node_radius = 30  # Radius to detect nearby nodes for selection

# Mode tracking
mode = "select_nodes"  # Modes: 'select_nodes' or 'add_routes'

def distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def find_nearest_node(x, y):
    """Find the nearest node within a given radius, or return None."""
    for node in crossroads:
        if distance((x, y), node) <= node_radius:
            return node
    return None

def onclick(event):
    """Handle mouse clicks based on the current mode."""
    global mode
    global crossroad_counter

    if event.xdata is not None and event.ydata is not None:
        x, y = int(event.xdata), int(event.ydata)
        if mode == "select_nodes":
            nearest_node = find_nearest_node(x, y)
            if nearest_node:
                print(f"Node is already added")
                ax.plot(nearest_node[0], nearest_node[1], 'yo')  # Highlight selected node
            else:
                crossroads.append((x, y))
                road_network.add_node((x, y))
                print(f"'{crossroad_counter}': ({x}, {y}),")
                crossroad_counter += 1
                ax.plot(x, y, 'go')  # Green dot for new node

                # Display the node number with white color
                ax.text(x + 5, y + 5, str(crossroad_counter), color='white', fontsize=12, ha='center', va='center')
                
            fig.canvas.draw()
        
        elif mode == "add_routes":
            nearest_node = find_nearest_node(x, y)
            if nearest_node:
                print(f"Selected node for route creation: {nearest_node}")
                selected_nodes.append(nearest_node)
                ax.plot(nearest_node[0], nearest_node[1], 'yo')  # Highlight selected node
                fig.canvas.draw()

                # If two nodes are selected, create a route
                if len(selected_nodes) == 2:
                    p1, p2 = selected_nodes
                    cost = distance(p1, p2)
                    edges.append((p1, p2))
                    road_network.add_edge(p1, p2, weight=cost)  # Add edge to the graph
                    print(f"Road added between: {p1} and {p2}")
                    
                    # Draw the road
                    x_vals, y_vals = zip(*[p1, p2])
                    ax.plot(x_vals, y_vals, 'r-')  # Red line for the road
                    fig.canvas.draw()
                    selected_nodes.clear()  # Clear selection for next route

def on_key(event):
    """Handle Enter key to switch modes."""
    global mode

    if event.key == "enter":
        if mode == "select_nodes":
            mode = "add_routes"
            print("Switched to route creation mode. Select two nodes to connect them.")
            ax.set_title("Route Creation Mode: Click two nodes to create a route.")
        elif mode == "add_routes":
            print("Already in route creation mode. Continue selecting nodes.")
        fig.canvas.draw()

# Load the map
image_path = "../Track2025_2.png"  # Replace with the path to your map image
image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

fig, ax = plt.subplots(figsize=(12, 8))
ax.imshow(image)
ax.set_title("Node Selection Mode: Click to add/select nodes. Press Enter to switch modes.")

fig.canvas.mpl_connect('button_press_event', onclick)
fig.canvas.mpl_connect('key_press_event', on_key)

plt.show()

print("Crossroads (nodes):", crossroads)
print("Roads (edges):", edges)

nx.draw(road_network, with_labels=True, node_color='lightblue', font_weight='bold')
plt.show()

pickle.dump(road_network, open('road_network.sav', 'wb'))  

