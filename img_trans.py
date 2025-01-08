import cv2
from utils import LoadWebCam, SendImg
from utils.ImgTrans import NeedReConnect

if __name__ == "__main__":
    stream = SendImg("169.254.60.115", 4444)
    cap = cv2.VideoCapture(0)
    while True:
        if stream.connecting():
            break
    stream.start()
    while True:
        try:
            img = cap.read()[1]
            stream.send(img)
        except NeedReConnect:
            while True:
                if stream.connecting():
                    break
