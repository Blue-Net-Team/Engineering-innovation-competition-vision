#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-07-28 23:32:28 +0800
* LastEditTime: 2024-09-08 17:41:06 +0800
* FilePath: \工创25\detect.py
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


# 加载模型
cnn = CNN()
cnn.load_state_dict(torch.load("best_model.pth", map_location=torch.device('cpu')))
cnn.eval()


def detect(img: cv2.typing.MatLike):
    # img = cv2.resize(img, (128, 128))
    img = torch.from_numpy(img).unsqueeze(0).float()

    with torch.no_grad():
        output = cnn(img)
        prediction = torch.argmax(output, dim=1)
        probabilities = F.softmax(output, dim=1)
    
    return COLOR_DICT[prediction.item()], probabilities[0][prediction.item()].item()
