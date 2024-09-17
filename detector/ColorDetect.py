#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-07-28 23:32:28 +0800
* LastEditTime: 2024-09-17 13:45:07 +0800
* FilePath: \工创2025\detector\ColorDetect.py
* details: 识别函数
* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""
import torch
import torch.nn.functional as F
import cv2
try:
    from detector.model import cnn
except ModuleNotFoundError:
    from model import cnn

import onnxruntime as ort
import numpy as np

class ColorDetector:
    def __init__(self, model_path="best_model.onnx"):
        # 加载模型
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.session = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider' if self.device == 'cuda' else 'CPUExecutionProvider'])

    def detect(self, img: cv2.typing.MatLike):
        """
        识别颜色
        ----
        :param img: 图片
        :return: 颜色，概率
        """
        img = np.expand_dims(img, axis=0).astype(np.float32)

        inputs = {self.session.get_inputs()[0].name: img}
        outputs = self.session.run(None, inputs)
        output = torch.tensor(outputs[0])
        prediction = torch.argmax(output, dim=1)
        probabilities = F.softmax(output, dim=1)
        return prediction, probabilities

# 将模型转换为 ONNX 格式并保存
if __name__ == "__main__":
    cnn = cnn.CNN()
    cnn.load_state_dict(torch.load("best_model.pth"))
    cnn.eval()
    dummy_input = torch.randn(1, 20, 20, 3)
    torch.onnx.export(cnn, dummy_input, "best_model.onnx", opset_version=11)