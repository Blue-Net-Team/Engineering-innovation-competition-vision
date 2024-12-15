"""
解决方案
====
与电控对接的顶层需求，包含了所有的检测和串口通信功能

包含的接口
- 物料运动检测，当物料的位号发生改变，则返回1，否则返回None
- 获取转盘中心, 返回转盘中心的偏差
- 获取物料位置，返回物料的位号
- 圆环检测，返回圆环的颜色和位置
- 直角检测，返回两直线的角度和交点(正在开发)
"""

import json
import cv2
import numpy as np
from USART.communicate import Usart
import detector
from colorama import Fore, Style, init

# 初始化 colorama
init(autoreset=True)

COLOR_DIC = {0: "R", 1: "G", 2: "B"}
COLOR_DIC_INV = {v: k for k, v in COLOR_DIC.items()}


def show(img):
    return cv2.imshow("img", img)


def get_centre_point(
    point1: tuple[int, int], point2: tuple[int, int], point3: tuple[int, int]
):
    """
    获取三点圆的圆心
    ----
    Args:
        point1 (tuple): 第一个点
        point2 (tuple): 第二个点
        point3 (tuple): 第三个点
    Returns:
        tuple: 圆心坐标
    """
    x1, y1 = point1  # A点
    x2, y2 = point2  # B点
    x3, y3 = point3  # C点

    # AB中点
    mid_1 = ((x1 + x2) / 2, (y1 + y2) / 2)
    # BC中点
    mid_2 = ((x2 + x3) / 2, (y2 + y3) / 2)

    # AB中垂线斜率
    _k_AB = (x1 - x2) / (y2 - y1)
    # BC中垂线斜率
    _k_BC = (x3 - x2) / (y2 - y3)

    L = np.array([[_k_AB, -1], [_k_BC, -1]])

    R = np.array([[_k_AB * mid_1[0] - mid_1[1]], [_k_BC * mid_2[0] - mid_2[1]]])

    # 求解方程
    x, y = np.linalg.solve(L, R)
    return int(x), int(y)


