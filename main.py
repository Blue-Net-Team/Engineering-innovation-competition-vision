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
from utils import LoadCap, SendImg
from colorama import Fore, Style, init

init(autoreset=True)

HEAD: str = "@"
TAIL: str = "#"

DEAL_IMG = "hide"  # 处理图像的方式,包含"show"、"send"、"hide"

IP: str = "169.254.60.115"
PORT: int = 8000  # 端口号

SERIAL_PORT = "/dev/ttyUSB0"

# region 主代码
vs = SendImg(IP, PORT)
solution = Solution.Solution(SERIAL_PORT)
cap1 = LoadCap(0)

DEAL_IMG_DICT = {"show": Solution.show, "send": vs.send, "hide": lambda x: None}

solution_dict = {
    "1": solution.material_moving_detect,  # 物料运动检测
    "2": solution.get_material,  # 获取物料位号
    "3": solution.right_angle_detect,  # 直角检测
    "4": solution.annulus_top,      # 圆环检测
}


if DEAL_IMG == "send":
    vs.connecting()
    vs.start()

while True:
    sign = solution.uart.read(head=HEAD, tail=TAIL)  # 读取串口
    # 判断信号是否合法
    if sign in solution_dict:  # 信号合法
        for img in cap1:      # 读取摄像头
            if img is None:
                continue

            t0 = time.perf_counter()

            # 如果res是none，会继续读取下一帧图像，直到res不是none
            res, res_img = solution_dict[sign](img)

            t1 = time.perf_counter()
            detect_time = t1 - t0

            DEAL_IMG_DICT[DEAL_IMG](res_img)

            if res:
                solution.uart.write(res, head=HEAD, tail=TAIL)
                now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                time_show = detect_time * 1000

                if time_show <= 30:
                    color = Fore.GREEN
                elif time_show <= 50:
                    color = Fore.YELLOW
                else:
                    color = Fore.RED

                print(
                    f"[{now_time}] Detect time(ms):",
                        color + f"{time_show}" + Style.RESET_ALL,
                      "writed {res}"
                )
                break
    else:  # 信号非法
        print(f"Invalid sign {sign}")
        continue
# endregion
