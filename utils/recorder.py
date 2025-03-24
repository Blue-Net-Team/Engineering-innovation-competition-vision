import cv2
import numpy as np
import time

class Recorder:
    """
    记录器
    ----
    用于记录视频
    """
    def __init__(self):
        """
        初始化

        ----
        Args:
            output_path(str): 输出路径
            fps(int): 帧率
            frame_size(tuple): 帧大小
            writer(cv2.VideoWriter): 视频写入器

        """
        self.output_path = 'run_log/replay.mp4'
        self.fps = 30
        self.frame_size = (320, 240)
        self.writer = cv2.VideoWriter(
            self.output_path,
            cv2.CAP_FFMPEG,
            self.fps,
            self.frame_size
        )

    def record(self, frame: np.ndarray):
        """
        记录图像

        ----
        Args:
            frame: 图像帧

        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 字体设置(类型，位置，大小，颜色)
        font = cv2.FONT_HERSHEY_SIMPLEX
        position = (10, 30)
        size = 1
        font_color = (255, 0, 0)
        cv2.putText(frame, timestamp, position, font, size, font_color)
        self.writer.write(frame)

    def release(self):
        """
        释放资源
        """
        self.writer.release()
