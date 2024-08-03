import cv2
import torch
import torch.nn as nn

class CNN(nn.Module):
    """用神经网络识别颜色，红绿蓝白"""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        #0号节点，将128*128的图片进行卷积
        self.node0 = nn.Sequential(
            nn.Conv2d(3, 64, 3, 1, 1),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, 1, 1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )

        #1号节点，将64*64的图片进行卷积
        self.node1 = nn.Sequential(
            # 归一化
            nn.BatchNorm2d(64),
            nn.Conv2d(64, 128, 3, 1, 1),
            nn.ReLU(),
            nn.Conv2d(128, 128, 3, 1, 1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )

        # 全连接层
        self.fc = nn.Sequential(
            # 归一化
            nn.BatchNorm2d(128),
            nn.Flatten(),
            nn.Linear(128*32*32, 1024),
            nn.ReLU(),
            nn.Linear(1024, 10),
            nn.ReLU(),
            nn.Linear(10, 3)
        )


    def forward(self, img_tensor:torch.Tensor):
        img_tensor = img_tensor.float()  # 将数据转换为float类型
        img_tensor = img_tensor.permute(0, 3, 1, 2)  # 交换维度
        # 0号节点
        img_tensor = self.node0(img_tensor)
        # 1号节点
        img_tensor = self.node1(img_tensor)
        # 全连接层
        img_tensor = self.fc(img_tensor)
        return img_tensor
    
