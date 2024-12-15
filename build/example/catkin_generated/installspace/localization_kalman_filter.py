import cv2
import matplotlib.pyplot as plt
import matplotlib
import rospy
from utils.msg import localisation
import threading
import signal
import sys
import numpy as np

matplotlib.use('Qt5Agg')

# Load image for GUI
image_path = "Track2025_2.png" 
image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

scale_factor = 3500 / 15

terminate_flag = False

# Kalman Filter class with dynamic noise adjustment
class KalmanFilterOptimized:
    def __init__(self, process_noise=1e-5, measurement_noise=1e-2, estimation_error=1.0, initial_values=[0.0, 0.0]):
        self.q = process_noise
        self.r = measurement_noise
        self.p = np.array([estimation_error, estimation_error])  # Estimation error
        self.x = np.array(initial_values)  # Initial state

    def update(self, measurements):
        self.p += self.q
        k = self.p / (self.p + self.r)
        self.x += k * (measurements - self.x)
        self.p *= (1 - k)
        return self.x

    def adjust_noise(self, signal_change_rate):
        # Dynamically adjust process noise based on signal change rate
        self.q = max(1e-7, min(1e-5, 1e-6 / (signal_change_rate + 1)))

# Initialize Kalman Filter
kf = KalmanFilterOptimized()

raw_posA = 0
raw_posB = 0
pos_x = 0
pos_y = 0

data_lock = threading.Lock()

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

    while not terminate_flag:
        with data_lock:
            raw_data = np.array([raw_posA, raw_posB])
        
        # Calculate signal change rate
        signal_change_rate = np.linalg.norm(raw_data - prev_raw_data)
        kf.adjust_noise(signal_change_rate)
        
        # Apply Kalman Filter
        filtered_data = kf.update(raw_data)
        
        with data_lock:
            pos_x, pos_y = filtered_data
        prev_raw_data = raw_data
        rospy.sleep(0.01)

def display_gui():
    global pos_x, pos_y

    fig, ax = plt.subplots(figsize=(960 / 100, 540 / 100))
    ax.set_title("Localization with kalman filter")
    ax.axis('off')  # Tắt trục để làm sạch giao diện

    image_display = ax.imshow(image, interpolation='bilinear', aspect='equal')
    ax.set_xlim(0, image.shape[1])  # Giới hạn khung theo chiều rộng ảnh
    ax.set_ylim(image.shape[0], 0)  # Giới hạn khung theo chiều cao ảnh, đảo ngược để trục Y tăng lên trên
    ax.set_aspect('equal')  # Đặt tỷ lệ 1:1 cho hình vuông

    # Thêm điểm để hiển thị vị trí
    point, = ax.plot([], [], 'ro', markersize=10, label='Location')
    ax.legend()

    plt.ion()  # Bật chế độ tương tác

    while not terminate_flag:
        with data_lock:
            x, y = pos_x, pos_y
        point.set_data(x, y)
        plt.pause(0.0001) 
    plt.ioff()
    plt.show()

def plot_results(raw_data, filtered_data):
    plt.figure(figsize=(10, 6))
    plt.plot(raw_data[:, 0], raw_data[:, 1], 'g-', label='Raw Data (posA, posB)')
    plt.plot(filtered_data[:, 0], filtered_data[:, 1], 'r-', label='Filtered Data (posX, posY)')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.legend()
    plt.title('Comparison of Raw vs Filtered Data')
    plt.show()

def signal_handler(signal, frame):
    global terminate_flag
    print('Terminating the program...')
    terminate_flag = True
    plt.close() 
    sys.exit(0)

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

        display_gui()

    except rospy.ROSInterruptException:
        pass
