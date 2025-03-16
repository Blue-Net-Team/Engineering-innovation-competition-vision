"""
直线检测模块
====
LineDetector类
----
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
- `find_right_angle(self, _img, draw: bool = False):`
    找出图像中的直角的交线和交点

    参数:
        - `_img (numpy.ndarray)`: 传入的图像数据
        - `draw (bool)`: 是否在传入的图像中画出直线
    返回:
        - `tuple`: 两个直线的角度，两直线的交点坐标

"""

import cv2
import numpy as np

try:
    from Detect import Detect
except ModuleNotFoundError:
    from detector.Detect import Detect

def calculate_cross_point(
        p1:tuple[int, int], p2:tuple[int, int], p3:tuple[int, int], p4:tuple[int, int]
):
    """
    计算两条直线的交点
    ----
    Args:
        p1: 第一条直线的两个端点
        p2: 第一条直线的两个端点
        p3: 第二条直线的两个端点
        p4: 第二条直线的两个端点
    Returns:
        交点坐标
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    A = np.array(
        (
            [-(y4-y3)/(x4-x3), 1],
            [-(y2-y1)/(x2-x1), 1]
        )
    )
    B = np.array(
        (
            [y3-((y4-y3)/(x4-x3))*x3],
            [y1-((y2-y1)/(x2-x1))*x1]
        )
    )

    # 求解矩阵方程 Ax=B
    cross_point = np.linalg.solve(A, B)

    return cross_point

class LineDetector(Detect):
    """
    直线检测
    ----
    * 识别出直线
    * 画出画面中的直线
    * 获取直线角度
    * 获取两条直线的夹角
    """

    # canny边缘检测参数
    Min_val = 120
    Max_val = 255

    # 霍夫直线检测参数
    Hough_threshold = 70  # 霍夫直线检测的阈值，越大检测到的直线越少
    minLineLength = 0  # 霍夫直线检测的最小直线长度
    maxLineGap = 10  # 霍夫直线检测的最大间隔

    bias = 3            # 允许的角度误差
    sigma = 0  # 高斯滤波器的标准差
    odd_index = 3   # 奇数索引

    @property
    def kernel_size(self):
        """kernel_size是第几个奇数"""
        if self.odd_index == 0:
            self.odd_index = 1
        return 2 * self.odd_index - 1

    def createTrackbar(self):
        cv2.namedWindow("Trackbar")
        cv2.createTrackbar("Min_val", "Trackbar", self.Min_val, 255, self.__callback)
        cv2.createTrackbar("Max_val", "Trackbar", self.Max_val, 255, self.__callback)
        cv2.createTrackbar("Hough_threshold", "Trackbar", self.Hough_threshold, 1000, self.__callback)
        cv2.createTrackbar("minLineLength", "Trackbar", self.minLineLength, 600, self.__callback)
        cv2.createTrackbar("maxLineGap", "Trackbar", self.maxLineGap, 600, self.__callback)
        cv2.createTrackbar("bias", "Trackbar", self.bias, 10, self.__callback)
        cv2.createTrackbar("odd_index", "Trackbar", self.odd_index, 20, self.__callback)
        cv2.createTrackbar("sigma", "Trackbar", self.sigma * 10, 100, self.__callback)

    def __callback(self, x):
        self.Min_val = cv2.getTrackbarPos("Min_val", "Trackbar")
        self.Max_val = cv2.getTrackbarPos("Max_val", "Trackbar")
        self.Hough_threshold = cv2.getTrackbarPos("Hough_threshold", "Trackbar")
        self.minLineLength = cv2.getTrackbarPos("minLineLength", "Trackbar")
        self.maxLineGap = cv2.getTrackbarPos("maxLineGap", "Trackbar")
        self.bias = cv2.getTrackbarPos("bias", "Trackbar")
        self.odd_index = cv2.getTrackbarPos("odd_index", "Trackbar")
        self.sigma = cv2.getTrackbarPos("sigma", "Trackbar") / 10

    def draw_line(self, img, line, _color=(0, 0, 255)):
        """
        通过直线参数画出直线
        ----
        Args:
            img: 传入的图像数据
            line: 直线参数
            _color: 画线的颜色
        """
        x1, y1, x2, y2 = line[0]

        cv2.line(img, (x1, y1), (x2, y2), _color, 1)

    def __draw_point(self, img, point):
        """
        画出交点
        ----
        用蓝色的圆圈画出交点

        Args:
            img: 传入的图像数据
            point: 交点坐标
        """
        cv2.circle(img, point, 2, (255, 0, 0), 3)

    def get_right_angle(self, _img, draw: bool = True) -> tuple[None|int, None|int, None|tuple[float, float], cv2.typing.MatLike]:
        """
        找出直角
        ----
        Args:
            _img(Mat): 传入的图像数据
            draw(bool): 是否在图像上画出直线
        Returns:
            tuple:两个直线的角度，两直线的交点坐标
        """
        lines, canny_img = self.find_line(_img)
        res_img = np.vstack([_img, cv2.cvtColor(canny_img, cv2.COLOR_GRAY2BGR)])

        if lines is None:  # 未检测到直线,直接返回
            return None, None, None, res_img

        line_dict = {}
        for line in lines:
            degree: float = round(np.degrees(np.arctan2(line[0][3] - line[0][1], line[0][2] - line[0][0])), 1)
            line_dict[degree] = line[0]

            # 计算目标角度
            _target_degree = degree - 90 if degree > 0 else degree + 90

            # 目标角度误差范围
            target_degree_range = np.arange(
                _target_degree - self.bias, _target_degree + self.bias, 0.1
            )

            for target_degree in target_degree_range:
                if target_degree in line_dict:  # 判断目标角在字典的话
                    target_line = line_dict[target_degree]

                    # 计算交点
                    x1, y1, x2, y2 = line[0]
                    x3, y3, x4, y4 = target_line
                    target_line = [target_line]
                    try:
                        cross_point_ff = calculate_cross_point(
                            (x1, y1), (x2, y2), (x3, y3), (x4, y4)
                        )
                        cross_point_ii = tuple(map(int, cross_point_ff))
                    except ValueError:
                        res_img = np.vstack([_img, cv2.cvtColor(canny_img, cv2.COLOR_GRAY2BGR)])
                        return None, None, None, res_img


                    if draw:  # 画出直线
                        self.draw_line(_img, line)
                        self.draw_line(_img, target_line)
                        self.__draw_point(_img, cross_point_ii)
                    res_img = np.vstack([_img, cv2.cvtColor(canny_img, cv2.COLOR_GRAY2BGR)])

                    return int(degree*10), int(target_degree*10), cross_point_ff, res_img

        return None, None, None, res_img

    def find_line(self, _img:cv2.typing.MatLike) -> tuple[np.ndarray, cv2.typing.MatLike]:
        """
        找出直线
        ----
        Args:
            _img(Mat): 传入的图像数据
        Returns:
            直线参数
        """
        img = _img.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转为灰度图
        img = cv2.medianBlur(img, self.kernel_size)
        img = cv2.GaussianBlur(
            img,
            (self.kernel_size, self.kernel_size),
            self.sigma,
            borderType=cv2.BORDER_REPLICATE
        )

        # canny边缘检测
        canny_img = cv2.Canny(img, self.Min_val, self.Max_val)

        # 霍夫直线检测
        # lines是形状为(n,1,4)的数组
        # n是检测到的直线数量
        # 1是固定值
        # 4是直线的参数，(x1,y1,x2,y2)
        lines = cv2.HoughLinesP(
            canny_img,
            1,
            np.pi / 180,
            self.Hough_threshold,
            minLineLength=self.minLineLength,
            maxLineGap=self.maxLineGap,
        )

        return lines, canny_img

    def get_line_angle(self, line):
        """
        获取直线角度
        ----
        Args:
            line: 直线参数,由find_line得到
        Returns:
            直线角度
        """
        x1, y1, x2, y2 = line
        return int(np.degrees(np.arctan2(y2 - y1, x2 - x1)))


    def save_config(self, path: str):
        """
        保存当前参数到指定路径的 JSON 文件
        ----
        Args:
            path (str): 文件路径
        """
        try:
            config = super().load_config(path)
        except:
            config = {}
        config["LineDetector"] = {
            "Min_val": self.Min_val,
            "Max_val": self.Max_val,
            "Hough_threshold": self.Hough_threshold,
            "minLineLength": self.minLineLength,
            "maxLineGap": self.maxLineGap,
            "bias": self.bias,
            "sigma": self.sigma,
            "odd_index": self.odd_index
        }
        super().save_config(path, config)

    def load_config(self, _config: str|dict):
        """
        从指定路径的 JSON 文件加载参数
        ----
        Args:
            _config (str|dict): 配置信息
        Returns:
            res_str(str): 错误信息
        """
        res_str = ''
        try:
            ori_config = super().load_config(_config)
            config = ori_config["LineDetector"]

            if "Min_val" in config:
                self.Min_val = config["Min_val"]
            else:
                res_str += "配置文件中没有Min_val参数；"
            if "Max_val" in config:
                self.Max_val = config["Max_val"]
            else:
                res_str += "配置文件中没有Max_val参数；"
            if "Hough_threshold" in config:
                self.Hough_threshold = config["Hough_threshold"]
            else:
                res_str += "配置文件中没有Hough_threshold参数；"
            if "minLineLength" in config:
                self.minLineLength = config["minLineLength"]
            else:
                res_str += "配置文件中没有minLineLength参数；"
            if "maxLineGap" in config:
                self.maxLineGap = config["maxLineGap"]
            else:
                res_str += "配置文件中没有maxLineGap参数；"
            if "bias" in config:
                self.bias = config["bias"]
            else:
                res_str += "配置文件中没有bias参数；"
            if "sigma" in config:
                self.sigma = config["sigma"]
            else:
                res_str += "配置文件中没有sigma参数；"
            if "odd_index" in config:
                self.odd_index = config["odd_index"]
            else:
                res_str += "配置文件中没有odd_index参数；"
        except KeyError:
            res_str += f"加载{_config}失败，配置文件没有LineDetector的配置"
            pass
        return res_str
