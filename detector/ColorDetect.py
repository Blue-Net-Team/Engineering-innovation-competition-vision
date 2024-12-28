r"""
颜色检测模块
====
该模块包含两个类：TraditionalColorDetector，用于颜色识别。

TraditionalColorDetector:
---
使用传统的颜色识别方法，通过中央色相阈值和色相容差来识别颜色。

方法:
    - `__init__()`:
        初始化 TraditionalColorDetector 类，更新色相范围。
    - `binarization(_img: cv2.typing.MatLike) -> np.ndarray`:
        对输入图像进行二值化处理。

        参数:
            - `_img`: 输入图像 (cv2.typing.MatLike)。
        返回:
            - 二值化后的图像 (numpy 数组)。
    - `createTrackbar()`:
        创建调节条，用于调整色相中心和误差。
    - `__callback(x: int)`:
        调节条回调函数，更新色相范围。
    - `__save(x: int)`:
        保存参数回调函数，将当前参数保存到文件。
    - `update_range()`:
        更新色相范围，根据中心色相和误差计算上下限。
    - `save_params(path: str)`:
        保存当前参数到指定路径的 JSON 文件。

        参数:
            - `path`: 文件路径 (str)。
    - `load_param(path: str)`:
        从指定路径的 JSON 文件加载参数。

        参数:
            - `path`: 文件路径 (str)。
"""

import json
from typing import Union
import numpy as np
import cv2

COLOR_DICT: dict[Union[int, float, bool], str] = {
    0:'R',
    1:'G',
    2:'B',
}

