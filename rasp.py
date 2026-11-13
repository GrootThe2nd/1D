import cv2
import numpy as np
from picamera2 import Picamera2
from PIL import Image
import time
import serial

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1.0)
time.sleep(3)
ser.reset_input_buffer()
print("Serial OK")
picam = Picamera2()
picam.start()

# BGR colour for red in OpenCV
target_color = [255, 0, 0]

def resize_frame_to_dimensions(frame, width, height):
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

def get_limits(color_bgr):
    c = np.uint8([[color_bgr]])
    hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    hue = hsvC[0][0][0]

    if hue >= 165:
        lower_limit = np.array([hue - 10, 100, 100], dtype=np.uint8)
        upper_limit = np.array([180, 255, 255], dtype=np.uint8)
    elif hue <= 15:
        lower_limit = np.array([0, 100, 100], dtype=np.uint8)
        upper_limit = np.array([hue + 10, 255, 255], dtype=np.uint8)
    else:
        lower_limit = np.array([hue - 10, 100, 100], dtype=np.uint8)
        upper_limit = np.array([hue + 10, 255, 255], dtype=np.uint8)

    return lower_limit, upper_limit

while True:
    frame = picam.capture_array()

    # PiCamera2 outputs RGB ? convert to BGR for OpenCV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    frame = resize_frame_to_dimensions(frame, 640, 480)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_limit, upper_limit = get_limits(target_color)

    mask = cv2.inRange(hsv, lower_limit, upper_limit)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest = max(contours, key=cv2.contourArea)
        x1, y1, w, h = cv2.boundingRect(largest)
        x2, y2 = x1 + w, y1 + h


        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)

        x_center = (x1 + x2) / 2
        y_center = (y1 + y2) / 2

        x_deg = ((x_center / 640) * 720)-360
        y_deg = ((y_center / 480) * 720)
        coord = int(x_deg)

        print("message Sent")
        print(f"{coord}")
        ser.write(f"{coord}\n".encode('utf-8'))
    else:
        print("No object detected")

    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

ser.write("0\n".encode('utf-8'))
picam.stop()
cv2.destroyAllWindows()

