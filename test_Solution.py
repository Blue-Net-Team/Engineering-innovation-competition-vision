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
import cv2
import numpy as np
from Solution import Solution
from utils.dataset import LoadCap
from detector import TraditionalColorDetector, LineDetector


COLOR_DIC = {0: "R", 1: "G", 2: "B"}


class Test_solution(Solution):
    def __init__(self, ser_port: str):
        """
        解决方案
        ----
        Args:
            pth_path (str): pytorch模型路径
            ser_port (str): 串口号
        """
        super().__init__(ser_port)
        self.FUNC_DICT = {
            "annulus": self.annulus_detect,
            "right_angle": self.right_angle_detect,
            "rotator_center": self.get_rotator_centre,
            "if_move": self.material_moving_detect,
            "line_angle": self.get_line_angle_top,
        }

    def test_func(self, cap_id: int, func_name: str):
        """
        测试Solution功能

        Args:
            cap_id (int): 摄像头编号
            func_name (str): 功能名称,包含"annulus"(圆环)、"right_angle"(直角)、"rotator_center"(转盘中心)、"if_move"(物料移动)
        Returns:
            None
        """
        cap = LoadCap(cap_id)
        for img in cap:
            if img is None:
                continue
            t0 = time.perf_counter()

            try:
                read_img_time = t0 - t1
            except:
                read_img_time = 0

            res = self.FUNC_DICT[func_name](img)
            t1 = time.perf_counter()

            detect_time = t1 - t0

            process_time = read_img_time + detect_time
            fps = 1 / process_time

            cv2.putText(  # 显示FPS
                img,
                f"FPS: {fps:.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

            cv2.imshow("img", img)
            print(res)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

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
            data = self.read_serial(head, tail)
            print(
                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} readed {data}"
            )

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
            self.write_serial(data, head, tail)
            print(
                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} writed {data}"
            )
            time.sleep(0.5)

    def test_annulus_color(self, cap_id: int, color: str):
        """
        测试圆环颜色检测
        ----
        Args:
            cap_id (int): 摄像头编号
            color (str): 颜色名称
        """
        cap = LoadCap(cap_id)
        for img in cap:
            if img is None:
                continue
            res = self.get_with_and_img(img, color)
            cv2.imshow("img", img)
            print(res)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

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
        img_sharpen = self.material_circle_detector.sharpen(img)  # 锐化

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

    def test_material_positions(self, cap_id: int):
        """
        测试物料位置检测
        ----
        Args:
            cap_id (int): 摄像头编号
        """
        cap = LoadCap(cap_id)
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        for img in cap:
            if img is None:
                continue
            res_dict, res = self.detect_material_positions(img)
            cv2.imshow("img", res)
            print(res_dict)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()

class Test_Line_detect:
    def __init__(self) -> None:
        self.ld = LineDetector()

        try:
            self.ld.load_config("config.json")
        except:
            print("config.json not found")

    def test_right_angle(self):
        self.ld.createTrackbar()
        cap = LoadCap(0)
        for img in cap:
            if img is None:
                continue
            # region 计算帧率部分1
            t0 = time.perf_counter()

            try:
                read_img_time = t0 - t1
            except:
                read_img_time = 0
            # endregion

            img = self.ld.sharpen(img)
            angel1, angel2, point = self.ld.get_right_angle(img, True)

            # region 计算帧率部分2
            t1 = time.perf_counter()

            detect_time = t1 - t0

            process_time = read_img_time + detect_time
            fps = 1 / process_time
            # endregion

            cv2.putText(  # 显示FPS
                img,
                f"FPS: {fps:.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
            cv2.imshow("img", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.ld.save_config("config.json")
                cap.release()
                break

    def test_line(self):
        self.ld.createTrackbar()
        cap = LoadCap(0)
        for img in cap:
            if img is None:
                continue
            # region 计算帧率部分1
            t0 = time.perf_counter()

            try:
                read_img_time = t0 - t1
            except:
                read_img_time = 0
            # endregion

            img = self.ld.sharpen(img)
            lines = self.ld.find_line(img)

            # region 计算帧率部分2
            t1 = time.perf_counter()

            detect_time = t1 - t0

            process_time = read_img_time + detect_time
            fps = 1 / process_time
            # endregion

            for line in lines:
                self.ld.draw_line(img, line)

            cv2.putText(  # 显示FPS
                img,
                f"FPS: {fps:.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
            cv2.imshow("img", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.ld.save_config("config.json")
                cap.release()
                break

class TraditionalColor_Test(TraditionalColorDetector):
    def __init__(self):
        super().__init__()
        self.createTrackbar()

    def test(self):
        cap = LoadCap(0)
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)

        for img in cap:
            if img is None:
                continue

            mask = self.binarization(img)
            bit_and = cv2.bitwise_and(img, img, mask=mask)
            res = np.vstack((img, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), bit_and))

            cv2.imshow("img", res)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

if __name__ == "__main__":
    test = Test_solution("COM5")
    # test.test_func(0, "material")
    test.test_material_positions(0)
    # test.test_circle_edge(0)
    # test.test_usart_read("head", "tail")
    # test.test_usart_write("data", "head", "tail")

    # test = Test_CNN_detector("best_model2024-12-09-12-46-06.pth", 0)
    # test.test()

    # test = Test_Line_detect()
    # test.test()

    # test = Polygon_Test()
    # test.test_img()

    # test = TraditionalColor_Test()
    # test.test()
# end main
