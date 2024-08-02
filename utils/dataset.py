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

class DataSet1:
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
    

class DataSet2:
    """
    用文件夹作为标签的数据集
    """
    def __init__(self, path:str='./datas/train') -> None:
        self.path_list = get_all_file_paths(path)       # 获取所有文件路径

    def __len__(self):
        return len(self.path_list)
    
    def __getitem__(self, index):
        img_path = self.path_list[index]
        label = os.path.basename(os.path.dirname(img_path))

        img = cv2.imread(img_path)          # 读取图片
        return torch.from_numpy(img), label



class ImageDataLoader:
    def __init__(self, dataset, batch_size=1):
        self.dataset = dataset
        self.batch_size = batch_size

    def __iter__(self):
        self.count = 0
        return self
    
    def __next__(self):
        if self.count >= len(self.dataset):
            raise StopIteration
        img, label = self.dataset[self.count]
        self.count += 1
        return img, label

