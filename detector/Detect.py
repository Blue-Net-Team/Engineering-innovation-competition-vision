"""
Copyright (C) 2025 IVEN-CN(He Yunfeng) and Anan-yy(Weng Kaiyi)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import cv2
import numpy as np

from utils.ConfigLoader import ConfigLoader


class Detect(ConfigLoader):
    """
    检测器基类
    ----
    提供了卷积锐化的方法--sharpen
    """

    @staticmethod
    def sharpen(_img):
        """
        锐化图片
        ----
        :param _img: 需要锐化的图片
        """
        # 锐化卷积核
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        img = _img.copy()
        img = cv2.filter2D(img, -1, kernel)  # 锐化
        for i in range(3):
            img = cv2.GaussianBlur(img, (3, 3), 0)  # 高斯模糊
        return img
