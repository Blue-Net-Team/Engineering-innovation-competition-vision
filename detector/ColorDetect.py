#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-07-28 23:32:28 +0800
* LastEditTime: 2024-09-16 22:20:58 +0800
* FilePath: \工创2025\detector\ColorDetect.py
* details: 识别函数
* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""
import torch
import cv2
from model import CNN
import torch.nn.functional as F

COLOR_DICT = {
    0:'R',
    1:'G',
    2:'B',
    3:'W'
}

class ColorDetector:
    def __init__(self, model_path="best_model.pth"):
        # 加载模型
        self.cnn = CNN()
        self.cnn.load_state_dict(torch.load(model_path))
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.cnn.to(self.device)
        self.cnn.eval()

    def detect(self, img: cv2.typing.MatLike):
        """
        识别颜色
        ----
        :param img: 图片
        :return: 颜色，概率
        """
        # img = cv2.resize(img, (128, 128))
        img = torch.from_numpy(img).unsqueeze(0).float().to(self.device)

        with torch.no_grad():
            output = self.cnn(img)
            prediction = torch.argmax(output, dim=1)
            probabilities = F.softmax(output, dim=1)
        
        return COLOR_DICT[prediction.item()], probabilities[0][prediction.item()].item()
