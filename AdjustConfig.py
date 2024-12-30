import time
from typing import Callable
import cv2
import numpy as np
from Solution import Solution
from detector import (
    LineDetector,
    CircleDetector,
    TraditionalColorDetector,
)
from utils.dataset import LoadCap
from img_trans import LoadWebCam


class Ad_Config(Solution):
    """
    调整参数

    调整圆环参数，地面和物料
    调整直线参数，canny算子参数
    """

    def __init__(
        self,
        ser_port: str,
        cap_id: int,
        ip: str | None = None,
        port: int | None = None,
    ):
        super().__init__(ser_port)

        if ip is not None and port is not None:
            self.cap = LoadWebCam(ip, port)
        else:
            self.cap = LoadCap(cap_id)

    def adjust_circle(self, config_name: str):
        """
        调整圆环参数
        ----
        Args:
            config_name (str): 配置名称,包含"material"(物料)、"annulus"(圆环)
        """
        detector = self.annulus_circle_detector
        detect_func = self.annulus_circle_detector.detect_circle

        # 加载配置
        # detector.load_config("config.json", config_name)

        # 创建滑动条
        detector.createTrackbar()
        for img in self.cap:
            if img is None:
                continue
            t0 = time.perf_counter()

            try:
                read_img_time = t0 - t1
            except:
                read_img_time = 0

            res = detect_func(img)
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
                # 保存配置
                detector.save_config("config.json", config_name)
                # 释放摄像头
                self.cap.release()
                break

    def adjust_color_threshold(self):
        """
        调整颜色阈值
        ----
        """
        tcd = TraditionalColorDetector()
        # tcd.load_config("config.json")
        tcd.createTrackbar()
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        tcd.update_range()
        for img in self.cap:
            if img is None:
                continue

            binarization_img = tcd.binarization(img)

            # 按位与的图
            and_img = cv2.bitwise_and(img, img, mask=binarization_img)

            res_img = np.vstack(
                (img, cv2.cvtColor(binarization_img, cv2.COLOR_GRAY2BGR), and_img)
            )

            cv2.imshow("img", res_img)

            key_pressed = cv2.waitKey(1)

            if key_pressed & 0xFF == ord("q"):
                break
            elif key_pressed & 0xFF == ord("s"):
                tcd.save_params("config.json")

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    ad_config = Ad_Config(
        "COM5",
        0
    )
    # ad_config.adjust_circle("annulus")
    ad_config.adjust_color_threshold()
# end main
