import torch
import torch.nn as nn

class CNN(nn.Module):
    """用神经网络识别颜色，红绿蓝"""
    def __init__(self, img_size=20) -> None:
        """
        初始化
        ----
        :param img_size: 图片尺寸
        """
        super().__init__()

        # 0号节点，将图片进行卷积
        self.node0 = nn.Sequential(
            nn.Conv2d(3, 128, 3, 1, 1),
            nn.ReLU(),
            nn.AvgPool2d(2, 2),  # 输出尺寸: (img_size // 2, img_size // 2)
            nn.Dropout(0.25)  # 添加Dropout层
        )

        # 计算全连接层的输入神经元数量
        fc_input_size = (img_size // 2) * (img_size // 2) * 128  # 调整计算方式

        # 全连接层
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(fc_input_size, 128),  # 调整全连接层的神经元数量
            nn.ReLU(),
            nn.Dropout(0.5),  # 添加Dropout层
            nn.Linear(128, 3)
        )

    def forward(self, img_tensor: torch.Tensor):
        img_tensor = img_tensor.float()  # 将数据转换为float类型
        img_tensor = img_tensor.permute(0, 3, 1, 2)  # 交换维度
        # 0号节点
        img_tensor = self.node0(img_tensor)
        # 全连接层
        img_tensor = self.fc(img_tensor)
        return img_tensor