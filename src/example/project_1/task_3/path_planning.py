import matplotlib.pyplot as plt
import cv2
import math
from heapq import heappop, heappush
import pickle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import rospy
from utils.msg import localisation
import threading
import signal
import sys
import numpy as np
with open("../graph_data.sav", "rb") as file:
    data = pickle.load(file)
terminate_flag = False
image_path = "../Track2025_2.png"


raw_posA = 0
raw_posB = 0
pos_x = 0
pos_y = 0
scale_factor = 3500 / 15
data_lock = threading.Lock()
nodes = data["nodes"]
edges = data["edges"]
image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
fig, ax = plt.subplots(figsize=(16, 12))


class KalmanFilterOptimized:
    def __init__(self, process_noise=1e-5, measurement_noise=1e-2, estimation_error=1.0, initial_values=[0.0, 0.0]):
        self.q = process_noise
        self.r = measurement_noise
        self.p = np.array([estimation_error, estimation_error])
        self.x = np.array(initial_values)

    def update(self, measurements):
        self.p += self.q
        k = self.p / (self.p + self.r)
        self.x += k * (measurements - self.x)
        self.p *= (1 - k)
        return self.x
    def adjust_noise(self, signal_change_rate):
        self.q = max(1e-7, min(1e-5, 1e-6 / (signal_change_rate + 1)))



def localisation_callback(data):
    global raw_posA, raw_posB
    with data_lock:
        raw_posA = data.posA * scale_factor
        raw_posB = data.posB * scale_factor

def listener():
    rospy.Subscriber('/automobile/localisation', localisation, localisation_callback)
    rospy.spin()



def kalman_thread():
    global raw_posA, raw_posB, pos_x, pos_y
    prev_raw_data = np.array([0.0, 0.0])
    kf = KalmanFilterOptimized()
    point, = ax.plot([], [], 'bo',markersize=10)
    while not rospy.is_shutdown():
        point.set_data(pos_x, pos_y)
        with data_lock:
            raw_data = np.array([raw_posA, raw_posB])
        signal_change_rate = np.linalg.norm(raw_data - prev_raw_data)
        kf.adjust_noise(signal_change_rate)
        
        filtered_data = kf.update(raw_data)
        with data_lock:
            pos_x, pos_y = filtered_data
        ax.figure.canvas.draw_idle()
        rospy.sleep(0.001)

def save_coordinates_to_file(path, nodes, edge_points, file_name="coordinates.txt"):
    scale_factor_x = 15 / 3500
    scale_factor_y = 15 / 3500

    with open(file_name, "w") as file:
        file.write("Nodes:\n")
        for node in path:
            x, y = nodes[node]
            scaled_x, scaled_y = x * scale_factor_x, y * scale_factor_y
            file.write(f"{node}: ({scaled_x:.2f}, {scaled_y:.2f})\n")

        file.write("\nEdge Points:\n")
        for x, y in edge_points:
            scaled_x, scaled_y = x * scale_factor_x, y * scale_factor_y
            file.write(f"({scaled_x:.2f}, {scaled_y:.2f})\n")

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

    


def signal_handler(signal, frame):
    global pos_x, pos_y
    global terminate_flag
    print('Terminating the program...')
    terminate_flag = True
    plt.close() 
    sys.exit(0) 



def interactive_map(image_path):
    
    ax.imshow(image)
    ax.axis("on")

    selected_points = [] 
    global terminate_flag
    terminate_flag = False  


    def on_click(event):
        if event.xdata and event.ydata:
            scale_factor = 15 / 3500
            nearest_node = find_nearest_node(event.xdata, event.ydata, nodes)
            selected_points.append(nearest_node)
          
            scaled_x, scaled_y = nodes[nearest_node][0] * scale_factor, nodes[nearest_node][1] * scale_factor
            
            ax.scatter(*nodes[nearest_node], color="red", s=100)
            plt.draw()
            if len(selected_points) == 2:
                start, goal = selected_points
                path = a_star(start, goal, nodes, cost_map)
                draw_path(path)
                selected_points.clear() 

   
    def draw_path(path):
        scale_factor_x = 14.0 / 3500
        scale_factor_y = 14.5 / 3500

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

        save_coordinates_to_file(path, nodes, edge_points, file_name="coordinates.txt")

  
        px, py = zip(*path_points)
        ax.plot(px, py, color="yellow", linewidth=2)
        plt.draw()

  
    fig.canvas.mpl_connect("button_press_event", on_click)

   
    plt.show()



if __name__ == '__main__':
    try:
        signal.signal(signal.SIGINT, signal_handler)
        rospy.init_node('localisation_listener', anonymous=True)
        listener_thread_instance = threading.Thread(target=listener)
        listener_thread_instance.daemon = True
        listener_thread_instance.start()
        kalman_thread_instance = threading.Thread(target=kalman_thread)
        kalman_thread_instance.daemon = True
        kalman_thread_instance.start()


        image_path = "../Track2025_2.png"
        interactive_map(image_path)
        
    except rospy.ROSInterruptException:
        pass