class Solution:
    def __init__(self, pth_path: str, ser_port: str):
        """
        解决方案
        ----
        Args:
            pth_path (str): pytorch模型路径
            ser_port (str): 串口号
        """
        self.material_circle_detector = detector.CircleDetector()
        self.annulus_circle_detector = detector.CircleDetector()
        self.color_detector = detector.ColorDetector(pth_path)
        self.traditional_color_detector = detector.TraditionalColorDetector()
        self.line_detector = detector.LineDetector()
        self.polygon_detector = detector.PolygonDetector()
        self.uart = Usart(ser_port)
        self.position_id_stack:list[dict[str,int]] = []     # 用于存放上一帧图像的物料位号的栈

        # region 读取配置文件
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                # 圆环中心点
                self.annulus_point: list[int] = config["annulus_point"]
                # 转盘中心点
                self.rotator_centre_point: list[int] = config["rotator_centre_point"]
                # 多边形边数
                self.nums: int = config["nums"]
                # 位号顶点
                self.area1_points:list[list[int]] = config["area1_points"]
                self.area2_points:list[list[int]] = config["area2_points"]
                self.area3_points:list[list[int]] = config["area3_points"]
        except Exception as e:
            self.annulus_point = [0, 0]
            self.rotator_centre_point = [0, 0]
            self.area1_points:list[list[int]] = [[0,0],[0,0]]
            self.area2_points:list[list[int]] = [[0,0],[0,0]]
            self.area3_points:list[list[int]] = [[0,0],[0,0]]
            self.nums = 0
            print(Fore.RED + "配置文件读取annulus_point,rotator_centre_point,nums失败")

        # 加载物料识别的圆环参数
        load_err1 = self.material_circle_detector.load_config("config.json", "material")
        # 加载圆环识别的圆环参数
        load_err2 = self.annulus_circle_detector.load_config("config.json", "annulus")
        # 加载直线检测的参数
        load_err3 = self.line_detector.load_config("config.json")
        # 加载多边形检测的参数
        load_err4 = self.polygon_detector.load_config("config.json")
        # 加载颜色识别的参数
        load_err5 = self.traditional_color_detector.load_config("config.json")

        err = [load_err1, load_err2, load_err3, load_err4, load_err5]
        if any(err):
            print(Fore.RED + "加载配置文件失败")
            for e in err:
                if e:
                    print(Fore.RED + e)

        # endregion

    # region 物料运动检测
    def material_moving_detect(self, _img):
        """
        物料运动检测
        ----
        - 图像噪声可能会使其返回None
        - 某个位置没有物料会返回None
        - 物料没有运动会返回None

        **注意：** 本方法会修改传入的图像

        可以通过这个函数去调整位号参数

        Args:
            _img (Mat): 图片
        Returns:
            str|none: 1代表运动，none代表没有运动
        """
        color_position_dict:dict[str,tuple[int,int]] = self.detect_material_positions(_img)  # type:ignore

        # 如果有物料没识别到，即color_position_dict有None，返回none
        if None in color_position_dict.values():
            return None

        # 将坐标转换成位号，在后面排除了now_color_position_id_dict中有None的情况
        now_color_position_id_dict: dict[str, int] = self.position2area(color_position_dict)   # type:ignore

        # 如果有某个物料不在规定区域内，认为运动还没停止，返回none
        if None in now_color_position_id_dict.values():
            return None

        # 上一次的颜色位号
        last_color_position_id_dict: dict[str, int] = self.position_id_stack.pop() if self.position_id_stack else now_color_position_id_dict    # type:ignore

        # 将now_color_position_id_dict压入栈
        self.position_id_stack.append(now_color_position_id_dict)

        # 如果两个字典不相等，说明物料运动了
        if now_color_position_id_dict != last_color_position_id_dict:
            return "1"
        else:
            return None

    # endregion

    # region 识别转盘圆心
    def get_rotator_centre(self, _img):
        """
        获取转盘中心
        ----
        - 图片波动可能会返回none
        - 没看到物料可能会返回none

        Args:
            _img (Mat): 图片
        Returns:
            tuple: 转盘中心坐标
        """
        res_dict = self.detect_material_positions(_img)
        # 获取三个颜色的圆心坐标
        R_point, G_point, B_point = res_dict["R"], res_dict["G"], res_dict["B"]

        if R_point is None or G_point is None or B_point is None:
            return None
        # 获取转盘中心
        centre_point = get_centre_point(R_point, G_point, B_point)
        # 画出转盘中心
        cv2.circle(_img, centre_point, 5, (0, 255, 0), 2)

        # 转换为字符，便于发送
        # 01代表正负号，后面的三个数字代表坐标
        err = (
            centre_point[0] - self.rotator_centre_point[0],
            centre_point[1] - self.rotator_centre_point[1],
        )
        res = f"{'0' if err[0] < 0 else '1'}{str(err[0]).rjust(3, '0')}{'0' if err[1] < 0 else '1'}{str(err[1]).rjust(3, '0')}"
        return res
    # endregion

    # region 物料位置检测
    def get_material(self, _img):
        """
        获取物料位置，返回字符发送电控
        ----
        Args:
            _img (np.ndarray): 图片
        Returns:
            str: 物料位置，例如："R1G2B3"代表红色在1号位，绿色在2号位，蓝色在3号位
        """
        color_position_dict = self.detect_material_positions(_img)
        if None in color_position_dict.values():
            return None
        color_position_id_dict = self.position2area(color_position_dict)
        # 如果有物料不在规定区域内，返回None
        if None in color_position_id_dict.values():
            return None
        res = "".join(
            [
                f"{color}{area}"
                for color, area in color_position_id_dict.items()
            ]
        )
        return res

    def detect_material_positions(self, _img) -> dict[str, tuple[int, int] | None]:
        """
        物料位置检测(跟踪)
        ----
        本方法不是顶层需求

        **注意：** 本方法会修改传入的图像

        Args:
            _img (np.ndarray): 图片
        Returns:
            res_dict (dict): 结果字典，例如：{"R":(x,y), "G":(x,y), "B":(x,y)}
        """
        # 结果字典, 例如：{"R":(x,y), "G":(x,y), "B":(x,y)}
        # 初始化为{"R":None, "G":None, "B":None}
        res_dict: dict[str, None | tuple] = {
            color: None for color in COLOR_DIC.values()
        }

        img = _img.copy()
        img_sharpen = self.material_circle_detector.sharpen(img)  # 锐化

        if self.nums == 0:
            # 检测圆形
            points, rs = self.material_circle_detector.detect_circle(img_sharpen)
        else:
            # 检测多边形
            # 轮廓approx被抽象为rs
            points, rs = self.polygon_detector.get_polygon_centre(
                img_sharpen, self.nums
            )

        # 如果检测不到圆形则返回None
        if points is None or rs is None:
            return res_dict

        for point, r in zip(points, rs):
            # 颜色识别区顶点
            pt0 = (int(point[0] - 10), int(point[1] - 10))
            pt1 = (int(point[0] + 10), int(point[1] + 10))

            # 颜色识别区
            ROI_img = img[pt0[1] : pt1[1], pt0[0] : pt1[0]]
            try:
                # 颜色识别
                color, prob = self.color_detector.detect(ROI_img)
            except:
                color, prob = "?", 1.0

            # 绘制颜色识别区
            cv2.rectangle(_img, pt0, pt1, (0, 255, 0), 1)

            if self.nums == 0:  # 圆形物料
                cv2.circle(_img, point, r, (0, 255, 0), 1)
            else:  # 多边形物料
                cv2.polylines(_img, [r], True, (0, 255, 0), 2)

            # 在显示对应的颜色
            cv2.putText(
                _img,
                f"{color}, {prob:.2f}",
                (point[0], point[1] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

            # 将point变成整形
            point = (int(point[0]), int(point[1]))

            res_dict[color] = point
        return res_dict

    def position2area(self, color_p_dict:dict[str,tuple[int,int]]) -> dict[str,int|None]:
        """
        将坐标字典转换成位号字典
        ----
        **注意：** 本方法不是顶层需求

        Args:
            color_p_dict (dict): 颜色坐标字典, 例如：{"R":(x,y), "G":(x,y), "B":(x,y)}
        Returns:
            dict: 位号字典，例如：{"R":1, "G":2, "B":3}代表红色在1号位，绿色在2号位，蓝色在3号位
        """
        color_area_dict:dict[str,int|None] = {}
        for color in color_p_dict.keys():
            point = color_p_dict[color]
            if point is None:
                continue
            if self.area1_points[0][0] <= point[0] <= self.area1_points[1][0] and self.area1_points[0][1] <= point[1] <= self.area1_points[1][1]:
                color_area_dict[color] = 1
            elif self.area2_points[0][0] <= point[0] <= self.area2_points[1][0] and self.area2_points[0][1] <= point[1] <= self.area2_points[1][1]:
                color_area_dict[color] = 2
            elif self.area3_points[0][0] <= point[0] <= self.area3_points[1][0] and self.area3_points[0][1] <= point[1] <= self.area3_points[1][1]:
                color_area_dict[color] = 3
            else:
                color_area_dict[color] = None  # 未知区域
        return color_area_dict
    # endregion

    # region 圆环检测
    def detect_circle_colors(self, _img):
        """
        圆环的颜色检测
        ----
        本方法不是顶层需求

        **注意** 本方法会在传入的图像上画出圆环和圆心

        Args:
            _img (np.ndarray): 图片
        Returns:
            res_dict (dict): 结果字典，例如：{"R":(x,y), "G":(x,y), "B":(x,y)}
        """
        dict1:dict[str,list[tuple[int,int]]] = {color: [] for color in COLOR_DIC.values()}
        res_dict:dict[str,tuple[int,int]] = {}

        img = _img.copy()
        img_sharpen = self.annulus_circle_detector.sharpen(img)
        points, rs = self.annulus_circle_detector.detect_circle(img_sharpen)
        if points is None or rs is None:
            return None

        for point, r in zip(points, rs):
            # 在原图上绘制圆环
            cv2.circle(_img, point, r, (0, 255, 0), 1)
            cv2.circle(_img, point, 1, (255, 0, 0), 1)

            color, _, _ = self.detect_circle_edge_color(_img, point, r)
            dict1[color].append(point)

        # 将结果字典的坐标列表进行平均值计算
        for color in dict1:
            res_dict[color] = (     # type:ignore
                np.mean(dict1[color], axis=0) if dict1[color] else []
            )

        return res_dict

    def annulus_detect(self, _img):
        """
        地面圆环颜色和位置检测
        ----
        本方法会在传入的图像上画出圆环和圆心

        - 图片噪声的波动可能会返回none

        Args:
            _img (np.ndarray): 图片
        Returns:
            err (None|str): 如果检测到圆环则返回None，否则返回颜色和圆心坐标与标准位置的偏差

            `err`的格式为：以颜色字母开头，下一个01表示正负号，后面的数字表示偏差(补全成3位，FFF表示未检测到)
        """
        annulus_dict:dict[str,tuple[int,int]] = {}

        for color in COLOR_DIC.values():
            annulus_img = self.__get_with_and_img(_img, color)
            points, rs = self.annulus_circle_detector.detect_circle(annulus_img)

            # 坐标平均值
            avg_point:tuple[int,int]|None = np.mean(points,axis=0) if points else None
            # 计算平均半径
            avg_r:int|None = int(np.mean(rs)) if rs else None

            if avg_point is None or avg_r is None: return None

            annulus_dict[color] = avg_point

        # 结果列表
        errs = [
            (
                [
                    color,
                    [
                        annulus_dict[color][0] - self.annulus_point[0],
                        annulus_dict[color][1] - self.annulus_point[1],
                    ],
                ]
                if annulus_dict[color]
                else [color, None]
            )
            for color in annulus_dict
        ]

        # 将结果列表转换成字符串，例如：
        # "RFFFFFFFFG00421432B13450002"代表红色未检测到，绿色偏差-42,432，蓝色偏差345,2
        # 以颜色字母开头，下一个01表示正负号，后面的数字表示偏差(补全成3位，FFF表示未检测到)
        res = "".join(
            [
                f"{color}{'0' if err[1][0] < 0 else '1'}{str(err[1][0]).rjust(3, '0')}{'0' if err[1][1] < 0 else '1'}{str(err[1][1]).rjust(3, '0')}"
                for color, err in errs
            ]
        )

        return res

    def detect_circle_edge_color(
        self, _img: cv2.typing.MatLike, point: list[int] | tuple[int, int], r: int
    ):
        """
        识别圆环的颜色
        ----
        *此方法不是顶层需求*

        Args:
            _img (cv2.typing.MatLike): 传入图片
            point (Iterable[int]): 圆心坐标
            r (int): 圆半径
        Returns:
            tuple: 颜色、重构的图片和ROI
        """
        # region 提取圆环区域
        img = _img.copy()
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.circle(mask, point, r, (255,), 2)
        ROI = cv2.bitwise_and(img, img, mask=mask)
        # 将ROI非零部分取出变成20*20的图片
        polar_img = cv2.warpPolar(ROI, (2 * r, r), point, r, cv2.WARP_FILL_OUTLIERS)
        # 将极坐标图像转换为方形图像
        square_img = cv2.resize(polar_img, (20, 20))
        # endregion

        # 颜色识别
        color, prob = self.color_detector.detect(square_img)

        return color, square_img, ROI

    def __get_with_and_img(self, _img:cv2.typing.MatLike ,color_name:str):
        """
        获取按位与的图片
        ----
        Args:
            _img (cv2.typing.MatLike): 图片
            color_name (str): 颜色名称
        Returns:
            res_img (cv2.typing.MatLike): 按位与的图片
        """
        self.traditional_color_detector.update_range(color_name)
        res_img = self.traditional_color_detector.binarization(_img, color_name)
        return res_img
    # endregion

    # region 直角检测
    def right_angle_detect(self, _img):
        """
        直角检测
        ----
        本方法会在传入的图像上画出直线和交点

        :param _img: 传入的图像
        :return: 两直线的角度，交点坐标
        """
        angel1, angel2, cross_point = self.line_detector.find_line(_img, draw=True)
        return angel1, angel2, cross_point
    # endregion

    # region 串口
    def read_serial(self, head: str, tail: str):
        """
        读取串口数据
        ----
        :param head: 数据头
        :param tail: 数据尾
        """
        # 清除缓冲区
        self.uart.clear()
        # 读取数据
        data = self.uart.read(head, tail)
        return data

    def write_serial(self, data: str, head: str, tail: str):
        """
        写入串口数据
        ----
        :param data: 数据
        """
        self.uart.write(data, head, tail)
    # endregion
