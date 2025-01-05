import cv2
from utils import LoadWebCam, SendImg

if __name__ == "__main__":
    stream = SendImg("169.254.60.115", 8000)
    cap = cv2.VideoCapture(0)
    stream.connecting()
    stream.start()
    while True:
        img = cap.read()[1]
        stream.send(img)
