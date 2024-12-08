r"""
                                                   __----~~~~~~~~~~~------___
                                  .  .   ~~//====......          __--~ ~~
                  -.            \_|//     |||\\  ~~~~~~::::... /~
               ___-==_       _-~o~  \/    |||  \\            _/~~-
       __---~~~.==~||\=_    -_--~/_-~|-   |\\   \\        _/~
   _-~~     .=~    |  \\-_    '-~7  /-   /  ||    \      /
 .~       .~       |   \\ -_    /  /-   /   ||      \   /
/  ____  /         |     \\ ~-_/  /|- _/   .||       \ /
|~~    ~~|--~~~~--_ \     ~==-/   | \~--===~~        .\
         '         ~-|      /|    |-~\~~       __--~~
                     |-~~-_/ |    |   ~\_   _-~            /\
                          /  \     \__   \/~                \__
                      _--~ _/ | .-~~____--~-/                  ~~==.
                     ((->/~   '.|||' -_|    ~~-/ ,              . _||
                                -_     ~\      ~~---l__i__i__i--~~_/
                                _-~-__   ~)  \--______________--~~
                              //.-~~~-~_--~- |-------~~~~~~~~
                                     //.-~~~--\
                              神兽保佑
                             工创国一！！
"""

import time
import cv2
import Solution
from utils import LoadCap
from img_trans import VideoStreaming

# TODO: 请填写串口头和尾
HEAD: str = ...
TAIL: str = ...

DEAL_IMG = "show"  # 处理图像的方式,包含"show"、"send"、"hide"

IP: str = ""  # TODO: 填写主机(jetson)IP地址
PORT: int = 8000  # 端口号

MODEL_PATH = "best_model2024-09-22-22-09-44.pth"
SERIAL_PORT = "dev/ttyUSB0"  # TODO: 填写串口号

# region 主代码
vs = VideoStreaming(IP, PORT)
solution = Solution.Solution(MODEL_PATH, SERIAL_PORT)
cap1 = LoadCap(0)
cap2 = LoadCap(1)  # 用于直线识别

DEAL_IMG_DICT = {"show": Solution.show, "send": vs.send, "hide": lambda x: None}

solution_dict = {  # TODO: 可能要更改对应任务的串口信号
    "0": (cap1, solution.material_detect),  # 物料检测
    "1": (cap1, solution.annulus_detect),  # 圆环检测
    "2": (cap2, solution.right_angle_detect),  # 直角检测
}


if DEAL_IMG == "send":
    vs.connecting()
    vs.start()

while True:
    sign = solution.read_serial(head=HEAD, tail=TAIL)  # 读取串口
    # 判断信号是否合法
    if sign in solution_dict:  # 信号合法
        for img in solution_dict[sign][0]:
            if img is None:
                continue

            t0 = time.perf_counter()

            try:
                read_img_time = t0 - t1
            except:
                read_img_time = 0

            res: str | None = solution_dict[sign][1](img)

            t1 = time.perf_counter()
            detect_time = t1 - t0
            process_time = read_img_time + detect_time
            fps = 1 / process_time

            cv2.putText(
                img,
                f"FPS: {fps:.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

            DEAL_IMG_DICT[DEAL_IMG](img)

            if res:
                solution.write_serial(res, head=HEAD, tail=TAIL)
                break
    else:  # 信号非法
        print("Invalid sign")
        continue
# endregion
