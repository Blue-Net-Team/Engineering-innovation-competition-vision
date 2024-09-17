#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-09-17 14:19:32 +0800
* LastEditTime: 2024-09-17 14:20:50 +0800
* FilePath: \工创2025\pth2onnx.py
* details: 
* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""
from detector.model import cnn
import torch

cnn = cnn.CNN()
cnn.load_state_dict(torch.load("best_model.pth"))
cnn.eval()
dummy_input = torch.randn(1, 20, 20, 3)
torch.onnx.export(cnn, dummy_input, "best_model.onnx", opset_version=11)