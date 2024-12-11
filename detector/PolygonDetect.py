import cv2
import numpy as np

from .Detect import Detect

class PolygonDetector(Detect):
    val_min = 50        # Canny边缘检测器的第一个阈值, 低阈值
    val_max = 150       # Canny边缘检测器的第二个阈值, 高阈值
    epsilon_factor = 0.02       # 多边形逼近的精度参数, 该参数越小, 多边形的拟合程度越高

    def createTrackbar(self):
        cv2.namedWindow("Trackbar")
        cv2.createTrackbar("val_min", "Trackbar", self.val_min, 255, self.__callback)
        cv2.createTrackbar("val_max", "Trackbar", self.val_max, 255, self.__callback)
        cv2.createTrackbar("epsilon_factor", "Trackbar", int(self.epsilon_factor*100), 100, self.__callback)

        cv2.setTrackbarPos("val_min", "Trackbar", self.val_min)
        cv2.setTrackbarPos("val_max", "Trackbar", self.val_max)
        cv2.setTrackbarPos("epsilon_factor", "Trackbar", int(self.epsilon_factor*100))

    def __callback(self, x):
        self.val_min = cv2.getTrackbarPos("val_min", "Trackbar")
        self.val_max = cv2.getTrackbarPos("val_max", "Trackbar")
        self.epsilon_factor = cv2.getTrackbarPos("epsilon_factor", "Trackbar") / 100

    def get_polygon_centre(self, _img, nums) -> list[tuple[int]]:
        """
        获取图像中的多边形的中心坐标
        ----
        Args:
            _img (numpy.ndarray): 需要检测的图像
            nums (int): 多边形的边数
        Returns:
            list[tuple[int]]: 多边形的中心坐标列表
        """
        img = _img.copy()
        # 将图像转换为灰度图像
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 使用Canny边缘检测器检测边缘
        edges = cv2.Canny(gray, self.val_min, self.val_max)
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        centers = []

        # 对每个轮廓进行多边形拟合
        for contour in contours:
            epsilon = self.epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if len(approx) == nums:
                # 计算几何中心
                M = cv2.moments(approx)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    centers.append((cx, cy))

        return centers

    def save_config(self, path: str, config: dict):
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
