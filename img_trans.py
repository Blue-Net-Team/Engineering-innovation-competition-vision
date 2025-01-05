import cv2
from utils import LoadWebCam, SendImg

if __name__ == "__main__":
    stream = SendImg("192.168.137.141", 8000)
    cap = cv2.VideoCapture(0)
    stream.connecting()
    stream.start()
    while True:
        img = cap.read()[1]
        stream.send(img)
