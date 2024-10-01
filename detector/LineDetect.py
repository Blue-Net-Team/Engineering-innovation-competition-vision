#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-09-16 17:45:35 +0800
* LastEditTime: 2024-09-25 18:37:11 +0800
* FilePath: \工创2025\detector\LineDetect.py
* details: 直线检测器相关文件

* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""
import cv2
import numpy as np
try:
    from Detect import Detect
except ModuleNotFoundError:
    from detector.Detect import Detect

class LineDetector(Detect):
    """
    直线检测
    ----
    * 识别出直线
    * 画出画面中的直线
    * 获取直线角度
    * 获取两条直线的夹角
    """

    # canny边缘检测参数
    Min_val = 120
    Max_val = 255

    # 霍夫直线检测参数
    Hough_threshold = 70
    minLineLength = 200
    maxLineGap = 10

    bias = 3

    def createTrackbar(self):
        cv2.namedWindow("Trackbar")
        cv2.createTrackbar("Min_val", "Trackbar", self.Min_val, 255, self.__callback)
        cv2.createTrackbar("Max_val", "Trackbar", self.Max_val, 255, self.__callback)
        cv2.createTrackbar(
            "Hough_threshold", "Trackbar", self.Hough_threshold, 1000, self.__callback
        )
        cv2.createTrackbar(
            "minLineLength", "Trackbar", self.minLineLength, 600, self.__callback
        )
        cv2.createTrackbar(
            "maxLineGap", "Trackbar", self.maxLineGap, 600, self.__callback
        )
        cv2.createTrackbar("bias", "Trackbar", self.bias, 10, self.__callback)

    def __callback(self, x):
        self.Min_val = cv2.getTrackbarPos("Min_val", "Trackbar")
        self.Max_val = cv2.getTrackbarPos("Max_val", "Trackbar")
        self.Hough_threshold = cv2.getTrackbarPos("Hough_threshold", "Trackbar")
        self.minLineLength = cv2.getTrackbarPos("minLineLength", "Trackbar")
        self.maxLineGap = cv2.getTrackbarPos("maxLineGap", "Trackbar")
        self.bias = cv2.getTrackbarPos("bias", "Trackbar")

    def __draw_line(self, img, line, _color = (0, 0, 255)):
        """
        通过直线参数画出直线
        ----
        :param img: 传入的图像数据
        :param line: 直线参数
        """
        x1, y1, x2, y2 = line
        
        cv2.line(img, (x1, y1), (x2, y2), _color, 1)

    def __draw_point(self, img, point):
        """
        画出交点
        ----
        :param img: 传入的图像数据
        :param point: 交点坐标
        """
        cv2.circle(img, point, 4, (255, 0, 0), 3)

    def find_line(
        self, _img, draw: bool = False, 
    ):
        """
        找出直角
        ----
        :param img: 传入的图像数据
        :param draw: 是否在传入的图像中画出直线

        :return: 两个直线的角度，两直线的交点坐标
        """
        img = _img.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转为灰度图
        self.sharpen(img)  # 锐化

        # canny边缘检测
        img = cv2.Canny(img, self.Min_val, self.Max_val)

        # 锐化
        img = self.sharpen(img)

        img = cv2.inRange(img, np.array([50]), np.array([255]))

        cv2.imshow("canny", img)

        # 霍夫直线检测
        lines = cv2.HoughLinesP(
            img,
            1,
            np.pi / 180,
            self.Hough_threshold,
            minLineLength=self.minLineLength,
            maxLineGap=self.maxLineGap,
        )

        if lines is None:       # 未检测到直线,直接返回
            return None, None, None

        line_dict = {  # 用角度作为键值，直线作为值
            int(
                np.degrees(np.arctan2(line[0][3] - line[0][1], line[0][2] - line[0][0]))
            ): line[0]
            for line in lines
        }

        for degree in line_dict:
            # 画出直线
            self.__draw_line(_img, line_dict[degree], (0, 255, 0))
            # 计算目标角度
            _target_degree = degree - 90 if degree > 0 else degree + 90
            target_degree_range = range(_target_degree - self.bias, _target_degree + self.bias)

            for target_degree in target_degree_range:
                if target_degree in line_dict:

                    line = line_dict[degree]  # 基准直线
                    target_line = line_dict[target_degree]  # 目标直线

                    # 计算交点
                    x1, y1, x2, y2 = line
                    x3, y3, x4, y4 = target_line
                    try:
                        cross_point = (
                            int(int(
                                (x1 * y2 - y1 * x2) * (x3 - x4)
                                - (x1 - x2) * (x3 * y4 - y3 * x4)
                            )
                            / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))),
                            int(int(
                                (x1 * y2 - y1 * x2) * (y3 - y4)
                                - (y1 - y2) * (x3 * y4 - y3 * x4)
                            )
                            / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)))
                        )
                    except ValueError:
                        return None, None, None

                    if draw:  # 画出直线
                        self.__draw_line(_img, line)
                        self.__draw_line(_img, target_line)
                        # self.__draw_point(_img, cross_point)

                    return degree, target_degree, cross_point
        return None, None, None