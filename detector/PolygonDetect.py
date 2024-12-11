import cv2
import numpy as np

from .Detect import Detect

class PolygonDetector(Detect):
    """
    多边形检测器
    ----
    该类用于检测图像中的多边形，并计算其中心坐标。

    Attributes:
        val_min (int): Canny 边缘检测的低阈值。
        val_max (int): Canny 边缘检测的高阈值。
        epsilon_factor (float): 多边形逼近的精度参数。
        min_area (int): 多边形的最小面积。
        max_area (int): 多边形的最大面积。
    """
    val_min = 50        # Canny边缘检测器的第一个阈值, 低阈值
    val_max = 150       # Canny边缘检测器的第二个阈值, 高阈值
    epsilon_factor = 0.02       # 多边形逼近的精度参数, 该参数越小, 多边形的拟合程度越高
    min_area = 200        # 多边形的面积,小于该面积的多边形将被忽略
    max_area = 500  # 多边形的面积,大于该面积的多边形将被忽略

    def createTrackbar(self):
        cv2.namedWindow("Trackbar")
        cv2.createTrackbar("val_min", "Trackbar", self.val_min, 255, self.__callback)
        cv2.createTrackbar("val_max", "Trackbar", self.val_max, 255, self.__callback)
        cv2.createTrackbar("epsilon_factor", "Trackbar", int(self.epsilon_factor*100), 100, self.__callback)
        cv2.createTrackbar("min_area", "Trackbar", self.min_area, 500, self.__callback)
        cv2.createTrackbar("max_area", "Trackbar", self.max_area, 500, self.__callback)

        cv2.setTrackbarPos("val_min", "Trackbar", self.val_min)
        cv2.setTrackbarPos("val_max", "Trackbar", self.val_max)
        cv2.setTrackbarPos("epsilon_factor", "Trackbar", int(self.epsilon_factor*100))
        cv2.setTrackbarPos("min_area", "Trackbar", self.min_area)
        cv2.setTrackbarPos("max_area", "Trackbar", self.max_area)

    def __callback(self, x):
        self.val_min = cv2.getTrackbarPos("val_min", "Trackbar")
        self.val_max = cv2.getTrackbarPos("val_max", "Trackbar")
        self.epsilon_factor = cv2.getTrackbarPos("epsilon_factor", "Trackbar") / 100
        self.min_area = cv2.getTrackbarPos("min_area", "Trackbar") * 1000
        self.max_area = cv2.getTrackbarPos("max_area", "Trackbar") * 1000

    def get_polygon_centre(self, _img, nums) -> tuple[list[tuple[int,int]],list]:
        """
        获取图像中的多边形的中心坐标
        ----
        **注意：** 本方法会在传入的图像上画出轮廓和多边形的中心

        Args:
            _img (numpy.ndarray): 需要检测的图像
            nums (int): 多边形的边数
        Returns:
            list[tuple[int]]: 多边形的中心坐标列表
        """
        img = _img.copy()

        # 灰度化
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 高斯滤波
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # 边缘检测
        edges = cv2.Canny(blur, self.val_min, self.val_max)

        # 轮廓检测
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 几何中心坐标列表
        centers = []
        approxs = []

        for contour in contours:
            # 近似轮廓
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if len(approx) != nums:
                continue

            # 计算多边形的面积
            area = cv2.contourArea(approx)
            if area > self.max_area or area < self.min_area:
                continue


            # 计算几何中心
            M = cv2.moments(approx)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                centers.append((cX, cY))
                approxs.append(approx)

        return centers, approxs


    def save_config(self, path: str):
        """
        保存配置
        ----
        Args:
            path (str): 配置文件路径
            config (dict): 配置字典
        """
        try:
            config = super().load_config(path)
        except:
            config = {}

        config["polygon"] = {
            "val_min": self.val_min,
            "val_max": self.val_max,
            "epsilon_factor": self.epsilon_factor
        }

        super().save_config(path, config)

    def load_config(self, path: str):
        """
        从指定的 JSON 文件中加载配置
        ----
        Args:
            path (str): 配置文件路径
        """
        try:
            config = super().load_config(path)

            config = config["polygon"]
            self.val_min = config["val_min"]
            self.val_max = config["val_max"]
            self.epsilon_factor = config["epsilon_factor"]
            res_str = ""
        except FileNotFoundError:
            res_str = f"文件 {path} 不存在"
        except KeyError:
            res_str = f"配置文件 {path} 中没有找到对应的配置项"
        return res_str
