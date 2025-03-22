import cv2

from ImgTrans import LoadWebCam

if __name__ == "__main__":
    cap = LoadWebCam("169.254.133.100", 4444)
    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    for img in cap:
        if img is None:
            continue
        cv2.imshow("img", img)
        if cv2.waitKey(1) == ord("q"):
            break
