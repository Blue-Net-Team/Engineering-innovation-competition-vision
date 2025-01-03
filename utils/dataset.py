from ast import In
import os
import threading
import cv2
from collections import deque

COLOR_DIC = {
    'R':0,
    'G':1,
    'B':2,
    'W':3
}

def get_all_file_paths(directory):
    """
    获取目录下所有文件的路径
    """
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths


class LoadCap:
    def __init__(self, _id:int=0) -> None:
        self.cap = cv2.VideoCapture(_id)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
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


class InterpolationCap(cv2.VideoCapture):
    def __init__(self, _id:int=0) -> None:
        super().__init__(_id)
        self.set(3, 640)
        self.set(4, 480)
        self.set(5, 60)
        self.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

        self.img = None
        self.flag = True

    def get_img(self):
        while self.flag:
            ret, frame = self.read()
            if ret:
                self.img = frame

    def release(self):
        self.flag = False
        super().release()
        cv2.destroyAllWindows()

    def open_camera(self, camera_id=0):
        self.open(camera_id)
        if not self.isOpened():
            print(f"not open")
            return

        prev_frame = None
        # 插值系数
        alpha = 0.5

        prev_tick = cv2.getTickCount()
        frame_count = 0
        # 用于存储最近30帧的FPS值
        fps_deque = deque(maxlen=30)

        avg_fps = 0
        while True:
            ret, frame = self.read()
            if not ret:
                break

            if prev_frame is not None:
                # 使用插值方法生成新帧
                interpolated_frame = cv2.addWeighted(frame, alpha, prev_frame, 1 - alpha, 0)
                cv2.putText(interpolated_frame, f"FPS: {avg_fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.imshow('Interpolated Camera', interpolated_frame)

            cv2.imshow('Original Camera', frame)
            prev_frame = frame

            # 计算并显示FPS
            frame_count += 1
            if frame_count >= 10:
                tick = cv2.getTickCount()
                time_diff = (tick - prev_tick) / cv2.getTickFrequency()
                fps = frame_count / time_diff
                fps_deque.append(fps)
                avg_fps = sum(fps_deque) / len(fps_deque)
                prev_tick = tick
                frame_count = 0

            if cv2.waitKey(1) == 27:
                break

        self.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    camera_id = 0  # 可以根据需要更改摄像头索引
    cap = InterpolationCap()
    cap.open_camera(camera_id)
