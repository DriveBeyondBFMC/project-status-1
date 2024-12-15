import cv2
import matplotlib.pyplot as plt
import matplotlib
import rospy
from utils.msg import localisation
import threading
import signal
import sys
import numpy as np

# Sử dụng Qt5 để mở cửa sổ riêng
matplotlib.use('Qt5Agg')

# Load the image
image_path = "Track2025_2.png"  # Replace with the path to your image
image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

# Scale factora
scale_factor = 235.5

# Flag to check if the program should terminate
terminate_flag = False

# Kalman Filter optimized for 2D data
class KalmanFilterOptimized:
    def __init__(self, process_noise=1e-5, measurement_noise=1e-2, estimation_error=1.0, initial_values=[0.0, 0.0]):
        self.q = process_noise
        self.r = measurement_noise
        self.p = np.array([estimation_error, estimation_error])  # Sai số ước lượng
        self.x = np.array(initial_values)  # Giá trị ban đầu

    def update(self, measurements):
        # Prediction step
        self.p += self.q
        # Kalman Gain
        k = self.p / (self.p + self.r)
        # Update estimate
        self.x += k * (measurements - self.x)
        # Update error covariance
        self.p *= (1 - k)
        return self.x

# Initialize Kalman Filter
kf = KalmanFilterOptimized()

# Shared variables
raw_posA = 0
raw_posB = 0
pos_x = 0
pos_y = 0

# Lock for thread-safe operations
data_lock = threading.Lock()

# ROS callback to update raw positions
def localisation_callback(data):
    global raw_posA, raw_posB
    with data_lock:
        raw_posA = data.posA
        raw_posB = data.posB

def listener():
    # Đăng ký lắng nghe topic
    rospy.Subscriber('/automobile/localisation', localisation, localisation_callback)
    # Chờ và xử lý dữ liệu
    rospy.spin()

# Create a separate thread for ROS listener
def listener_thread():
    listener()

# Thread for Kalman Filter processing
def kalman_thread():
    global raw_posA, raw_posB, pos_x, pos_y
    while not terminate_flag:
        with data_lock:
            raw_data = np.array([raw_posA, raw_posB])
        # Apply Kalman filter
        filtered_data = kf.update(raw_data)
        with data_lock:
            pos_x, pos_y = filtered_data
        rospy.sleep(0.01)  # Điều chỉnh tốc độ xử lý Kalman nếu cần

# Display the image and location
def display_gui():
    global pos_x, pos_y

    fig, ax = plt.subplots(figsize=(16, 10))  # Adjust figsize as needed
    image_display = ax.imshow(image)
    point, = ax.plot([], [], 'ro', markersize=10, label='Filtered Location')  # Initialize point

    ax.set_title("Real-time Position Tracking")
    ax.legend()

    while not terminate_flag:
        # Update point without clearing entire plot
        with data_lock:
            x, y = pos_x, pos_y
        point.set_data(x * scale_factor, y * scale_factor)
        plt.pause(0.0001)  # Adjust pause time for smoother updates
    plt.show()

# Function to handle SIGINT (Ctrl+C) gracefully
def signal_handler(signal, frame):
    global terminate_flag
    print('Terminating the program...')
    terminate_flag = True
    plt.close()  # Close the matplotlib window
    sys.exit(0)  # Exit the program

if __name__ == '__main__':
    try:
        # Set up signal handler for graceful termination on Ctrl+C
        signal.signal(signal.SIGINT, signal_handler)

        # Khởi tạo node ROS trong luồng chính
        rospy.init_node('localisation_listener', anonymous=True)

        # Create and start listener thread
        listener_thread_instance = threading.Thread(target=listener_thread)
        listener_thread_instance.daemon = True
        listener_thread_instance.start()

        # Create and start Kalman filter thread
        kalman_thread_instance = threading.Thread(target=kalman_thread)
        kalman_thread_instance.daemon = True
        kalman_thread_instance.start()

        # Display the GUI
        display_gui()

    except rospy.ROSInterruptException:
        pass



# class interactive_map():
#     image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)




#     def __init__(self, image_path):
#         super().__init__()
#         self.image_path = image_path
#         self.selected_points = []  # Lưu các điểm đã chọn
#         self.init_ui()
#     def init_ui(self):
#         image = cv2.cvtColor(cv2.imread(self.image_path), cv2.COLOR_BGR2RGB)
#         self.fig, self.ax = plt.subplots(figsize=(16, 12))
#         self.canvas = FigureCanvas(self.fig)
#         self.ax.imshow(image)
#         rospy.loginfo("pos-x %2f. pox-y %2f", pos_x, pos_y)
#         self.ax.axis("on") 
#         central_widget = QWidget()
#         layout = QVBoxLayout()
#         layout.addWidget(self.canvas)
#         self.coord_label = QLabel(self)
#         layout.addWidget(self.coord_label)
#         central_widget.setLayout(layout)
#         self.setCentralWidget(central_widget)
#         self.setWindowTitle("Interactive Path Finder")
#         self.canvas.mpl_connect("button_press_event", self.on_click)
#     def on_click(self, event):
#         if event.xdata and event.ydata:
#             scale_factor = 15 / 3500
#             nearest_node = find_nearest_node(event.xdata, event.ydata, nodes)
#             self.selected_points.append(nearest_node)
#             print(f"Đã chọn: {nearest_node} (tọa độ gốc: {nodes[nearest_node]})")
#             scaled_x, scaled_y = nodes[nearest_node][0] * scale_factor, nodes[nearest_node][1] * scale_factor
#             print(f"Đã chọn (tọa độ tỷ lệ): ({scaled_x:.2f}, {scaled_y:.2f})")
#             self.ax.scatter(*nodes[nearest_node], color="red", s=100)
#             self.canvas.draw()
#             if len(self.selected_points) == 2:
#                 start, goal = self.selected_points
#                 path = a_star(start, goal, nodes, cost_map)
#                 self.draw_path(path)
#                 self.selected_points = []  # Reset danh sách
#     def draw_blue_dot(self, pos_x, pos_y):
#         self.ax.scatter(pos_x, pos_y, color="blue", s=100)  # Vẽ dấu chấm xanh dương với kích thước 100
#         self.canvas.draw()
#     def draw_path(self, path):
#         scale_factor_x = 14.0 / 3500
#         scale_factor_y = 14.5 / 3500

#         path_points = []
#         edge_points = []
#         for i in range(len(path) - 1):
#             if (path[i], path[i + 1]) in edges:
#                 path_points += edges[(path[i], path[i + 1])]
#                 edge_points += edges[(path[i], path[i + 1])]
#             elif (path[i + 1], path[i]) in edges:
#                 path_points += edges[(path[i + 1], path[i])]
#                 edge_points += edges[(path[i + 1], path[i])]
#             else:
#                 path_points += [nodes[path[i]], nodes[path[i + 1]]]

#         save_coordinates_to_file(path, nodes, edge_points, file_name="coordinates.txt")

#         # Vẽ đường đi
#         px, py = zip(*path_points)
#         self.ax.plot(px, py, color="yellow", linewidth=2)
#         self.canvas.draw()
