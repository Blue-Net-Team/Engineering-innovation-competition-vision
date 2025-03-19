import cv2
import numpy as np

from utils.ConfigLoader import ConfigLoader


class Detect(ConfigLoader):
    """
    检测器基类
    ----
    提供了卷积锐化的方法--sharpen
    """

    def sharpen(self, _img):
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
