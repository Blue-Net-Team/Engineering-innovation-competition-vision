"""
解决方案
====
与电控对接的顶层需求，包含了所有的检测和串口通信功能

包含的接口
- 物料运动检测，当物料的位号发生改变，则返回1，否则返回None
- 获取物料位置，返回物料的位号
- 直角检测，返回两直线的角度的均值和交点
"""

import datetime
import json
import math

import cv2
import numpy as np
from colorama import Fore, init, Style
import yaml

import detector
from utils import Uart
import detector
from colorama import Fore, Style, init
import math
from utils import printLog

# 初始化 colorama
init(autoreset=True)

COLOR_DIC = {0: "R", 1: "G", 2: "B"}
COLOR_DIC_INV = {v: k for k, v in COLOR_DIC.items()}
COLOR_DIC_CV = {"R": (0, 0, 255), "G": (0, 255, 0), "B": (255, 0, 0)}


def getTimeStamp():
    """
    获取时间戳(包含毫秒)
    ----
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]

def show(img):
    return cv2.imshow("img", img)

def draw_material(
        point_wh:tuple[int,int,int,int],
        _img:cv2.typing.MatLike,
        color:str|None
):
    """
    画出物料
    ----
    Args:
        point_wh (tuple): 物料的坐标和宽高
        _img (cv2.typing.MatLike): 图片
        color (str): 颜色
    Returns:
        img (cv2.typing.MatLike): 画出物料的图片
    """
    img = _img.copy()
    x,y,w,h = point_wh
    cv2.rectangle(
        img,
        (x - w // 2, y - h // 2),
        (x + w // 2, y + h // 2),
        (0, 255, 0),
        2,
    )
    cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
    if color:
        cv2.putText(
            img,
            color,
            (x+10, y+10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2,
        )
    return img

class Solution:
    def __init__(self, ser_port: str|None, config_path:str):
        """
        解决方案
        ----
        Args:
            ser_port (str): 串口号
            config_path (str): 配置文件路径
        """
        self.annulus_circle_detector = detector.CircleDetector()
        self.traditional_color_detector = detector.TraditionalColorDetector()
        self.line_detector = detector.LineDetector()
        self.uart = Uart(ser_port)
        self.configPath = config_path
        self.position_id_stack:list[dict[str,int|None]] = []     # 用于存放上一帧图像的物料位号的栈

        # 初始化默认参数
        self.area1_points:list[list[int]] = [[0,0],[0,0]]
        self.area2_points:list[list[int]] = [[0,0],[0,0]]
        self.area3_points:list[list[int]] = [[0,0],[0,0]]
        self.target_angel:int = 45
        self.NEED2CUT:int = 40
        # 读取配置文件
        self.load_config()

    def load_config(self):
        """
        读取配置文件
        ----
        """
        try:
            config = {}
            with open(self.configPath, "r") as f:
                if self.configPath.endswith(".json"):
                    config = json.load(f)
                elif self.configPath.endswith(".yaml"):
                    config = yaml.safe_load(f)
                else:
                    printLog(Fore.RED + f"{self.configPath}不是一个合理的配置文件")
            # 判断是否存在对应的参数
            if "area1_points" in config:
                self.area1_points:list[list[int]] = config["area1_points"]
            else:
                printLog(Fore.RED + "配置文件读取位号1参数失败")
            if "area2_points" in config:
                self.area2_points:list[list[int]] = config["area2_points"]
            else:
                printLog(Fore.RED + "配置文件读取位号2参数失败")
            if "area3_points" in config:
                self.area3_points:list[list[int]] = config["area3_points"]
            else:
                printLog(Fore.RED + "配置文件读取位号3参数失败")
            if "target_angel" in config:
                self.target_angel:int = config["target_angel"]
            else:
                printLog(Fore.RED + "配置文件读取目标角度参数失败")
            if "need2cut_height" in config:
                self.NEED2CUT:int = config["need2cut_height"]
            else:
                printLog(Fore.RED + "配置文件读取裁剪高度参数失败")
        except Exception as e:
            printLog(Fore.RED + str(e))

        # 加载圆环识别的圆环参数
        load_err1 = self.annulus_circle_detector.load_config(self.configPath)
        # 加载直线检测的参数
        load_err2 = self.line_detector.load_config(self.configPath)
        # 加载颜色识别的参数
        load_err3 = self.traditional_color_detector.load_config(self.configPath)

        err = [load_err1, load_err2, load_err3]
        if any(err):
            for e in err:
                if e:
                    printLog(Fore.RED + e)


    # region 物料运动检测
    def material_moving_detect(self, _img:cv2.typing.MatLike) -> tuple[str|None, cv2.typing.MatLike]:
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
            res(str|None,Mat): 返回1代表物料运动了，返回None代表物料没有运动,Mat是画出了物料和位号的图片
        """
        res_img = _img.copy()

        color_position_dict:dict[str,tuple[int,int,int,int]] = self.__detect_material_positions(_img)   # type:ignore

        res_img = self.__draw_positions(color_position_dict, res_img)

        # 将坐标转换成位号，在后面排除了now_color_position_id_dict中有None的情况
        now_color_position_id_dict: dict[str, int|None] = self.position2area(color_position_dict)     # type:ignore

        # 上一次的颜色位号
        last_color_position_id_dict: dict[str, int] = (
            self.position_id_stack.pop()
            if self.position_id_stack
            else now_color_position_id_dict
        )  # type:ignore

        # 将now_color_position_id_dict压入栈
        self.position_id_stack.append(now_color_position_id_dict)

        # 如果两个字典不相等，说明物料运动了
        if now_color_position_id_dict != last_color_position_id_dict\
        and (len(set(now_color_position_id_dict.values())) == 3\
            or list(now_color_position_id_dict.values()).count(None) == 2):
            res, res_img = self.get_material(_img)
            return res, res_img
        else:
            return None, res_img

    # endregion

    # region 物料位置检测
    def get_material(self, _img:cv2.typing.MatLike) -> tuple[str|None, cv2.typing.MatLike]:
        """
        获取物料位置，返回字符发送电控
        ----
        Args:
            _img (np.ndarray): 图片
        Returns:
            res (str,cv2.Mat): 物料位置和画出物料和位号的图片

            例如："R1G2B3"代表红色在1号位，绿色在2号位，蓝色在3号位
        """
        res_img = _img.copy()

        color_position_dict:dict[str,tuple[int,int,int,int]|None] = self.__detect_material_positions(_img)

        res_img = self.__draw_positions(color_position_dict, res_img)

        color_position_id_dict = self.position2area(color_position_dict)

        res = "".join(
            [
                f"{area if area else '0'}"
                for color, area in color_position_id_dict.items()
            ]
        )
        res = "C" + res + "E"
        return res, res_img

    def __draw_positions(self, color_position_dict, _img):
        for (color, position), area_point in zip(
                color_position_dict.items(),
                [self.area1_points, self.area2_points, self.area3_points],
        ):
            if position is not None:
                # 画出物料
                _img = draw_material(position, _img, color)
            # 画出位号
            cv2.rectangle(
                _img,
                (area_point[0][0], area_point[0][1]),
                (area_point[1][0], area_point[1][1]),
                (255, 0, 200),
                2,
            )
        return _img

    def __detect_material_positions(self, _img:cv2.typing.MatLike) -> dict[str, tuple[int, int, int, int] | None]:
        """
        物料位置检测(跟踪)
        ----
        本方法不是顶层需求

        Args:
            _img (np.ndarray): 图片
        Returns:
            res_dict (dict): 结果字典，例如：{"R":(x,y,w,h), "G":(x,y,w,h), "B":(x,y,w,h)}
        """
        # 结果字典, 例如：{"R":(x,y,w,h), "G":(x,y,w,h), "B":(x,y,w,h)}
        # 初始化为{"R":None, "G":None, "B":None}
        res_dict: dict[str, None | tuple] = {
            color: None for color in COLOR_DIC.values()
        }

        img = _img.copy()
        img_sharpen = self.annulus_circle_detector.sharpen(img)  # 锐化

        for color in COLOR_DIC.values():
            self.traditional_color_detector.update_threshold(color)
            binarization_img=self.traditional_color_detector.binarization(img_sharpen)
            res = self.traditional_color_detector.get_color_position(binarization_img)
            if res is not None:
                res_dict[color] = res

        return res_dict

    def position2area(self, color_p_dict:dict[str,tuple[int,int,int,int]|None]) -> dict[str,int|None]:
        """
        将坐标字典转换成位号字典
        ----
        **注意：** 本方法不是顶层需求

        Args:
            color_p_dict (dict): 颜色坐标字典, 例如：{"R":(x,y,w,h), "G":(x,y,w,h), "B":(x,y,w,h)}
        Returns:
            dict: 位号字典，例如：{"R":1, "G":2, "B":3}代表红色在1号位，绿色在2号位，蓝色在3号位
        """
        color_area_dict:dict[str,int|None] = {}
        for color in color_p_dict.keys():
            # 如果有物料没识别到，字典中对应的值为None
            point_wh = color_p_dict[color]
            if point_wh is None:
                color_area_dict[color] = None
                continue

            point = point_wh[:2]
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

    # region 直角检测
    def right_angle_detect(self, _img:cv2.typing.MatLike) -> tuple[str|None, cv2.typing.MatLike]:
        """
        直角检测
        ----
        Args:
            _img (cv2.typing.MatLike): 图片
        Returns:
            res (str, cv2.typing.MatLike): 直角的角度和画出直角的图片

        * str的结果会表示为
        'LHXXXxxxyyyE'，
        其中：
        - LE代表包头包尾
        - H是正负标记，0- 1+
        - XXX是角度的十倍，例如： 45.0->450,46.7->467
        - xxx和yyy代表交点的坐标
        """
        res_img = _img.copy()
        angel1, angel2, cross_point_ff, detect_res_img = self.line_detector.get_right_angle(res_img, draw=True)

        if angel1 is None or angel2 is None or cross_point_ff is None:
            return None, detect_res_img
        cross_point = round(cross_point_ff[0][0]), round(cross_point_ff[1][0])

        # 取出大于0的角度
        angel = angel1/10 if 0 < angel1 < 900 else angel2/10

        point2 = (cross_point[0] + 100 * math.cos(math.radians(angel)), cross_point[1] + 100 * math.sin(math.radians(angel)))
        cv2.line(
            detect_res_img,
            (cross_point[0], cross_point[1]),
            (int(point2[0]), int(point2[1])),
            (0, 255, 255),
            2,
        )

        diff_angel = int((angel - self.target_angel)*10)

        res1 = f"L{'0' if diff_angel < 0 else '1'}{str(abs(diff_angel)).rjust(3, '0')}"
        res3 =  f"{str(abs(cross_point[0])).rjust(3, '0')}"\
                f"{str(abs(cross_point[1])).rjust(3, '0')}E"

        str_res = res1 + res3
        return str_res, detect_res_img
    # endregion

    # region 圆环检测
    def annulus_color_detect(
        self, _img: cv2.typing.MatLike
    ) -> tuple[dict[str, tuple[int, int] | None], cv2.typing.MatLike]:
        """
        地面圆环颜色和位置检测
        ----
        本方法不是顶层需求,可以用于测试，本方法会画出圆环和圆心

        Args:
            _img (np.ndarray): 图片
        Returns:
            annulus_dict (dict): 圆环颜色和位置字典，例如：{"R":(x,y), "G":(x,y), "B":(x,y)}
        """
        res_img = _img.copy()
        annulus_dict:dict[str,tuple[int,int]|None] = {}

        # 三个颜色的二值化图
        res_bit_and = np.zeros_like(_img)

        for color in COLOR_DIC.values():
            bit_with_and_img = self.get_with_and_img(_img, color)
            res_bit_and = cv2.bitwise_or(res_bit_and, bit_with_and_img)
            avg_point, avg_r, _ = self.annulus_detect_only(bit_with_and_img)

            if avg_point and avg_r:
                # 画出圆环
                cv2.circle(
                    res_img,
                    (int(avg_point[0]),int(avg_point[1])),
                    int(avg_r),
                    (255, 0, 0),
                    2
                )
                # 画出圆心
                cv2.circle(res_img, (int(avg_point[0]), int(avg_point[1])), 5, (0, 0, 255), 2)
                # 绘制文字，用于显示颜色
                cv2.putText(
                    res_img,
                    color,
                    (int(avg_point[0])+10, int(avg_point[1])+10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )

                annulus_dict[color] = avg_point
            else:
                annulus_dict[color] = None
        # 将res_bit_and和原图拼接
        res_img = np.vstack((res_img, cv2.cvtColor(res_bit_and, cv2.COLOR_GRAY2BGR)))
        return annulus_dict, res_img

    def annulus_color_top(self, _img:cv2.typing.MatLike) -> tuple[str|None,cv2.typing.MatLike]:
        """
        地面圆环颜色和位置检测
        ----
        返回三个圆环的颜色和位置

        本方法会画出圆环和圆心

        - 图片噪声的波动可能会返回none

        Args:
            _img (np.ndarray): 图片
        Returns:
            res (str): 对应颜色的圆环的位置

            `err`的格式为：RXXXYYYGXXXYYYBXXXYYY
            * RGB代表颜色
            * XXX代表x坐标，YYY代表y坐标，如果没检测到这个颜色，则对应返回FFF
        """
        annulus_dict, res_img = self.annulus_color_detect(_img)

        # 结果列表
        errs = [
            (
                [
                    color,
                    [
                        annulus_dict[color][0],     # type:ignore  x轴坐标
                        annulus_dict[color][1],     # type:ignore  y轴坐标
                    ],
                ]
                if annulus_dict[color]
                else [color, ["FFF", "FFF"]]
            )
            for color in annulus_dict
        ]

        # 将结果转换成字符串
        res = "".join(
            [
                f"{color}"\
                f"{str(err[1][0]).rjust(3, '0')}"\
                f"{str(err[1][1]).rjust(3, '0')}"
                for color, err in errs
            ]
        )

        return res, res_img

    def get_with_and_img(self, _img:cv2.typing.MatLike ,color_name:str):
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
        mask = self.traditional_color_detector.binarization(_img)

        # 膨胀
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=6)

        res_img = cv2.bitwise_and(_img, _img, mask=mask)
        return res_img

    def annulus_detect_only(self, _img:cv2.typing.MatLike) -> tuple[tuple[int,int]|None,int|None,cv2.typing.MatLike]:
        """
        圆环检测
        ----
        本方法不是顶层需求

        Args:
            _img (cv2.typing.MatLike): 图片
        Returns:
            res (tuple|None): 圆环的位置和半径以及滤波之后的灰度图
        """
        img = _img.copy()
        points, rs, new_img = self.annulus_circle_detector.detect_circle(img)

        if points is None or rs is None:
            return None, None, new_img

        # 取前5个圆环的坐标平均值
        avg_point = np.mean(points[:5], axis=0)
        avg_point = (int(avg_point[0]), int(avg_point[1]))
        avg_r = int(np.mean(rs[:5]))

        return avg_point, avg_r, new_img

    def annulus_top(self, _img:cv2.typing.MatLike) -> tuple[str|None, cv2.typing.MatLike]:
        """
        圆环检测
        ----
        本方法是顶层需求

        Args:
            _img (cv2.typing.MatLike): 图片
        Returns:
            res (str|None): 圆环的位置和半径

        * str的结果会表示为
        'L0000xxxyyyE'，其中：LE代表包头包尾，xxx和yyy代表圆心的坐标
        """
        img = _img.copy()
        avg_point, avg_r, new_img = self.annulus_detect_only(img)

        canny_img = cv2.Canny(
            new_img,
            self.annulus_circle_detector.param1//2,
            self.annulus_circle_detector.param1
        )

        if avg_point is not None and avg_r is not None:
            # 画出圆环
            cv2.circle(
                new_img,
                avg_point,
                avg_r,
                (255, 0, 0),
                2
            )
            # 画出圆心
            cv2.circle(new_img, avg_point, 2, (255, 255, 0), 2)

        # 拼接canny和原图
        res_img = np.vstack((
            new_img,
            cv2.cvtColor(canny_img, cv2.COLOR_GRAY2BGR)
        ))

        if avg_point is None or avg_r is None:
            return None, res_img

        res =   f"L0000"\
                f"{str(avg_point[0]).rjust(3, '0')}"\
                f"{str(avg_point[1]).rjust(3, '0')}E"

        return res, res_img
    # endregion
