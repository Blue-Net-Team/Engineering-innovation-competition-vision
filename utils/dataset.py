import os
import threading
import cv2
import torch
from torch.utils.data import DataLoader, Dataset

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

class DataSet1(Dataset):
    """
    用文件夹中的标签作为标签的数据集
    """
    def __init__(self, path:str='./datas/train') -> None:
        img_floders_path = path + '/img'        # 图片文件夹路径
        label_floders_path = path + '/label'    # 标签文件夹路径

        self.img_list = get_all_file_paths(img_floders_path)       # 获取所有图片路径
        self.label_list = get_all_file_paths(label_floders_path)   # 获取所有标签路径

        # 按照文件名排序
        self.img_list = sorted(self.img_list, key=self.sort_key)
        self.label_list = sorted(self.label_list, key=self.sort_key)


    def sort_key(self, s):
        # 提取出文件名中的数字部分
        return int(s.split('/')[-1].split('.')[0])
    
    def __len__(self):
        return len(self.img_list)
    
    def __getitem__(self, index):
        img_path = self.img_list[index]
        label_path = self.label_list[index]

        img = cv2.imread(img_path)          # 读取图片
        
        with open(label_path, 'r') as f:    # 读取标签
            label = f.read().strip()

        return torch.from_numpy(img), label
    

class DataSet2(Dataset):
    """
    用文件夹作为标签的数据集
    """
    def __init__(self, path:str='./datas/train', ifrandom:bool=False) -> None:
        self.path_list = get_all_file_paths(path)       # 获取所有文件路径
        if ifrandom:
            # 随机打乱path_list
            import random
            random.shuffle(self.path_list)

    def __len__(self):
        return len(self.path_list)
    
    def __getitem__(self, index):
        img_path = self.path_list[index]
        label = os.path.basename(os.path.dirname(img_path))

        label = COLOR_DIC[label]            # 将标签转换为数字

        img = cv2.imread(img_path)          # 读取图片
        return torch.from_numpy(img), label


class LoadCap:
    def __init__(self, _id:int=0) -> None:
        self.cap = cv2.VideoCapture(_id)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        self.cap.set(5, 60)
        self.cap.set(6,cv2.VideoWriter.fourcc('M','J','P','G'))

        self.img = None

    def get_img(self):
        while True:
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
        

d = DataSet2()