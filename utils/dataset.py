import os
import cv2
import torch


def get_all_file_paths(directory):
    """
    获取目录下所有文件的路径
    """
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

class DataSet:
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

