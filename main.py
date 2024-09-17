#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-09-08 18:48:36 +0800
* LastEditTime: 2024-09-17 16:32:33 +0800
* FilePath: \工创2025\main.py
* details: 主文件

* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""

import time
import cv2
import Solution
from utils import LoadCap

solution = Solution.Solution()
cap = LoadCap(0)

HEAD:str = ...
TAIL:str = ...

solution_dict = {
    "0":solution.material_detect,       # 物料检测
    "1":solution.annulus_detect,        # 圆环检测
    "2":solution.right_angle_detect,        # 直角检测
}

count = 0
fps = 0

while True:
    sign = solution.read_serial(head=HEAD, tail=TAIL)
    if sign in solution_dict:
        for img in cap:
            if img is None: continue
            if count % 10 == 0:
                st = time.perf_counter()
            solution_dict[sign](img)
            if count % 10 == 9:
                et = time.perf_counter()
                fps = 10 / (et - st)
            count += 1
            cv2.putText(img, f"FPS: {fps:.2f}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.imshow("img", img)
    else:
        print("Invalid sign")
        continue
