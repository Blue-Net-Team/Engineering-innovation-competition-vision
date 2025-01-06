import threading
import time
import cv2
from collections import deque

class LoadCap:
    def __init__(self, _id:int=0, cap_method:str="opencv") -> None:
        """
        初始化
        ----
        Args:
            _id (int):摄像头编号
            cap_method (str):摄像头的方法，包括'opencv'和'interpolated'
        """
        if cap_method not in ["opencv", "interpolated"]:
            raise ValueError("argument cap_method must is opencv or interpolated")
        if cap_method == "opencv":
            self.cap = cv2.VideoCapture(_id)
        else:
            self.cap=Cap(_id)

        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.cap.set(5, 60)
        self.cap.set(6,cv2.VideoWriter.fourcc('M','J','P','G'))

        self.img = None
        self.flag = True

    def get_img(self):
        while self.flag:
            ret, frame = self.cap.read()
            if ret:
                self.img = frame

    def __len__(self):
        return 1

    def __iter__(self):
        self.thread = threading.Thread(target=self.get_img)
        self.thread.start()
        return self

    def __next__(self):
        if self.img is not None:
            return self.img
        else:
            return None

    def release(self):
        self.flag = False
        self.thread.join()
        self.cap.release()
        cv2.destroyAllWindows()

    def __del__(self):
        self.release()

class Cap(cv2.VideoCapture):
    """
    运用插值补帧方法的Cap类
    """
    def __init__(self, _id:int=0) -> None:
        super().__init__(_id)
        self.set(3, 640)
        self.set(4, 480)
        self.set(5, 100)
        self.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

        self.prev_frame = None
        # 插值系数
        self.alpha = 0.5
        self.prev_tick = cv2.getTickCount()
        self.frame_count = 0
        # 用于存储最近30帧的FPS值
        self.fps_deque = deque(maxlen=30)
        self.avg_fps = 0


    def read(self):
        ret, frame = super().read()
        if ret:
            if self.prev_frame is not None:
                # 使用插值方法生成新帧
                interpolated_frame = cv2.addWeighted(frame, self.alpha, self.prev_frame, 1 - self.alpha, 0)
            self.prev_frame = frame
        return ret, frame

    def release(self):
        super().release()
        cv2.destroyAllWindows()

