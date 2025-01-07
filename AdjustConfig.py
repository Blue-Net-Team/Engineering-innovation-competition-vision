import json
import time
import cv2
import numpy as np
from Solution import Solution
from detector import LineDetector
from utils import ReceiveImg, Cap
from colorama import Fore, init

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
        _cap:cv2.VideoCapture|Cap|ReceiveImg,
        ser_port: str|None = None,
    ):
        super().__init__(ser_port)

        self.cap = _cap

    def adjust_circle(self):
        """
        调整圆环参数
        ----
        """
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        detector = self.annulus_circle_detector

        # 创建滑动条
        detector.createTrackbar()
        while True:
            t0 = time.perf_counter()
            _, img = self.cap.read()

            if img is None:
                continue

            res = self.annulus_circle_detector.detect_circle(img)
            t1 = time.perf_counter()

            points = res[0]
            radius = res[1]

            if points is None or radius is None:
                continue

            for point, r in zip(points, radius):
                cv2.circle(img, point, r, (0, 255, 0), 2)

            detect_time = t1 - t0

            fps = 1 / detect_time

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

            press_key = cv2.waitKey(1)
            if press_key & 0xFF == ord("q"):
                # 释放摄像头
                self.cap.release()
                break
            elif press_key & 0xFF == ord("s"):
                # 保存配置
                detector.save_config("config.json", "annulus")
                print(Fore.GREEN + "保存配置")

    def adjust_color_threshold(self, color_name: str="R"):
        """
        调整颜色阈值
        ----
        """
        self.traditional_color_detector.createTrackbar()
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        self.traditional_color_detector.update_range(color_name)
        while True:
            _, img = self.cap.read()
            if img is None:
                continue

            new_img = img.copy()

            binarization_img = self.traditional_color_detector.binarization(img)

            position = self.traditional_color_detector.get_color_position(binarization_img)
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
                self.traditional_color_detector.save_params("config.json")
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

    def __init__(self, _cap:cv2.VideoCapture|Cap|ReceiveImg,) -> None:
        self.load_config()
        self.x = 0

        self.cap = _cap

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

        while True:
            _, img = self.cap.read()
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
    def __init__(self, _cap:cv2.VideoCapture|Cap|ReceiveImg,) -> None:
        super().__init__()
        print(self.load_config("config.json"))
        self.cap = _cap

    def ad_line(self):
        self.createTrackbar()

        while True:
            _, img = self.cap.read()
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

        while True:
            ret, img = self.cap.read()
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


def ad_color(_cap:cv2.VideoCapture|Cap|ReceiveImg):
    ad_config = Ad_Config(_cap)
    ad_config.adjust_color_threshold()

def ad_circle(_cap:cv2.VideoCapture|Cap|ReceiveImg):
    ad_config = Ad_Config(_cap)
    ad_config.adjust_circle()

def ad_area(_cap:cv2.VideoCapture|Cap|ReceiveImg):
    ad_area_config = Ad_Area_config(_cap)
    ad_area_config.main()

def ad_line(_cap:cv2.VideoCapture|Cap|ReceiveImg):
    ad_line_config = Ad_Line_config(_cap)
    ad_line_config.ad_line()

def ad_right_angle(_cap:cv2.VideoCapture|Cap|ReceiveImg):
    ad_line_config = Ad_Line_config(_cap)
    ad_line_config.ad_right_angle()


if __name__ == "__main__":
    cap = Cap(0)

    ad_color(cap)
    # ad_area(cap)
    # ad_circle(cap)
    # ad_line(cap)
# end main
