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

Test_CNN_detector
----
继承自Solution类，用于测试CNN检测器的效果

通过鼠标点击获取ROI区域的颜色

方法:
    - `__init__(self, pt_path, _id):` 初始化方法，设置模型路径和摄像头ID
    - `mouse_callback(self, event, x, y, flags, param):` 鼠标回调函数，用于检测颜色
    - `draw_ROI(self, _frame: cv2.typing.MatLike):` 绘制ROI区域
    - `update_res_img(self):` 更新结果图像
    - `test(self):` 测试方法，显示检测结果

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
from detector.ColorDetect import ColorDetector
from utils.dataset import LoadCap
from detector import TraditionalColorDetector, LineDetector, PolygonDetector


class Test_solution(Solution):
    def __init__(self, pth_path: str, ser_port: str):
        """
        解决方案
        ----
        Args:
            pth_path (str): pytorch模型路径
            ser_port (str): 串口号
        """
        super().__init__(ser_port)
        self.FUNC_DICT = {
            "material": self.detect_material_positions,
            "annulus": self.annulus_detect,
            "right_angle": self.right_angle_detect,
            "rotator_center": self.get_rotator_centre,
            "if_move": self.material_moving_detect,
        }

    def test_func(self, cap_id: int, func_name: str):
        """
        测试Solution功能

        Args:
            cap_id (int): 摄像头编号
            func_name (str): 功能名称,包含"material"(物料)、"annulus"(圆环)、"right_angle"(直角)、"rotator_center"(转盘中心)、"if_move"(物料移动)
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

class Test_CNN_detector:
    """测试CNN检测器的效果"""

    def __init__(self, pt_path, _id) -> None:
        self.colorDetector = ColorDetector(pt_path)
        self.cap = LoadCap(_id)
        self.img = None
        self.x, self.y = 0, 0
        self.color = None

    def mouse_callback(self, event, x, y, flags, param):
        # 鼠标左键按下
        if self.img is None:
            return

        if event == cv2.EVENT_LBUTTONDOWN:
            self.x, self.y = x, y
            x0, y0 = self.x - 10, self.y - 10
            x1, y1 = self.x + 10, self.y + 10
            roi_img = self.img[y0:y1, x0:x1]
            self.color, _ = self.colorDetector.detect(roi_img)

    def draw_ROI(self, _frame: cv2.typing.MatLike):
        if self.x == 0 and self.y == 0:
            return _frame
        frame = _frame.copy()
        x0, y0 = self.x - 10, self.y - 10
        x1, y1 = self.x + 10, self.y + 10
        cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 1)
        return frame

    def update_res_img(self):
        if self.color is None or self.img is None:
            return self.img
        res_img = self.img.copy()
        x0, y0 = self.x - 10, self.y - 10
        x1, y1 = self.x + 10, self.y + 10
        cv2.rectangle(res_img, (x0, y0), (x1, y1), (0, 255, 0), 1)
        cv2.putText(
            res_img,
            self.color,
            (x0, y0 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
        )

        return res_img

    def test(self):
        cv2.namedWindow("test", cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback("test", self.mouse_callback)

        for self.img in self.cap:
            if self.img is None:
                continue

            res_img = self.update_res_img()

            cv2.imshow("test", res_img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.cap.release()
                break


class Test_Line_detect:
    def __init__(self) -> None:
        self.ld = LineDetector()

        try:
            self.ld.load_config("config.json")
        except:
            print("config.json not found")

    def test(self):
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
            angel1, angel2, point = self.ld.find_line(img, True)

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

class Polygon_Test(PolygonDetector):
    def __init__(self):
        super().__init__()
        self.createTrackbar()

    def test(self):
        cap = LoadCap(0)
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)

        for _img in cap:
            if _img is None:
                continue

            img = _img.copy()

            centers,approxs = self.get_polygon_centre(img, 4)

            for center, approx in zip(centers, approxs):
                cv2.circle(img, center, 5, (0, 255, 0), -1)
                cv2.polylines(img, [approx], True, (0, 255, 0), 2)

            cv2.imshow("img", img)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                # 保存配置
                self.save_config("config.json")
                break

    def test_img(self):
        _img = cv2.imread("test.png")
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)

        while True:
            img = _img.copy()
            centers,approxs = self.get_polygon_centre(img, 4)

            for center, approx in zip(centers, approxs):
                cv2.circle(img, center, 5, (0, 255, 0), -1)
                cv2.polylines(img, [approx], True, (0, 255, 0), 2)

            cv2.imshow("img", img)

            if cv2.waitKey(1) & 0xFF == ord("q"):
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
    test = Test_solution("best_model2024-12-09-12-46-06.pth", "COM6")
    test.test_func(0, "annulus")
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
