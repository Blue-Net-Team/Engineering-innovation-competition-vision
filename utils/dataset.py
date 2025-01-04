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


class Cap(cv2.VideoCapture):
    def __init__(self, _id:int=0) -> None:
        super().__init__(_id)
        self.set(3, 640)
        self.set(4, 480)
        self.set(5, 60)
        self.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

        self.prev_frame = None
        self.alpha = 0.5  # 插值系数
        self.prev_tick = cv2.getTickCount()
        self.frame_count = 0
        self.fps_deque = deque(maxlen=30)  # 用于存储最近30帧的FPS值
        self.avg_fps = 0

    def read(self):
        ret, frame = super().read()
        if ret:
            if self.prev_frame is not None:
                # 使用插值方法生成新帧
                interpolated_frame = cv2.addWeighted(frame, self.alpha, self.prev_frame, 1 - self.alpha, 0)
                cv2.putText(interpolated_frame, f"FPS: {self.avg_fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.imshow('Interpolated Camera', interpolated_frame)

            cv2.imshow('Original Camera', frame)
            self.prev_frame = frame

            # 计算并显示FPS
            self.frame_count += 1
            if self.frame_count >= 10:
                tick = cv2.getTickCount()
                time_diff = (tick - self.prev_tick) / cv2.getTickFrequency()
                fps = self.frame_count / time_diff
                self.fps_deque.append(fps)
                self.avg_fps = sum(self.fps_deque) / len(self.fps_deque)
                self.prev_tick = tick
                self.frame_count = 0
        return ret, frame

    def release(self):
        super().release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    cap = Cap()
    cap.open(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
