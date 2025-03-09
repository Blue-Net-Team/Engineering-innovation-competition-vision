"""
测试文件
====
用于测试solution和各个识别器功能是否正常

Test_solution
----
继承自Solution类，用于测试解决方案的功能

方法:
    - `__init__(self, pth_path: str, ser_port: str):`初始化方法，设置模型路径和串口号
    - `test_func(self, cap_id: int, func_name: str):`测试Solution功能，显示FPS
    - `test_usart_read(self, head: str, tail: str):`测试读取串口
    - `test_usart_write(self, data: str, head: str, tail: str):`测试写入串口

Test_Line_detect
----
测试直线检测器的效果

方法:
    - `__init__(self):` 初始化方法
    - `test(self):` 测试方法，显示检测结果
"""

import time
from datetime import datetime

import cv2
import numpy as np
from colorama import Fore, Style, init

from Solution import Solution
from utils import SendImg, ReceiveImg, Cap

init(autoreset=True)

COLOR_DIC = {0: "R", 1: "G", 2: "B"}


class Test_solution(Solution):
    def __init__(self, ser_port: str|None=None, sender: SendImg | None=None) -> None:
        """
        解决方案
        ----
        Args:
            pth_path (str): pytorch模型路径
            ser_port (str): 串口号
        """
        super().__init__(ser_port)
        # 顶层方法字典
        self.TOP_FUNC_DICT = {
            "1": self.annulus_top,  # 圆环检测
            "2": self.right_angle_detect,  # 直角检测
            "3": self.material_moving_detect,  # 物料运动检测
            "4": self.get_material,  # 获取物料位号
        }

        if sender is not None:
            self.sender = sender
            while True:
                if self.sender.connecting():
                    break
            self.sender.start()
        else:
            self.sender = None

    def test_func(self, cap:Cap|ReceiveImg, sign: str):
        """
        测试Solution顶层功能
        ----
        * "2": 直角检测
        * "3": 物料运动检测
        * "4": 获取物料位号

        Args:
            cap_id (int): 摄像头编号
            sign (str): 串口信号(功能编号)
        Returns:
            None
        """
        # cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        while True:
            _,img = cap.read()
            if img is None:
                continue

            img = img[:400,:]

            t0 = time.perf_counter()
            res, res_img = self.TOP_FUNC_DICT[sign](img)
            t1 = time.perf_counter()

            detect_time = t1 - t0

            if self.sender is not None:
                self.sender.send(res_img)
            # else:
                # cv2.imshow("img", res_img)

            if res:
                time_show = detect_time * 1000

                if time_show <= 30:
                    color = Fore.GREEN
                elif time_show <= 50:
                    color = Fore.YELLOW
                else:
                    color = Fore.RED

                now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                if res[0] == "L":
                    print(
                        Fore.YELLOW + f"[{now_time}]" + Style.RESET_ALL,
                        "res:",
                        Fore.MAGENTA + f"{'+'if res[1]=='1' else '-'}{res[2:4]}.{res[4]}" + Style.RESET_ALL,
                        "x:",
                        Fore.MAGENTA + f"{res[5:8]}" + Style.RESET_ALL,
                        "y:",
                        Fore.MAGENTA + f"{res[8:11]}" + Style.RESET_ALL,
                        "\t detect time(ms):",
                        color + f"{detect_time * 1000:.2f}" + Style.RESET_ALL
                    )
                elif res[0] == "C":
                    # "CR1G2B3E"
                    print(
                        Fore.YELLOW + f"[{now_time}]" + Style.RESET_ALL,
                        "res:",
                        Fore.RED + f"{res[1]}" + Style.RESET_ALL,
                        Fore.GREEN + f"{res[2]}" + Style.RESET_ALL,
                        Fore.BLUE + f"{res[3]}" + Style.RESET_ALL,
                        "\t detect time(ms):",
                        color + f"{detect_time * 1000:.2f}" + Style.RESET_ALL
                    )


            # if self.sender is None:
            #     if cv2.waitKey(1) & 0xFF == ord("q"):
            #         break

    def test_usart_read(self, head: str, tail: str):
        """
        测试读取串口
        Args:
            head (str): 串口头
            tail (str): 串口尾
        Returns:
            None
        """
        while True:
            data1 = self.uart.new_read(head, tail)
            data = data1
            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"{now_time} readed {data}")


    def test_usart_write(self, data: str, head: str, tail: str):
        """
        测试写入串口
        Args:
            data (str): 写入的数据
            head (str): 串口头
            tail (str): 串口尾
        Returns:
            None
        """
        while True:
            self.uart.write(data, head, tail)
            time.sleep(0.3)
            self.uart.write("0051125375", "L", "E")
            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"{now_time} writed {data}")
            time.sleep(0.5)

    def detect_material_positions(self, _img:cv2.typing.MatLike) -> tuple[dict[str, tuple[int, int] | None], cv2.typing.MatLike]:
        """
        物料位置检测(跟踪)
        ----
        本方法不是顶层需求

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
        img2 = _img.copy()
        img_sharpen = self.annulus_circle_detector.sharpen(img)  # 锐化

        mask_lst = []   # 用于测试

        for color in COLOR_DIC.values():
            self.traditional_color_detector.update_threshold(color)
            binarization_img=self.traditional_color_detector.binarization(img_sharpen)
            center_point = self.traditional_color_detector.get_color_position(binarization_img)

            # region 用于测试
            mask_lst.append(binarization_img)
            # endregion

            if center_point is not None:
                res_dict[color] = center_point[:2]

                # region 用于测试
                # 画矩形
                cv2.rectangle(
                    img2,
                    (center_point[0] - center_point[2] // 2, center_point[1] - center_point[3] // 2),
                    (center_point[0] + center_point[2] // 2, center_point[1] + center_point[3] // 2),
                    (0, 255, 0),
                    2,
                )
                # 画出中心点
                cv2.circle(img2, (center_point[0], center_point[1]), 5, (0, 0, 255), -1)
                # 写出颜色
                cv2.putText(
                    img2,
                    color,
                    (center_point[0] - center_point[2] // 2, center_point[1] - center_point[3] // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (0, 255, 0),
                    2,
                )
                # endregion

        # region 用于测试
        # 将所有mask按位或
        mask_total = mask_lst[0]
        for mask in mask_lst[1:]:
            mask_total = cv2.bitwise_or(mask_total, mask)

        # img与mask按位与
        img_and = cv2.bitwise_and(img, img, mask=mask_total)

        res = np.vstack(
            (
                img2,
                cv2.cvtColor(mask_lst[0], cv2.COLOR_GRAY2BGR),
                cv2.cvtColor(mask_lst[1], cv2.COLOR_GRAY2BGR),
                cv2.cvtColor(mask_lst[2], cv2.COLOR_GRAY2BGR),
                img_and,
            )
        )
        # endregion

        return res_dict, res

    def test_material_positions(self, cap: Cap|ReceiveImg):
        """
        测试物料位置检测
        ----
        Args:
            cap_id (int): 摄像头编号
        """
        # cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        while True:
            _, img = cap.read()
            if img is None:
                continue
            res_dict, res = self.detect_material_positions(img)
            # cv2.imshow("img", res)
            self.sender.send(res)
            print(res_dict)
            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break

        cap.release()

if __name__ == "__main__":
    sender = SendImg("eth0", 4444)
    cap = Cap()
    test = Test_solution(sender=sender)
    test.test_func(cap, "1")
    # test.test_material_positions(0)
    # test.test_annulus_color(0, "G")
    # test.test_usart_read("@","#")
# end main