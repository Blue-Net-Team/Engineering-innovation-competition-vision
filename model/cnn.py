import cv2
import torch
import torch.nn as nn

class CNN(nn.Module):
    """用神经网络识别颜色，红绿蓝白"""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # 0号节点，将20x20的图片进行卷积
        self.node0 = nn.Sequential(
            nn.Conv2d(3, 64, 3, 1, 1),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, 1, 1),
            nn.ReLU(),
            nn.AvgPool2d(2, 2),  # 输出尺寸: 64x10x10
            nn.Dropout(0.25)  # 添加Dropout层
        )

        # 1号节点，将10x10的图片进行卷积
        self.node1 = nn.Sequential(
            nn.BatchNorm2d(64),
            nn.Conv2d(64, 128, 3, 1, 1),
            nn.ReLU(),
            nn.Conv2d(128, 128, 3, 1, 1),
            nn.ReLU(),
            nn.AvgPool2d(2, 2),  # 输出尺寸: 128x5x5
            nn.Dropout(0.25)  # 添加Dropout层
        )

        # 全连接层
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128*5*5, 512),  # 调整全连接层的神经元数量
            nn.ReLU(),
            nn.Dropout(0.5),  # 添加Dropout层
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Dropout(0.5),  # 添加Dropout层
            nn.Linear(128, 4)
        )

    def forward(self, img_tensor: torch.Tensor):
        img_tensor = img_tensor.float()  # 将数据转换为float类型
        img_tensor = img_tensor.permute(0, 3, 1, 2)  # 交换维度
        # 0号节点
        img_tensor = self.node0(img_tensor)
        # 1号节点
        img_tensor = self.node1(img_tensor)
        # 全连接层
        img_tensor = self.fc(img_tensor)
        return img_tensor