import json
import time
from typing import Callable
import cv2
import numpy as np
from Solution import Solution
from detector import (
    LineDetector,
    CircleDetector,
    TraditionalColorDetector,
)
from utils import LoadCap, LoadWebCam, ReceiveImg
from colorama import Fore, Style, init

# 初始化 colorama
init(autoreset=True)

class Ad_Config(Solution):
    """
    调整参数

    * 调整圆环参数，地面
    * 调整直线参数，canny算子参数
    * 调整颜色阈值
    """

    def __init__(
        self,
        cap_id: int = 0,
        ser_port: str|None = None,
        ip: str | None = None,
        port: int | None = None,
    ):
        super().__init__(ser_port)

        if ip is not None and port is not None:
            self.cap = LoadWebCam(ip, port)
        else:
            self.cap = LoadCap(cap_id,cap_method='opencv')

    def adjust_circle(self, config_name: str):
        """
        调整圆环参数
        ----
        Args:
            config_name (str): 配置名称,包含"material"(物料)、"annulus"(圆环)
        """
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        detector = self.annulus_circle_detector

        # 加载配置
        # detector.load_config("config.json", config_name)

        # 创建滑动条
        detector.createTrackbar()
        for img in self.cap:
            if img is None:
                continue
            t0 = time.perf_counter()

            try:
                read_img_time = t0 - t1
            except:
                read_img_time = 0

            res = self.annulus_circle_detector.detect_circle(img)
            t1 = time.perf_counter()

            points = res[0]
            radius = res[1]

            if points is None or radius is None:
                continue

            for point, r in zip(points, radius):
                cv2.circle(img, point, r, (0, 255, 0), 2)


            detect_time = t1 - t0

            process_time = read_img_time + detect_time
            fps = 1 / process_time

            cv2.putText(  # 显示FPS
                img,
                f"FPS: {fps:.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

            cv2.imshow("img", img)
            print(res)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                # 保存配置
                detector.save_config("config.json", config_name)
                # 释放摄像头
                self.cap.release()
                break

    def adjust_color_threshold(self, color_name: str="R"):
        """
        调整颜色阈值
        ----
        """
        tcd = TraditionalColorDetector()
        tcd.load_config("config.json")
        tcd.createTrackbar()
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        tcd.update_range(color_name)
        for img in self.cap:
            if img is None:
                continue

            new_img = img.copy()

            binarization_img = tcd.binarization(img)

            position = tcd.get_color_position(binarization_img)
            if position:
                point = position[:2]
                w, h = position[2:]

                # 画矩形
                cv2.rectangle(
                    new_img,
                    (point[0] - w // 2, point[1] - h // 2),
                    (point[0] + w // 2, point[1] + h // 2),
                    (0, 255, 0),
                    2,
                )
                # 画出中心点
                cv2.circle(new_img, (point[0], point[1]), 5, (0, 0, 255), -1)

            # 按位与的图
            and_img = cv2.bitwise_and(img, img, mask=binarization_img)

            res_img = np.vstack(
                (new_img, cv2.cvtColor(binarization_img, cv2.COLOR_GRAY2BGR), and_img)
            )

            cv2.imshow("img", res_img)

            key_pressed = cv2.waitKey(1)

            if key_pressed & 0xFF == ord("q"):
                break
            elif key_pressed & 0xFF == ord("s"):
                tcd.save_params("config.json")
                print(Fore.GREEN + "保存配置")

        self.cap.release()
        cv2.destroyAllWindows()


class Ad_Area_config:
    """
    调整位号的点位参数
    ----
    * 鼠标左键点击位号的左上角点
    * 鼠标右键点击位号的右下角点
    * 滑动条选择位号
    """
    area_dict: dict[int, list[tuple[int, int]]]
    x:int

    def __init__(self, _webcam:ReceiveImg|None=None) -> None:
        self.load_config()
        self.x = 0

        self.webcam = _webcam

    def load_config(self):
        """
        加载配置
        """
        with open("config.json", "r") as f:
            self.config = json.load(f)
        self.area_dict = {
            1: self.config["area1_points"],
            2: self.config["area2_points"],
            3: self.config["area3_points"],
        }

    def save_config(self):
        """
        保存配置
        """
        with open("config.json", "r") as f:
            self.config = json.load(f)

        self.config["area1_points"] = self.area_dict[1]
        self.config["area2_points"] = self.area_dict[2]
        self.config["area3_points"] = self.area_dict[3]

        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)

    def createTrackbar(self):
        cv2.namedWindow("trackbar", cv2.WINDOW_NORMAL)
        cv2.createTrackbar("id", "trackbar", 0, 2, self.__callback)

    def __callback(self, x: int):
        self.x = x

    def __mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.area_dict[self.x + 1][0] = (x, y)
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.area_dict[self.x + 1][1] = (x, y)

    def main(self):
        cv2.namedWindow("img", cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback("img", self.__mouse_callback)
        self.createTrackbar()

        if self.webcam is not None:
            cap = self.webcam
        else:
            cap = cv2.VideoCapture(0)
            cap.set(3, 640)
            cap.set(4, 480)
            cap.set(5, 60)
            cap.set(6,cv2.VideoWriter.fourcc('M','J','P','G'))

        while True:
            ret, img = cap.read()
            if img is None:
                continue
            for key, value in self.area_dict.items():
                cv2.rectangle(
                    img,
                    value[0],
                    value[1],
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    img,
                    f"area{key}",
                    value[0],
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
            cv2.imshow("img", img)
            key = cv2.waitKey(1)
            if key & 0xFF == ord("q"):
                break
            elif key & 0xFF == ord("s"):
                self.save_config()
                print(Fore.GREEN + "保存配置")


class Ad_Line_config(LineDetector):
    def __init__(self, _webcam:ReceiveImg|None=None) -> None:
        super().__init__()
        print(self.load_config("config.json"))
        self.webcam = _webcam

    def ad_line(self):
        self.createTrackbar()

        if self.webcam is None:
            cap = cv2.VideoCapture(0)
            cap.set(3, 640)
            cap.set(4, 480)
            cap.set(5, 60)
            cap.set(6,cv2.VideoWriter.fourcc('M','J','P','G'))
        else:
            cap = self.webcam

        while True:
            ret, img = cap.read()
            if img is None:
                continue

            lines = self.find_line(img)

            if lines is not None:
                nums = len(lines) if len(lines) < 5 else 5

                for i in range(nums):
                    self.draw_line(img, lines[i])

            cv2.imshow("img", img)
            key = cv2.waitKey(1)
            if key & 0xFF == ord("q"):
                break
            elif key & 0xFF == ord("s"):
                self.save_config("config.json")
                print(Fore.GREEN + "保存配置")

    def ad_right_angle(self):
        self.createTrackbar()

        if self.webcam is None:
            cap = cv2.VideoCapture(0)
            cap.set(3, 640)
            cap.set(4, 480)
            cap.set(5, 60)
            cap.set(6,cv2.VideoWriter.fourcc('M','J','P','G'))
        else:
            cap = self.webcam

        while True:
            ret, img = cap.read()
            if img is None:
                continue

            img = self.sharpen(img)
            angel1, angel2, point = self.get_right_angle(img, True)

            cv2.imshow("img", img)
            key = cv2.waitKey(1)
            if key & 0xFF == ord("q"):
                break
            elif key & 0xFF == ord("s"):
                self.save_config("config.json")
                print(Fore.GREEN + "保存配置")



if __name__ == "__main__":
    ad_config = Ad_Config(
            0,
    )
    # ad_config.adjust_circle("annulus")
    ad_config.adjust_color_threshold()
    # ad_area_config = Ad_Area_config()
    # ad_area_config.main()

    # ad_line_config = Ad_Line_config()
    # ad_line_config.ad_line()
    # ad_line_config.ad_right_angle()
# end main
