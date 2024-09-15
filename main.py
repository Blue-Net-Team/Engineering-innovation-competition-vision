#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-09-08 18:48:36 +0800
* LastEditTime: 2024-09-11 15:40:23 +0800
* FilePath: \ColorDetector-base-on-pytorch\main.py
* details: 主文件

* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""

import json
import time

import cv2
import detect
from utils import LoadCap
from img_trans import VideoStreaming


class Main:
    def __init__(self) -> None:
        with open("ROI.json", "r") as f:
            ROI = json.load(f)

        self.x0 = ROI[0]
        self.y0 = ROI[1]
        self.x1 = ROI[2]
        self.y1 = ROI[3]

        self.cap = LoadCap(0)

    def main(self, debug: bool = False):
        if debug:
            # 下面写的是树莓派的ip地址
            self.streaming = VideoStreaming("192.168.137.141", 8000)
            self.streaming.connecting()
            self.streaming.start()

        count = 0
        total_time = 0

        for img in self.cap:
            if img is None:
                continue
            if count % 10 == 0:
                st = time.perf_counter()

            img1 = img[self.y0 : self.y1, self.x0 : self.x1]
            res = detect.detect(img1)

            if count % 10 == 9:
                et = time.perf_counter()
                total_time += et - st
                avg_fps = 10 / total_time
                total_time = 0
                print(f"Average FPS: {avg_fps:.2f}, color: {res[0]}, probability: {res[1]:.2f}")
            else:
                total_time += time.perf_counter() - st

            count += 1

            if debug:
                img_send = img.copy()
                cv2.rectangle(
                    img_send, (self.x0, self.y0), (self.x1, self.y1), (0, 255, 0), 1
                )
                self.streaming.send(img_send)


if __name__ == "__main__":
    # 如果不需要图传，将main()中的debug参数设置为False
    Main().main(True)
