import cv2
from collections import deque


class Cap(cv2.VideoCapture):
    def __init__(self, _id: int = 0, w: int = 640, h: int = 480, fps: int = 60) -> None:
        super().__init__(_id)
        self.set(3, w)
        self.set(4, h)
        self.set(5, fps)
        self.set(6, cv2.VideoWriter.fourcc("M", "J", "P", "G"))


class LoadCap:
    def __init__(self, _id: int = 0, cap_method: str = "opencv") -> None:
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
            self.cap = Cap(_id)
        else:
            self.cap = InterpolatedCap(_id)

        self.img = None
        self.flag = True

    def __len__(self):
        return 1

    def __iter__(self):
        return self

    def __next__(self):
        _, frame = self.cap.read()
        if frame is not None:
            return frame
        else:
            return None

    def __del__(self):
        self.cap.release()

    def release(self):
        self.cap.release()


class InterpolatedCap(Cap):
    """
    运用插值补帧方法的Cap类
    """

    def __init__(self, _id: int = 0) -> None:
        super().__init__(_id)
        self.set(3, 640)
        self.set(4, 480)
        self.set(5, 100)
        self.set(6, cv2.VideoWriter.fourcc("M", "J", "P", "G"))

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
                interpolated_frame = cv2.addWeighted(
                    frame, self.alpha, self.prev_frame, 1 - self.alpha, 0
                )
            self.prev_frame = frame
        return ret, frame

    def release(self):
        super().release()
        cv2.destroyAllWindows()
