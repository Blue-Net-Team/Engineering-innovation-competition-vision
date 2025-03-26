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
import os

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
        width =  320
        height = 240
        # 使用时间戳yy-mm-dd_hh-mm-ss-replay.avi命名文件
        self.output_path = 'run_log/' + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '-replay.avi'
        self.fps = 60
        self.frame_size = (width, height)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.writer = cv2.VideoWriter(self.output_path, fourcc, 20.0, (width, height))

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

        # 获取摄像头画面尺寸
        frame_height, frame_width = frame.shape[:2]

        # 计算缩放比例
        scale = min(self.frame_size[0] / frame_width, self.frame_size[1] / frame_height)

        # 调整画面大小
        resized_frame = cv2.resize(frame, (int(frame_width * scale), int(frame_height * scale)))

        # 创建黑色背景
        background = np.zeros((self.frame_size[1], self.frame_size[0], 3), dtype=np.uint8)

        # 将调整后的画面放置在背景中央
        y_offset = (self.frame_size[1] - resized_frame.shape[0]) // 2
        x_offset = (self.frame_size[0] - resized_frame.shape[1]) // 2
        background[y_offset:y_offset + resized_frame.shape[0], x_offset:x_offset + resized_frame.shape[1]] = resized_frame

        self.writer.write(background)

    def release(self):
        """
        释放资源
        """
        self.writer.release()
        cv2.destroyAllWindows()
        print(f"视频已保存到 {recorder.output_path}")

if __name__ == '__main__':
    recorder = Recorder()
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        recorder.record(frame)
        cv2.imshow('Recording', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    recorder.release()
