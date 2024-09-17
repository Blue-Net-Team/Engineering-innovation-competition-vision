#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-09-16 17:45:35 +0800
* LastEditTime: 2024-09-16 21:16:19 +0800
* FilePath: \工创2025\detector\LineDetect.py
* details: 直线检测器相关文件

* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""
import cv2
import numpy as np


class LineDetector:
    """
    直线检测
    ----
    * 识别出直线
    * 画出画面中的直线
    * 获取直线角度
    * 获取两条直线的夹角
    """

    # canny边缘检测参数
    Min_val = 0
    Max_val = 255

    # 霍夫直线检测参数
    Hough_threshold = 70
    minLineLength = 50
    maxLineGap = 10

    def sharpen(self, _img: cv2.typing.MatLike):
        """
        锐化图片
        ----
        :param img: 需要锐化的图片
        """
        # 锐化卷积核
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        img = _img.copy()
        img = cv2.filter2D(img, -1, kernel)  # 锐化
        for i in range(3):
            img = cv2.GaussianBlur(img, (3, 3), 0)  # 高斯模糊
        return img

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

    def __callback(self, x):
        self.Min_val = cv2.getTrackbarPos("Min_val", "Trackbar")
        self.Max_val = cv2.getTrackbarPos("Max_val", "Trackbar")
        self.Hough_threshold = cv2.getTrackbarPos("Hough_threshold", "Trackbar")
        self.minLineLength = cv2.getTrackbarPos("minLineLength", "Trackbar")
        self.maxLineGap = cv2.getTrackbarPos("maxLineGap", "Trackbar")

    def __draw_line(self, img: cv2.typing.MatLike, line):
        """
        通过直线参数画出直线
        ----
        :param img: 传入的图像数据
        :param line: 直线参数
        """
        rho, theta = line
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    def find_line(self, _img: cv2.typing.MatLike, draw: bool = False):
        """
        找出直角
        ----
        :param img: 传入的图像数据
        :param draw: 是否在传入的图像中画出直线

        :return: 两个直线的角度，两直线的交点坐标
        """
        img = _img.copy()
        self.sharpen(img)  # 锐化
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转为灰度图
        self.sharpen(img)  # 锐化

        # canny边缘检测
        img = cv2.Canny(img, self.Min_val, self.Max_val)

        # 膨胀
        kernel = np.ones((2, 2), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)

        # 霍夫直线检测
        lines = cv2.HoughLines(
            img,
            1,
            np.pi / 180,
            self.Hough_threshold,
            min_theta=0,
            max_theta=np.pi,
        )

        if draw and lines is not None:
            for i in range(len(lines)):
                for j in range(i + 1, len(lines)):
                    rho1, theta1 = lines[i][0]
                    rho2, theta2 = lines[j][0]
                    angle = abs(theta1 - theta2)
                    if abs(np.pi / 2 - angle) < np.pi / 180:  # 夹角接近90度
                        self.__draw_line(_img, (rho1, theta1))
                        self.__draw_line(_img, (rho2, theta2))

                        angel1 = theta1 * 180 / np.pi
                        angel2 = theta2 * 180 / np.pi
                        
                        # 交点坐标
                        x = (rho1 * np.sin(theta2) - rho2 * np.sin(theta1)) / np.sin(theta2 - theta1)
                        y = (rho1 * np.cos(theta2) - rho2 * np.cos(theta1)) / np.sin(theta1 - theta2)

                        return angel1, angel2, (x, y)
        return None, None, None