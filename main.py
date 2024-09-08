#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-09-08 17:37:29 +0800
* LastEditTime: 2024-09-08 17:44:58 +0800
* FilePath: \工创25\main.py
* details: 主文件
* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""
import json

import cv2
import detect
from utils import LoadCap
from img_trans import VideoStreaming


class Main:
    def __init__(self) -> None:
        with open("ROI.json", "r") as f:
            ROI = json.load(f)

        self.x0 = ROI["x0"]
        self.y0 = ROI["y0"]
        self.x1 = ROI["x1"]
        self.y1 = ROI["y1"]

        self.cap = LoadCap(0)
        self.streaming = VideoStreaming("192.168.137.141", 8000)

    def main(self, debug:bool=False):
        if debug:
            self.streaming.connecting()
            self.streaming.start()
        for img in self.cap:
            if img is None:
                continue

            if debug:
                img_send = img.copy()
                cv2.rectangle(img_send, (self.x0, self.y0), (self.x1, self.y1), (0, 255, 0), 1)
                self.streaming.send(img_send)

            img = img[self.y0 : self.y1, self.x0 : self.x1]
            res = detect.detect(img)
            print(res)


if __name__ == "__main__":
    Main().main()
