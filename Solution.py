"""
解决方案
====
与电控对接的顶层需求，包含了所有的检测和串口通信功能
"""

import json
import cv2
import numpy as np
from USART.communicate import Usart
import detector

COLOR_DIC = {0: "R", 1: "G", 2: "B", 3: "W"}


def show(img):
    return cv2.imshow("img", img)


class Solution:
    def __init__(self, pth_path: str, ser_port: str):
        """
        解决方案
        ----
        Args:
            pth_path (str): pytorch模型路径
            ser_port (str): 串口号
        """
        self.material_circle_detector = detector.CircleDetector()
        self.annulus_circle_detector = detector.CircleDetector()
        self.color_detector = detector.ColorDetector(pth_path)
        self.line_detector = detector.LineDetector()
        self.uart = Usart(ser_port)

        # region 读取配置文件
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.point: list[int] = config["point"]
        except:
            self.point = [0, 0]

        self.material_circle_detector.load_config("config.json", "material")
        self.annulus_circle_detector.load_config("config.json", "annulus")
        # endregion

    def material_detect(self, _img):
        """
        材料检测
        ----
        本方法会在传入的图像上画出圆形区域和颜色识别区

        Args:
            _img (np.ndarray): 图片
        Returns:
            str|None: 颜色
        """
        img = _img.copy()
        img_sharpen = self.material_circle_detector.sharpen(img)  # 锐化
        points, rs = self.material_circle_detector.detect_circle(
            img_sharpen
        )  # 检测圆形
        if points is not None and rs is not None:
            for point, r in zip(points, rs):
                # 颜色识别区顶点
                pt0 = (int(point[0] - 10), int(point[1] - 10))
                pt1 = (int(point[0] + 10), int(point[1] + 10))

                # 颜色识别区
                ROI_img = img[pt0[1] : pt1[1], pt0[0] : pt1[0]]
                try:
                    # 颜色识别
                    color, prob = self.color_detector.detect(ROI_img)
                except:
                    color, prob = "?", 1.0

                cv2.rectangle(_img, pt0, pt1, (0, 255, 0), 1)
                cv2.circle(_img, point, r, (0, 255, 0), 1)
                cv2.putText(
                    _img,
                    f"{color}, {prob:.2f}",
                    (point[0], point[1] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )
            return color
        return None

    def annulus_detect(self, _img):
        """
        圆环检测
        ----
        本方法会在传入的图像上画出圆环和圆心

        Args:
            _img (np.ndarray): 图片
        Returns:
            err (None|list): 如果检测到圆环则返回None，否则返回颜色和圆心坐标与标准位置的偏差

            `[[color, [dx,dy]],...]`
        """
        res_dict = {color: [] for color in COLOR_DIC.values()}

        img = _img.copy()
        img_sharpen = self.annulus_circle_detector.sharpen(img)
        points, rs = self.annulus_circle_detector.detect_circle(img_sharpen)
        if points is None or rs is None:
            return None

        for point, r in zip(points, rs):
            # 在原图上绘制圆环
            cv2.circle(_img, point, r, (0, 255, 0), 1)
            cv2.circle(_img, point, 1, (255, 0, 0), 1)

            color, _, _ = self.detect_circle_edge_color(_img, point, r)
            res_dict[color].append(point)

        # 将结果字典的坐标列表进行平均值计算
        for color in res_dict:
            res_dict[color] = (
                np.mean(res_dict[color], axis=0) if res_dict[color] else []
            )

        # 结果列表
        errs = [
            (
                [
                    color,
                    [
                        res_dict[color][0] - self.point[0],
                        res_dict[color][1] - self.point[1],
                    ],
                ]
                if res_dict[color]
                else [color, None]
            )
            for color in res_dict
        ]

        # 将结果列表转换成字符串，例如：
        # "RFFFFFFFFG00421432B13450002"代表红色未检测到，绿色偏差-42,432，蓝色偏差345,2
        # 以颜色字母开头，下一个01表示正负号，后面的数字表示偏差(补全成3位，FFF表示未检测到)
        res = "".join(
            [
                f"{color}{'0' if err[1][0] < 0 else '1'}{str(err[1][0]).rjust(3, '0')}{'0' if err[1][1] < 0 else '1'}{str(err[1][1]).rjust(3, '0')}"
                for color, err in errs
            ]
        )

        return res

    def detect_circle_edge_color(
        self, _img: cv2.typing.MatLike, point: list[int] | tuple[int], r: int
    ):
        """
        识别圆环的颜色
        ----
        *此方法不是顶层需求*

        Args:
            _img (cv2.typing.MatLike): 传入图片
            point (Iterable[int]): 圆心坐标
            r (int): 圆半径
        Returns:
            tuple: 颜色、重构的图片和ROI
        """
        # region 提取圆环区域
        img = _img.copy()
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.circle(mask, point, r, (255,), 2)
        ROI = cv2.bitwise_and(img, img, mask=mask)
        # 将ROI非零部分取出变成20*20的图片
        polar_img = cv2.warpPolar(ROI, (2 * r, r), point, r, cv2.WARP_FILL_OUTLIERS)
        # 将极坐标图像转换为方形图像
        square_img = cv2.resize(polar_img, (20, 20))
        # endregion

        # 颜色识别
        color, prob = self.color_detector.detect(square_img)

        return color, square_img, ROI

    def right_angle_detect(self, _img):
        """
        直角检测
        ----
        本方法会在传入的图像上画出直线和交点

        :param _img: 传入的图像
        :return: 两直线的角度，交点坐标
        """
        angel1, angel2, cross_point = self.line_detector.find_line(_img, draw=True)
        # TODO:更改返回值
        return angel1, angel2, cross_point

    def read_serial(self, head: str, tail: str):
        """
        读取串口数据
        ----
        :param head: 数据头
        :param tail: 数据尾
        """
        # 清除缓冲区
        self.uart.clear()
        # 读取数据
        data = self.uart.read(head, tail)
        return data

    def write_serial(self, data: str, head: str, tail: str):
        """
        写入串口数据
        ----
        :param data: 数据
        """
        self.uart.write(data, head, tail)