class TraditionalColorDetector:
    """
    传统颜色识别
    ----
    使用中央色相阈值和色相容差来识别颜色
    """

    LOW_H1: int
    UP_H1: int

    LOW_H2: int | None
    UP_H2: int | None

    centre: int = 65
    error: int = 10

    L_S: int = 55
    U_S: int = 255
    L_V: int = 0
    U_V: int = 255

    min_material_area: int = 1000
    max_material_area: int = 10000

    color_index: int = 0

    color = COLOR_DICT[color_index]

    color_threshold = {
        "R":{
            "centre": 0,
            "error": 10,
            "L_S": 55,
            "U_S": 255,
            "L_V": 0,
            "U_V": 255,
        },
        "G":{
            "centre": 65,
            "error": 10,
            "L_S": 55,
            "U_S": 255,
            "L_V": 0,
            "U_V": 255,
        },
        "B":{
            "centre": 130,
            "error": 10,
            "L_S": 55,
            "U_S": 255,
            "L_V": 0,
            "U_V": 255,
        },
    }

    def __init__(self):
        color_threshold0 = self.color_threshold["R"]
        self.update_threshold(color_threshold0)

    def update_threshold(self,_color_threshold: dict[str, int]):
        """
        更新阈值
        ----
        Args:
            _color_threshold(dict[str, int]): 颜色阈值字典
        """
        # 初始化色相范围
        self.centre = _color_threshold["centre"]
        self.error = _color_threshold["error"]
        self.L_S = _color_threshold["L_S"]
        self.U_S = _color_threshold["U_S"]
        self.L_V = _color_threshold["L_V"]
        self.U_V = _color_threshold["U_V"]

    def binarization(self, _img: cv2.typing.MatLike) -> cv2.typing.MatLike:
        """
        二值化
        ----
        Args:
            _img(cv2.typing.MatLike): 输入图像
        Returns:
            cv2.typing.MatLike: 二值化后的图像
        """
        img = _img.copy()
        # 高斯滤波
        img = cv2.GaussianBlur(img, (15, 15), 2)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        if self.LOW_H2 is None:
            low = np.array([self.LOW_H1, self.L_S, self.L_V])
            up = np.array([self.UP_H1, self.U_S, self.U_V])
            mask = cv2.inRange(hsv, low, up)
        else:
            low1 = np.array([self.LOW_H1, self.L_S, self.L_V])
            up1 = np.array([self.UP_H1, self.U_S, self.U_V])

            low2 = np.array([self.LOW_H2, self.L_S, self.L_V])
            up2 = np.array([self.UP_H2, self.U_S, self.U_V])

            mask1 = cv2.inRange(hsv, low1, up1)
            mask2 = cv2.inRange(hsv, low2, up2)
            mask = cv2.bitwise_or(mask1, mask2)

        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        return mask

    def get_color_position(self, binarized_img:cv2.typing.MatLike) -> tuple[int, int]:
        """
        获取颜色位置
        ----
        通过传入二值化的图像，然后取外接矩形的中心点作为颜色的位置

        Args:
            binarized_img(cv2.typing.MatLike): 二值化图像
        Returns:
            tuple[int, int]: 颜色位置
        """
        contours,_=cv2.findContours(binarized_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # 获取最大的轮廓
            largest_contour=max(contours,key=cv2.contourArea)
            # 获取外接矩形
            x,y,w,h=cv2.boundingRect(largest_contour)
            #计算矩形中心点
            center_x=x+w//2
            center_y=y+h//2

            return(center_x,center_y)
        else:
            return (-1,-1)

    def createTrackbar(self):
        """
        创建调节条
        ----
        """
        cv2.namedWindow("Trackbar")
        cv2.createTrackbar("Centre", "Trackbar", self.centre, 180, self.__callback)
        cv2.createTrackbar("Error", "Trackbar", self.error, 40, self.__callback)
        cv2.createTrackbar("L_S", "Trackbar", self.L_S, 255, self.__callback)
        cv2.createTrackbar("U_S", "Trackbar", self.U_S, 255, self.__callback)
        cv2.createTrackbar("L_V", "Trackbar", self.L_V, 255, self.__callback)
        cv2.createTrackbar("U_V", "Trackbar", self.U_V, 255, self.__callback)
        cv2.createTrackbar("color", "Trackbar", 0, 2, self._color_callback)
        cv2.createTrackbar("min_area", "Trackbar", self.min_material_area, 10000, self.__callback)
        cv2.createTrackbar("max_area", "Trackbar", self.max_material_area, 10000, self.__callback)

    def __callback(self, x):
        self.centre = cv2.getTrackbarPos("Centre", "Trackbar")
        self.error = cv2.getTrackbarPos("Error", "Trackbar")
        self.L_S = cv2.getTrackbarPos("L_S", "Trackbar")
        self.U_S = cv2.getTrackbarPos("U_S", "Trackbar")
        self.L_V = cv2.getTrackbarPos("L_V", "Trackbar")
        self.U_V = cv2.getTrackbarPos("U_V", "Trackbar")
        self.min_material_area = cv2.getTrackbarPos("min_area", "Trackbar")
        self.max_material_area = cv2.getTrackbarPos("max_area", "Trackbar")

        self.color_threshold[self.color] = {
            "centre": self.centre,
            "error": self.error,
            "L_S": self.L_S,
            "U_S": self.U_S,
            "L_V": self.L_V,
            "U_V": self.U_V,
        }

        self.update_range(self.color)

    def _color_callback(self, x):
        self.color_index = cv2.getTrackbarPos("color", "Trackbar")

        self.color = COLOR_DICT[self.color_index]

        self.update_range(self.color)

    def update_range(self, color_name: str = "R"):
        self.centre = self.color_threshold[color_name]["centre"]
        self.error = self.color_threshold[color_name]["error"]

        minH = self.centre - self.error
        maxH = self.centre + self.error

        if minH < 0:
            self.LOW_H2 = 180 + minH
            self.UP_H2 = 180

            self.LOW_H1 = 0
            self.UP_H1 = maxH
        elif maxH > 180:
            self.LOW_H2 = 0
            self.UP_H2 = maxH - 180

            self.LOW_H1 = minH
            self.UP_H1 = 180
        else:
            self.LOW_H1 = minH
            self.UP_H1 = maxH

            self.LOW_H2 = None
            self.UP_H2 = None

        self.color_threshold[self.color] = {
            "centre": self.centre,
            "error": self.error,
            "L_S": self.L_S,
            "U_S": self.U_S,
            "L_V": self.L_V,
            "U_V": self.U_V,
        }

        # 更新滑块位置
        cv2.setTrackbarPos("Centre", "Trackbar", self.centre)
        cv2.setTrackbarPos("Error", "Trackbar", self.error)
        cv2.setTrackbarPos("L_S", "Trackbar", self.L_S)
        cv2.setTrackbarPos("U_S", "Trackbar", self.U_S)
        cv2.setTrackbarPos("L_V", "Trackbar", self.L_V)
        cv2.setTrackbarPos("U_V", "Trackbar", self.U_V)
        cv2.setTrackbarPos("color", "Trackbar", self.color_index)
        cv2.setTrackbarPos("min_area", "Trackbar", self.min_material_area)
        cv2.setTrackbarPos("max_area", "Trackbar", self.max_material_area)


    def save_params(self, path):
        """
        保存参数
        ----
        :param path: 路径
        """
        with open(path, "r") as f:
            config = json.load(f)

        config["color"] = self.color_threshold
        config["min_material_area"] = self.min_material_area
        config["max_material_area"] = self.max_material_area

        with open(path, "w") as f:
            json.dump(config, f, indent=4)

    def load_config(self, path):
        """
        加载参数
        ----
        :param path: 路径
        """
        try:
            with open(path, "r") as f:
                config = json.load(f)
                self.color_threshold = config["color"]
                self.min_material_area = config["min_material_area"]
                self.max_material_area = config["max_material_area"]
            self.update_threshold(self.color_threshold[self.color])
            res_str = ""
        except FileNotFoundError:
            res_str = f"文件 {path} 不存在"
        except KeyError:
            res_str = f"配置文件 {path} 中没有找到对应的配置项"
        return res_str

