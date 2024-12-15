#!/usr/bin/env python3
import matplotlib.pyplot as plt
import cv2
import math
from heapq import heappop, heappush
import pickle
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys

with open("../graph_data.sav", "rb") as file:
    data = pickle.load(file)

nodes = data["nodes"]
edges = data["edges"]

def calculate_cost(points):
    cost = 0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        cost += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return cost

cost_map = {}
for (start, end), points in edges.items():
    cost = calculate_cost(points)
    cost_map[(start, end)] = cost

def a_star(start, goal, nodes, cost_map):
    def heuristic(n1, n2):
        x1, y1 = nodes[n1]
        x2, y2 = nodes[n2]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    cost_so_far = {start: 0}

    while open_set:
        _, current = heappop(open_set)

        if current == goal:
            break

        for neighbor in nodes:
            if (current, neighbor) in cost_map:
                new_cost = cost_so_far[current] + cost_map[(current, neighbor)]
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + heuristic(neighbor, goal)
                    heappush(open_set, (priority, neighbor))
                    came_from[neighbor] = current

    path = []
    current = goal
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path

def find_nearest_node(x, y, nodes):
    min_dist = float('inf')
    nearest_node = None
    for node, (nx, ny) in nodes.items():
        dist = math.sqrt((nx - x) ** 2 + (ny - y) ** 2)
        if dist < min_dist:
            min_dist = dist
            nearest_node = node
    return nearest_node

class InteractiveMap(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.selected_points = []  # Lưu các điểm đã chọn
        self.init_ui()

    def init_ui(self):
        image = cv2.cvtColor(cv2.imread(self.image_path), cv2.COLOR_BGR2RGB)

        self.fig, self.ax = plt.subplots(figsize=(16, 12))
        self.canvas = FigureCanvas(self.fig)

        self.ax.imshow(image)
        self.ax.axis("on")  # Bật trục tọa độ

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        self.coord_label = QLabel(self)
        layout.addWidget(self.coord_label)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle("Interactive Path Finder")

        self.canvas.mpl_connect("button_press_event", self.on_click)

    def on_click(self, event):
        if event.xdata and event.ydata:
            scale_factor = 15 / 3500

            nearest_node = find_nearest_node(event.xdata, event.ydata, nodes)
            self.selected_points.append(nearest_node)
            
            scaled_x, scaled_y = nodes[nearest_node][0] * scale_factor, nodes[nearest_node][1] * scale_factor

            self.ax.scatter(*nodes[nearest_node], color="red", s=100)
            self.canvas.draw()

            if len(self.selected_points) == 2:
                start, goal = self.selected_points
                path = a_star(start, goal, nodes, cost_map)
                self.draw_path(path)
                self.selected_points = []  # Reset danh sách

    def draw_path(self, path):
        scale_factor = 15 / 3500

        path_points = []
        edge_points = []
        for i in range(len(path) - 1):
            if (path[i], path[i + 1]) in edges:
                path_points += edges[(path[i], path[i + 1])]
                edge_points += edges[(path[i], path[i + 1])]
            elif (path[i + 1], path[i]) in edges:
                path_points += edges[(path[i + 1], path[i])]
                edge_points += edges[(path[i + 1], path[i])]
            else:
                path_points += [nodes[path[i]], nodes[path[i + 1]]]

        node_coords = [
            f"{node}: ({nodes[node][0] * scale_factor:.2f}, {nodes[node][1] * scale_factor:.2f})"
            for node in path
        ]
        edge_coords = [
            f"({x * scale_factor:.2f}, {y * scale_factor:.2f})"
            for x, y in edge_points
        ]
        print("\n".join(node_coords))
        print(f"Edge points between {path[0]} and {path[-1]}: {', '.join(edge_coords)}")

        px, py = zip(*path_points)
        self.ax.plot(px, py, color="yellow", linewidth=2)
        self.canvas.draw()

image_path = "../Track2025_2.png"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InteractiveMap(image_path)
    window.show()
    sys.exit(app.exec_())