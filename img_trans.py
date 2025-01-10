import cv2
from utils import LoadWebCam, SendImg

if __name__ == "__main__":
    cap = LoadWebCam("169.254.60.115", 4444)
    for img in cap:
        if img is None:
            continue
        cv2.imshow("img", img)
        if cv2.waitKey(1) == ord("q"):
            break
