r"""
颜色检测模块
====
该模块包含两个类：ColorDetector 和 TraditionalColorDetector，用于颜色识别。

ColorDetector:
----
使用卷积神经网络 (CNN) 进行颜色识别。

方法:
    - `__init__(model_path: str = "best_model.pth")`:
        初始化 ColorDetector 类，加载预训练的 CNN 模型。
    - `detect(img: np.ndarray) -> tuple[str, float]`:
        识别输入图像的颜色。

        参数:
            - `img`: 输入图像 (numpy 数组)。
        返回:
            - 颜色 (str) 和概率 (float)。

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
import torch
import cv2
from detector.model import CNN
import torch.nn.functional as F

COLOR_DICT: dict[Union[int, float, bool], str] = {
    0:'R',
    1:'G',
    2:'B',
    3:'W'
}

class ColorDetector:
    def __init__(self, model_path="best_model.pth"):
        # 加载模型
        self.cnn = CNN()
        self.cnn.load_state_dict(torch.load(model_path))
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.cnn.to(self.device)
        self.cnn.eval()

    def detect(self, img):
        """
        识别颜色
        ----
        :param img: 图片
        :return: 颜色，概率
        """
        # img = cv2.resize(img, (128, 128))
        img = torch.from_numpy(img).unsqueeze(0).float().to(self.device)

        with torch.no_grad():
            output = self.cnn(img)
            prediction = torch.argmax(output, dim=1)
            probabilities = F.softmax(output, dim=1)

        return COLOR_DICT[prediction.item()], probabilities[0][int(prediction.item())].item()


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

    centre: int = 0
    error: int = 10

    def __init__(self):
        self.update_range()
        pass

    def binarization(self, _img: cv2.typing.MatLike):
        """
        二值化
        ----
        :param img: 图片
        :return: 二值化图片
        """
        img = _img.copy()
        # 高斯滤波
        img = cv2.GaussianBlur(img, (15, 15), 2)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        if self.LOW_H2 is None:
            low = np.array([self.LOW_H1, 5, 10])
            up = np.array([self.UP_H1, 255, 250])
            mask = cv2.inRange(hsv, low, up)
        else:
            low1 = np.array([self.LOW_H1, 5, 5])
            up1 = np.array([self.UP_H1, 255, 250])

            low2 = np.array([self.LOW_H2, 5, 5])
            up2 = np.array([self.UP_H2, 255, 250])

            mask1 = cv2.inRange(hsv, low1, up1)
            mask2 = cv2.inRange(hsv, low2, up2)
            mask = cv2.bitwise_or(mask1, mask2)

        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        return mask

    def createTrackbar(self):
        """
        创建调节条
        ----
        """
        cv2.namedWindow("Trackbar")
        cv2.createTrackbar("Centre", "Trackbar", self.centre, 180, self.__callback)
        cv2.createTrackbar("Error", "Trackbar", self.error, 40, self.__callback)
        cv2.createTrackbar("save", "Trackbar", 0, 1, self.__save)


    def __callback(self, x):
        self.centre = cv2.getTrackbarPos("Centre", "Trackbar")
        self.error = cv2.getTrackbarPos("Error", "Trackbar")

        self.update_range()

    def __save(self, x):
        if x == 1:
            self.save_params("./color params.json")
        else:
            pass
        
    def update_range(self):
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

    def save_params(self, path):
        """
        保存参数
        ----
        :param path: 路径
        """
        with open(path, "w") as f:
            json.dump({"color":{"centre": self.centre, "error": self.error}}, f)

    def load_param(self, path):
        """
        加载参数
        ----
        :param path: 路径
        """
        with open(path, "r") as f:
            data = json.load(f)
            data = data["color"]
            self.centre = data["centre"]
            self.error = data["error"]