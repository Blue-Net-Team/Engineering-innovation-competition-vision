import time
import cv2
import numpy as np
from Solution import Solution
from detector import ColorDetector, LineDetector, CircleDetector
from utils.dataset import LoadCap
from img_trans import LoadWebCam

class Ad_Config(Solution):
    """
    调整参数

    调整圆环参数，地面和物料
    调整直线参数，canny算子参数
    """
    def __init__(self, pth_path: str, ser_port: str, cap_id: int, ip:str|None=None, port:int|None=None):
        super().__init__(pth_path, ser_port)

        if ip is not None and port is not None:
            self.cap = LoadWebCam(ip, port)
        else:
            self.cap = LoadCap(cap_id)

        self.d = {
            "material": (self.material_circle_detector,self.material_detect),
            "annulus": (self.annulus_circle_detector,self.circle_detect),
        }

    def adjust(self, config_name: str):
        """
        调整圆环参数
        ----
        Args:
            config_name (str): 配置名称,包含"material"(物料)、"annulus"(圆环)
        """
        detector = self.d[config_name][0]
        detect_func = self.d[config_name][1]

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


if __name__ == "__main__":
    ad_config = Ad_Config("best_model2024-12-09-12-46-06.pth", "COM5", 0)
    ad_config.adjust("material")
# end main