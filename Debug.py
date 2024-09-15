"""
用于调整ROI的文件
----
* 封装了远程图传的用法
* 封装了调整ROI的类，可以用鼠标来直接点击ROI的位置
"""

import cv2
import json
import socket
import numpy as np
from img_trans import ReceiveImg


class ROILocater(object):
    x0 = 0
    y0 = 0
    x1 = 20
    y1 = 20

    def __init__(self, cap: cv2.VideoCapture | ReceiveImg) -> None:
        self.cap = cap
        pass

    def draw_ROI(self, _frame: cv2.typing.MatLike):
        frame = _frame.copy()
        cv2.rectangle(frame, (self.x0, self.y0), (self.x1, self.y1), (0, 255, 0), 1)
        return frame

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.x0, self.y0 = x - 10, y - 10
            self.x1, self.y1 = x + 10, y + 10

            with open("ROI.json", "w") as f:
                ROI = [self.x0, self.y0, self.x1, self.y1]
                json.dump(ROI, f)

    def locate(self):
        cv2.namedWindow("locate")
        cv2.setMouseCallback("locate", self.mouse_callback)

        while True:
            ret, self.ori_img = self.cap.read()
            if self.ori_img is None:
                continue

            res_img = self.draw_ROI(self.ori_img)

            cv2.imshow("locate", res_img)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    def show_only(self):
        while True:
            ret, frame = self.cap.read()
            if frame is None:
                continue
            cv2.imshow("locate", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break


if __name__ == "__main__":
    cap = ReceiveImg("192.168.137.141", 8000)
    locater = ROILocater(cap)

    # locater.locate()      # 用于调整ROI
    locater.show_only()     # 用于单纯接收图传图像
    cv2.destroyAllWindows()
