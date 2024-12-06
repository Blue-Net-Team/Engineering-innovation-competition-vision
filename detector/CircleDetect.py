#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-09-16 18:10:09 +0800
* LastEditTime: 2024-09-17 13:18:17 +0800
* FilePath: \工创2025\detector\CircleDetect.py
* details: 使用霍夫圆检测算法检测圆形，得到圆心

* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""

import json
import cv2
from .Detect import Detect


class CircleDetector(Detect):
    """
    圆形识别器
    ----
    * 识别出圆形，获取圆心坐标
    """

    # 霍夫圆环参数
    dp = 1  # 累加器分辨率与图像分辨率的反比，值越大，检测时间越短，但是可能会丢失一些小圆
    minDist = 20  # 圆心之间的最小距离
    param1 = 60  # Canny边缘检测的高阈值
    param2 = 20  # 累加器的阈值，值越小，检测到的圆越多
    minRadius = 35  # 圆的最小半径
    maxRadius = 45  # 圆的最大半径

    def createTrackbar(self):
        cv2.namedWindow("Trackbar")
        cv2.createTrackbar("dp", "Trackbar", self.dp, 10, self.__callback)
        cv2.createTrackbar("minDist", "Trackbar", self.minDist, 100, self.__callback)
        cv2.createTrackbar("param1", "Trackbar", self.param1, 100, self.__callback)
        cv2.createTrackbar("param2", "Trackbar", self.param2, 100, self.__callback)
        cv2.createTrackbar("minRadius", "Trackbar", self.minRadius, 100, self.__callback)
        cv2.createTrackbar("maxRadius", "Trackbar", self.maxRadius, 100, self.__callback)

        cv2.setTrackbarPos("dp", "Trackbar", self.dp)
        cv2.setTrackbarPos("minDist", "Trackbar", self.minDist)
        cv2.setTrackbarPos("param1", "Trackbar", self.param1)
        cv2.setTrackbarPos("param2", "Trackbar", self.param2)
        cv2.setTrackbarPos("minRadius", "Trackbar", self.minRadius)
        cv2.setTrackbarPos("maxRadius", "Trackbar", self.maxRadius)

    def __callback(self, x):
        self.dp = cv2.getTrackbarPos("dp", "Trackbar")
        self.minDist = cv2.getTrackbarPos("minDist", "Trackbar")
        self.param1 = cv2.getTrackbarPos("param1", "Trackbar")
        self.param2 = cv2.getTrackbarPos("param2", "Trackbar")
        self.minRadius = cv2.getTrackbarPos("minRadius", "Trackbar")
        self.maxRadius = cv2.getTrackbarPos("maxRadius", "Trackbar")

    def detect(self, _img):
        """
        检测圆形
        ----
        :param img: 需要检测的图片
        :return: 圆心坐标列表, 半径列表
        """
        point_lst = []
        r_lst = []
        img = _img.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(img, self.param1, self.param1 / 2)
        circles = cv2.HoughCircles(
            img,
            cv2.HOUGH_GRADIENT,
            dp=self.dp,
            minDist=self.minDist,
            param1=self.param1,
            param2=self.param2,
            minRadius=self.minRadius,
            maxRadius=self.maxRadius,
        )
        if circles is not None:
            circles = circles[0]
            for circle in circles:
                x, y, r = circle
                point_lst.append((int(x), int(y)))
                r_lst.append(int(r))
            return point_lst, r_lst
        return None, None

    def save_config(self, jsion_path, circle_type):
        """
        保存配置
        ----
        Args:
            jsion_path (str): 配置文件路径
            circle_type (str): 圆形类型,包含"material"(物料圆环)、"annulus"(地面圆环)
        """
        if circle_type not in ["material", "annulus"]:
            raise ValueError("circle_type must be 'material' or 'annulus'")
        
        config = {
            circle_type: {
                "dp": self.dp,
                "minDist": self.minDist,
                "param1": self.param1,
                "param2": self.param2,
                "minRadius": self.minRadius,
                "maxRadius": self.maxRadius,
            }
        }
        with open(jsion_path, "w") as f:
            json.dump(config, f)
            
    def load_config(self, jsion_path, circle_type):
        """
        加载配置
        ----
        Args:
            jsion_path (str): 配置文件路径
            circle_type (str): 圆形类型,包含"material"(物料圆环)、"annulus"(地面圆环)
        """
        if circle_type not in ["material", "annulus"]:
            raise ValueError("circle_type must be 'material' or 'annulus'")
        
        with open(jsion_path, "r") as f:
            config = json.load(f)
        config = config[circle_type]
        
        self.dp = config["dp"]
        self.minDist = config["minDist"]
        self.param1 = config["param1"]
        self.param2 = config["param2"]
        self.minRadius = config["minRadius"]
        self.maxRadius = config["maxRadius"]

