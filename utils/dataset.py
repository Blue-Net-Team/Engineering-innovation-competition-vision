import os
import threading
import cv2

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
