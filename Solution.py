"""
解决方案
====
与电控对接的顶层需求，包含了所有的检测和串口通信功能

包含的接口
- 物料运动检测，当物料的位号发生改变，则返回1，否则返回None
- 获取转盘中心, 返回转盘中心的偏差
- 获取物料位置，返回物料的位号
- 圆环检测，返回圆环的颜色和位置
- 圆环检测，返回绿色圆环的位置和红蓝圆环的连线角度
- 直角检测，返回两直线的角度和交点(正在开发)
"""

import json
import cv2
import numpy as np
from USART.communicate import Usart
import detector
from colorama import Fore, Style, init
import math

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
        img (np.ndarray): 图片
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
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2,
        )
    return img

def get_point_distance(point1:tuple[int,int],point2:tuple[int,int]):
    """
    获取两点之间的距离
    ----
    Args:
        point1 (tuple): 第一个点
        point2 (tuple): 第二个点
    Returns:
        res (int): 两点之间的距离
    """
    return int(math.sqrt((point1[0]-point2[0])**2+(point1[1]-point2[1])**2))

class Solution:
    def __init__(self, ser_port: str):
        """
        解决方案
        ----
        Args:
            pth_path (str): pytorch模型路径
            ser_port (str): 串口号
        """
        self.material_circle_detector = detector.CircleDetector()
        self.annulus_circle_detector = detector.CircleDetector()
        self.traditional_color_detector = detector.TraditionalColorDetector()
        self.line_detector = detector.LineDetector()
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

        # 加载圆环识别的圆环参数
        load_err1 = self.annulus_circle_detector.load_config("config.json", "annulus")
        # 加载直线检测的参数
        load_err2 = self.line_detector.load_config("config.json")
        # 加载颜色识别的参数
        load_err3 = self.traditional_color_detector.load_config("config.json")

        err = [load_err1, load_err2, load_err3]
        if any(err):
            print(Fore.RED + "加载配置文件失败")
            for e in err:
                if e:
                    print(Fore.RED + e)

        # endregion

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

        color_position_dict:dict[str,tuple[int,int,int,int]] = self.detect_material_positions(_img)   # type:ignore

        # 如果有物料没识别到，即color_position_dict有None，返回none
        if None in color_position_dict.values():
            return None, res_img

        for (color, position), area_point in zip(
            color_position_dict.items(),
            [self.area1_points, self.area2_points, self.area3_points],
        ):
            # 画出物料
            draw_material(position, res_img, color)
            # 画出位号
            cv2.rectangle(
                res_img,
                (area_point[0][0], area_point[0][1]),
                (area_point[1][0], area_point[1][1]),
                (255, 0, 200),
                2,
            )

        # 将坐标转换成位号，在后面排除了now_color_position_id_dict中有None的情况
        now_color_position_id_dict: dict[str, int|None] = self.position2area(color_position_dict)     # type:ignore

        # 如果有某个物料不在规定区域内，认为运动还没停止，返回none
        if None in now_color_position_id_dict.values():
            return None, res_img

        # 上一次的颜色位号
        last_color_position_id_dict: dict[str, int] = (
            self.position_id_stack.pop()
            if self.position_id_stack
            else now_color_position_id_dict
        )  # type:ignore

        # 将now_color_position_id_dict压入栈
        self.position_id_stack.append(now_color_position_id_dict)

        # 如果两个字典不相等，说明物料运动了
        if now_color_position_id_dict != last_color_position_id_dict:
            return "1", res_img
        else:
            return None, res_img

    # endregion

    # region 识别转盘圆心
    def get_rotator_centre(self, _img:cv2.typing.MatLike) -> tuple[str|None, cv2.typing.MatLike]:
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
        res_img = _img.copy()
        res_dict = self.detect_material_positions(_img)
        # 获取三个颜色的圆心坐标
        R_point, G_point, B_point = res_dict["R"], res_dict["G"], res_dict["B"]

        if R_point is None or G_point is None or B_point is None:
            return None, res_img
        # 获取转盘中心
        centre_point = get_centre_point(
            R_point[:2],
            G_point[:2],
            B_point[:2],
        )
        # 画出转盘中心
        cv2.circle(res_img, centre_point, 5, (0, 255, 0), 2)

        distances = []

        for index, point in enumerate([R_point, G_point, B_point]):
            draw_material(point, res_img, COLOR_DIC[index])
            distances.append(get_point_distance(centre_point, point[:2]))

        avg_distance = int(np.mean(distances))
        cv2.circle(res_img, centre_point, avg_distance, (0, 255, 0), 2)

        # 转换为字符，便于发送
        # 01代表正负号，后面的三个数字代表坐标
        err = (
            centre_point[0] - self.rotator_centre_point[0],
            centre_point[1] - self.rotator_centre_point[1],
        )
        res = f"{'0' if err[0] < 0 else '1'}{str(err[0]).rjust(3, '0')}{'0' if err[1] < 0 else '1'}{str(err[1]).rjust(3, '0')}"
        return res, res_img
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

        color_position_dict:dict[str,tuple[int,int,int,int]] = self.detect_material_positions(_img)
        # 判断是否有物料没识别到，如果有物料没识别到，则返回None
        if None in color_position_dict.values():
            return None, res_img

        for (color, position), area_point in zip(
            color_position_dict.items(),
            [self.area1_points, self.area2_points, self.area3_points],
        ):
            # 画出物料
            draw_material(position, res_img, color)
            # 画出位号
            cv2.rectangle(
                res_img,
                (area_point[0][0], area_point[0][1]),
                (area_point[1][0], area_point[1][1]),
                (255, 0, 200),
                2,
            )

        color_position_id_dict = self.position2area(color_position_dict)
        # 如果有物料不在规定区域内，返回None
        if None in color_position_id_dict.values():
            return None, res_img
        res = "".join(
            [
                f"{color}{area}"
                for color, area in color_position_id_dict.items()
            ]
        )
        return res, res_img


    def detect_material_positions(self, _img:cv2.typing.MatLike) -> dict[str, tuple[int, int, int, int] | None]:
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
        img_sharpen = self.material_circle_detector.sharpen(img)  # 锐化

        for color in COLOR_DIC.values():
            self.traditional_color_detector.update_threshold(color)
            binarization_img=self.traditional_color_detector.binarization(img_sharpen)
            res = self.traditional_color_detector.get_color_position(binarization_img)
            if res is not None:
                res_dict[color] = res

        return res_dict

    def position2area(self, color_p_dict:dict[str,tuple[int,int,int,int]]) -> dict[str,int|None]:
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
            point = color_p_dict[color][:2]
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
    def annulus_detect(self, _img) -> tuple[dict[str, tuple[int, int]] | None, cv2.typing.MatLike]:
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
        annulus_dict:dict[str,tuple[int,int]] = {}

        for color in COLOR_DIC.values():
            bit_with_and_img = self.get_with_and_img(_img, color)
            points, rs = self.annulus_circle_detector.detect_circle(bit_with_and_img)

            # 坐标平均值
            avg_point:tuple[int,int]|None = np.mean(points,axis=0) if points else None
            # 计算平均半径
            avg_r:int|None = int(np.mean(rs)) if rs else None

            if avg_point is None or avg_r is None: return None, res_img

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
        return annulus_dict, res_img

    def annulus_detect_top2(self, _img:cv2.typing.MatLike) -> tuple[str|None,cv2.typing.MatLike]:
        """
        地面圆环颜色和位置检测
        ----
        返回三个圆环的颜色和位置

        本方法会画出圆环和圆心

        - 图片噪声的波动可能会返回none

        Args:
            _img (np.ndarray): 图片
        Returns:
            err (None|str): 如果检测到圆环则返回None，否则返回颜色和圆心坐标与标准位置的偏差

            `err`的格式为：RHXXXYYYGHXXXYYYBHXXXYYY
            * RGB代表颜色
            * H代表正负号，未检测到为F
            * XXX代表x坐标，YYY代表y坐标，如果没检测到这个颜色，则对应返回FFF
        """
        annulus_dict, res_img = self.annulus_detect(_img)

        if annulus_dict is None:
            return None, res_img

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

        return res, res_img

    def annulus_detect_top(self,img:cv2.typing.MatLike) -> tuple[str|None, cv2.typing.MatLike]:
        """
        圆环与直线识别
        ----
        Args:
            img(cv2.typing.MatLike): 图像
        Returns:
            str: 识别结果

        识别结果的格式为:"GHXXXYYYLHAA",其中:
        * G是固定字母,代表绿色圆环
        * H是正负标记位
        * XXX是绿色圆环圆心的x坐标
        * YYY是绿色圆环圆心的y坐标
        * L是固定字母,代表红蓝圆环的连线
        * H是正负标记位
        * AA是红蓝圆环的连线角度

        "G01251056L013"代表绿色圆环位置在(-125,+056)，红蓝圆环的连线角度为13度
        """
        annulus_dict, res_img = self.annulus_detect(img)

        if annulus_dict is None:
            return None, res_img
        R_point, G_point, B_point = annulus_dict["R"], annulus_dict["G"], annulus_dict["B"]

        # 计算红蓝中点
        mid_point = (
            int((R_point[0] + B_point[0]) / 2),
            int((R_point[1] + B_point[1]) / 2),
        )
        # 计算绿色圆环平均坐标
        G_avg_point=(
            int((G_point[0] + mid_point[0]) / 2),
            int((G_point[1] + mid_point[1]) / 2),
        )
        # 计算红蓝圆环连线的角度
        angle = int(math.degrees(math.atan2(B_point[1] - R_point[1], B_point[0] - R_point[0])))

        res=f"G{'0' if G_avg_point[0] <0 else '1'}{abs(G_avg_point[0]):03}{'0' if G_avg_point[1] <0 else '1'}{abs(G_avg_point[1]):03}L{'O' if angle <0 else '1'}{abs(angle):02}"
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
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=6)

        res_img = cv2.bitwise_and(_img, _img, mask=mask)
        return res_img
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
        'AHXXXaHXXXPHxxxHyyy'，
        其中：A和a代表第一个和第二个直线的角度，P代表交点，H代表正负号（0和1），XXX代表角度，
        xxx和yyy代表交点的坐标
        """
        # XXX:第一条线和第二条线是否会发生跳变
        res_img = _img.copy()
        angel1, angel2, cross_point = self.line_detector.get_right_angle(res_img, draw=True)

        if angel1 is None or angel2 is None or cross_point is None:
            return None, res_img

        res1 = f"A{'0' if angel1 < 0 else '1'}{str(abs(angel1)).rjust(3, '0')}"
        res2 = f"a{'0' if angel2 < 0 else '1'}{str(abs(angel2)).rjust(3, '0')}"
        res3 = f"P{'0' if cross_point[0] < 0 else '1'}{str(abs(cross_point[0])).rjust(3, '0')}{'0' if cross_point[1] < 0 else '1'}{str(abs(cross_point[1])).rjust(3, '0')}"

        str_res = res1 + res2 + res3
        return str_res, res_img

    # endregion

    # region 直线识别
    def get_line_angle_top(self, _img:cv2.typing.MatLike) -> tuple[str, cv2.typing.MatLike]:
        """
        获取直线的角度
        ----
        本方法会在传入的图像上画出直线

        Args:
            _img (np.ndarray): 图片
        Returns:
            res (str, cv2.typing.MatLike): 直线的角度和画出直线的图片

        * 角度会补全成3位，此外，还会有一位用来表示正负号，例如：-90度会表示为0090
        """
        res_img = _img.copy()
        lines = self.line_detector.find_line(_img)

        nums = len(lines) if len(lines) < 5 else 5
        angles = []

        for i in range(nums):
            # XXX: 是否是lines[i][0]
            self.line_detector.draw_line(res_img, lines[i][0])
            angle = self.line_detector.get_line_angle(lines[i][0])
            angles.append(angle)
        avg_angle = int(np.mean(angles))

        # 画出平均角度的直线
        height, width = res_img.shape[:2]
        center = (width // 2, height // 2)
        length = min(width, height) // 2
        x1 = int(center[0] + length * np.cos(np.deg2rad(avg_angle)))
        y1 = int(center[1] + length * np.sin(np.deg2rad(avg_angle)))
        x2 = int(center[0] - length * np.cos(np.deg2rad(avg_angle)))
        y2 = int(center[1] - length * np.sin(np.deg2rad(avg_angle)))
        cv2.line(res_img, (x1, y1), (x2, y2), (255, 0, 255), 2)

        # 补成3位，正负号用01表示
        res = f"{'0' if avg_angle < 0 else '1'}{str(abs(avg_angle)).rjust(3, '0')}"
        return res, res_img
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
