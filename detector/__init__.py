"""
识别器模块
=====
提供了一些识别器类，用于识别图像中的各种对象。

CircleDetector类
--------
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
    - `save_config(self, json_path, circle_type)`:
        保存当前配置到指定的 JSON 文件中。

        参数:
            - `json_path (str)`: 配置文件路径。
            - `circle_type (str)`: 圆形类型，包含 "material"（物料圆环）和 "annulus"（地面圆环）。
    - `load_config(self, json_path, circle_type)`:
        从指定的 JSON 文件中加载配置。

        参数:
            - `json_path (str)`: 配置文件路径。
            - `circle_type (str)`: 圆形类型，包含 "material"（物料圆环）和 "annulus"（地面圆环）。

TraditionalColorDetector:
--------
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

LineDetector类
--------
继承自 Detect 类，用于检测图像中的直线，并提供以下功能：

属性:
- `Min_val (int)`: canny 边缘检测的最小阈值
- `Max_val (int)`: canny 边缘检测的最大阈值
- `Hough_threshold (int)`: 霍夫直线检测的阈值
- `minLineLength (int)`: 霍夫直线检测的最小直线长度
- `maxLineGap (int)`: 霍夫直线检测的最大间隔
- `bias (int)`: 角度偏差

方法:
- `createTrackbar(self):`
    创建用于调整参数的滑动条窗口
- `__callback(self, x):`
    滑动条回调函数，用于更新参数值
- `__draw_line(self, img, line, _color=(0, 0, 255)):`
    通过直线参数在图像上画出直线
- `__draw_point(self, img, point):`
    在图像上画出交点
- `find_line(self, _img, draw: bool = False):`
    找出图像中的直线，并计算两条直线的夹角和交点坐标

    参数:
        - `_img (numpy.ndarray)`: 传入的图像数据
        - `draw (bool)`: 是否在传入的图像中画出直线
    返回:
        - `tuple`: 两个直线的角度，两直线的交点坐标
"""

from detector.CircleDetect import CircleDetector
from detector.ColorDetect import *
from detector.LineDetect import LineDetector

__all__ = ["CircleDetector", "TraditionalColorDetector", "LineDetector"]
