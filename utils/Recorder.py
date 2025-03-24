"""
Copyright (C) 2025 IVEN-CN(He Yunfeng) and Anan-yy(Weng Kaiyi)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
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
        """
        # 使用时间戳yy-mm-dd_hh-mm-ss-replay.mp4命名文件
        self.output_path = 'run_log/' + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '-replay.mp4'
        self.fps = 60
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
        position = (10, 10)
        size = 1
        font_color = (255, 0, 0)
        cv2.putText(frame, timestamp, position, font, size, font_color)
        self.writer.write(frame)

    def release(self):
        """
        释放资源
        """
        self.writer.release()
