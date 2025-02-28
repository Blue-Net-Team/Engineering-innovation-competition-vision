import cv2
from utils import LoadWebCam, SendImg, Cap
from utils.ImgTrans import NeedReConnect

if __name__ == "__main__":
    stream = SendImg("wlan0", 4444)
    cap = Cap()
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
