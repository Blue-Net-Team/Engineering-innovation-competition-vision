"""
圆形检测器模块
====
提供了一个用于检测图像中圆形的识别器。

CircleDetector类
----
继承自 `Detect` 类，实现了圆形检测的功能。

方法:
    - `createTrackbar(self)`:
        创建用于调整霍夫圆环参数的滑动条窗口。
    - `__callback(self, x)`:
        滑动条回调函数，用于更新霍夫圆环参数。
    - `detect(self, _img)`:
        检测图像中的圆形。

        参数:
            - `_img (numpy.ndarray)`: 需要检测的图像。
        返回:
            `tuple`: 圆心坐标列表和半径列表，如果没有检测到圆形则返回 (None, None)。
    - `save_config(self, jsion_path, circle_type)`:
        保存当前配置到指定的 JSON 文件中。

        参数:
            - `jsion_path (str)`: 配置文件路径。
            - `circle_type (str)`: 圆形类型，包含 "material"（物料圆环）和 "annulus"（地面圆环）。
    - `load_config(self, jsion_path, circle_type)`:
        从指定的 JSON 文件中加载配置。

        参数:
            - `jsion_path (str)`: 配置文件路径。
            - `circle_type (str)`: 圆形类型，包含 "material"（物料圆环）和 "annulus"（地面圆环）。

"""

import json
import cv2
import numpy as np
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
    sigma:float = 0  # 高斯滤波器的标准差
    odd_index = 3   # 奇数索引

    @property
    def kernel_size(self):
        """kernel_size是第几个奇数"""
        return 2 * self.odd_index - 1

    def __callback(self, x):
        try:
            self.dp = cv2.getTrackbarPos("dp", "Trackbar")
            self.minDist = cv2.getTrackbarPos("minDist", "Trackbar")
            self.param1 = cv2.getTrackbarPos("param1", "Trackbar")
            self.param2 = cv2.getTrackbarPos("param2", "Trackbar")
            self.minRadius = cv2.getTrackbarPos("minRadius", "Trackbar")
            self.maxRadius = cv2.getTrackbarPos("maxRadius", "Trackbar")
            self.odd_index = cv2.getTrackbarPos("odd_index", "Trackbar")
            self.sigma = cv2.getTrackbarPos("sigma", "Trackbar") / 10
        except:
            pass

    def createTrackbar(self):
        cv2.namedWindow("Trackbar")
        cv2.createTrackbar("dp", "Trackbar", self.dp, 10, self.__callback)
        cv2.createTrackbar("minDist", "Trackbar", self.minDist, 100, self.__callback)
        cv2.createTrackbar("param1", "Trackbar", self.param1, 255, self.__callback)
        cv2.createTrackbar("param2", "Trackbar", self.param2, 100, self.__callback)
        cv2.createTrackbar("minRadius", "Trackbar", self.minRadius, 100, self.__callback)
        cv2.createTrackbar("maxRadius", "Trackbar", self.maxRadius, 100, self.__callback)
        cv2.createTrackbar("odd_index", "Trackbar", self.odd_index, 20, self.__callback)
        cv2.createTrackbar("sigma", "Trackbar", int(self.sigma * 10), 100, self.__callback)

        cv2.setTrackbarPos("dp", "Trackbar", self.dp)
        cv2.setTrackbarPos("minDist", "Trackbar", self.minDist)
        cv2.setTrackbarPos("param1", "Trackbar", self.param1)
        cv2.setTrackbarPos("param2", "Trackbar", self.param2)
        cv2.setTrackbarPos("minRadius", "Trackbar", self.minRadius)
        cv2.setTrackbarPos("maxRadius", "Trackbar", self.maxRadius)
        cv2.setTrackbarPos("odd_index", "Trackbar", self.odd_index)
        cv2.setTrackbarPos("sigma", "Trackbar", int(self.sigma * 10))

    def detect_circle(self, _img) -> tuple[list[tuple[int,int]]|None,list[int]|None, cv2.typing.MatLike]:
        """
        检测圆形
        ----
        :param img: 需要检测的图片
        :return: 圆心坐标列表, 半径列表，没识别到圆环返回none，以及经过滤波的灰度
        """
        point_lst = []
        r_lst = []
        img = _img.copy()
        # 滤波
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, self.kernel_size)
        img = cv2.GaussianBlur(
            img,
            (self.kernel_size, self.kernel_size),
            self.sigma,
            borderType=cv2.BORDER_REPLICATE
        )

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

        # 将原始图像和滤波后的图像拼接在一起
        res_img = np.vstack([
            _img,
            cv2.cvtColor(img, cv2.COLOR_GRAY2BGR),
        ])

        if circles is not None:
            circles = circles[0]
            for circle in circles:
                x, y, r = circle
                point_lst.append((int(x), int(y)))
                r_lst.append(int(r))
            return point_lst, r_lst, res_img
        return None, None, res_img

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

        try:
            config = super().load_config(jsion_path)
        except:
            config = {}

        config[circle_type] = {
            "dp": self.dp,
            "minDist": self.minDist,
            "param1": self.param1,
            "param2": self.param2,
            "minRadius": self.minRadius,
            "maxRadius": self.maxRadius,
            "sigma": self.sigma,
            "odd_index": self.odd_index
        }

        super().save_config(jsion_path, config)

    def load_config(self, _config:str|dict):
        """
        加载配置
        ----
        Args:
            _config (str|dict): 配置文件路径
        """
        res_str = ""
        circle_type = "annulus"

        config = {}
        try:
            config = super().load_config(_config)
            config = config[circle_type]

        except KeyError:
            res_str += f"配置文件{_config}中没有{circle_type}的配置"
            pass

        res_str += super().load_param(config, "dp")
        res_str += super().load_param(config, "minDist")
        res_str += super().load_param(config, "param1")
        res_str += super().load_param(config, "param2")
        res_str += super().load_param(config, "minRadius")
        res_str += super().load_param(config, "maxRadius")
        res_str += super().load_param(config, "sigma")
        res_str += super().load_param(config, "odd_index")

        return res_str
