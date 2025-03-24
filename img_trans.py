"""
Copyright (C) 2025 IVEN-CN(He Yunfeng) and Anan-yy(Weng Kaiyi)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys

import cv2

from ImgTrans import SendImgUDP
from ImgTrans.ImgTrans import LoadWebCam, NeedReConnect
from utils import Cap

if sys.platform == "linux":
    stream = SendImgUDP("wlan0", 4444)
    cap = Cap()
    while True:
        if stream.connecting():
            break
    while True:
        try:
            img = cap.read()[1]
            stream.send(img)
        except NeedReConnect:
            while True:
                if stream.connecting():
                    break
elif sys.platform == "win32":
    # cap = LoadWebCam("169.254.133.100", 4444, "169.254.233.52")
    cap = LoadWebCam("192.168.137.161", 4444, "192.168.137.1")
    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    for img in cap:
        if img is None:
            continue
        cv2.imshow("img", img)
        if cv2.waitKey(1) == ord("q"):
            break
