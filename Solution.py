#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-09-17 15:03:05 +0800
* LastEditTime: 2024-09-17 16:29:10 +0800
* FilePath: \工创2025\Solution.py
* details: 解决方案，包含了主要需求的解决方案代码

* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""

import cv2
from USART.communicate import Usart
import detector

COLOR_DIC = {0: "R", 1: "G", 2: "B", 3: "W"}


class Solution:
    def __init__(self, pth_path: str = "best_model.pth"):
        self.circle_detector = detector.CircleDetector()
        self.color_detector = detector.ColorDetector(pth_path)
        self.line_detector = detector.LineDetector()
        self.uart = Usart("/dev/ttyTHS1")
        pass

    def material_detect(
        self, _img: cv2.typing.MatLike
    ) -> list[tuple[str, tuple[int, int]]] | None:
        """
        材料检测
        ----
        本方法会在传入的图像上画出圆形区域和颜色识别区

        :param _img: 图片
        :return: 颜色(str)，位置(tuple)列表，如果没识别到园则返回None
        """
        return_lst = []  # 返回值
        img = _img.copy()
        img_sharpen = self.circle_detector.sharpen(img)  # 锐化
        points, rs = self.circle_detector.detect(img_sharpen)  # 检测圆形
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
                return_lst.append((color, point))
            return return_lst

    def annulus_detect(self, _img: cv2.typing.MatLike) -> list[tuple[int, int]] | None:
        """
        圆环检测
        ----
        本方法会在传入的图像上画出圆环和圆心

        :param _img: 传入的图像
        :return: 圆心坐标列表，如果没识别到园则返回None
        """
        points = []
        img = _img.copy()
        img_sharpen = self.circle_detector.sharpen(img)
        points, rs = self.circle_detector.detect(img_sharpen)
        if points is not None and rs is not None:
            for point, r in zip(points, rs):
                cv2.circle(_img, point, r, (0, 255, 0), 1)
                cv2.circle(_img, point, 1, (255, 0, 0), 1)
                points.append(point)
            return points

    def right_angle_detect(self, _img: cv2.typing.MatLike):
        """
        直角检测
        ----
        本方法会在传入的图像上画出直线和交点
        """
        angel1, angel2, cross_point = self.line_detector.find_line(_img, draw=True)
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
