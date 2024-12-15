import cv2
import matplotlib.pyplot as plt
import matplotlib
import rospy
from utils.msg import localisation
import threading
import signal
import sys

matplotlib.use('Qt5Agg')

# Load image for GUI
image_path = "../Track2025_2.png"
image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

terminate_flag = False
raw_posA = 0
raw_posB = 0
scale_factor = 3500 / 15

data_lock = threading.Lock()

def localisation_callback(data):
    global raw_posA, raw_posB
    with data_lock:
        raw_posA = data.posA
        raw_posB = data.posB

def listener():
    rospy.Subscriber('/automobile/localisation', localisation, localisation_callback)
    rospy.spin()

def display_gui():
    global raw_posA, raw_posB

    # Thiết lập khung hình GUI một nửa 1920x1080 (960x540) với tỷ lệ 1:1
    fig, ax = plt.subplots(figsize=(960 / 100, 540 / 100))
    ax.set_title("Localization")
    ax.axis('off')  # Tắt trục để làm sạch giao diện

    # Hiển thị hình ảnh và giữ tỷ lệ 1:1
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
            x, y = raw_posA * scale_factor, raw_posB * scale_factor
        print(f"posA {raw_posA}, posB {raw_posB}")
        point.set_data(x, y)
        fig.canvas.draw()
        plt.pause(0.001)
    plt.ioff()
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

        display_gui()

    except rospy.ROSInterruptException:
        pass
