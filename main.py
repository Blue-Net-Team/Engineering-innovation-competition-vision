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
import datetime
import threading
import time
from colorama import Fore, Style, init
import cv2
import Solution
from utils import SendImg, Cap, Switch
import numpy as np

from utils.ImgTrans import NeedReConnect

init(autoreset=True)

class MainSystem:

    deal_img_method = "hide"  # 处理图像的方法
    ori_imgTrans_running_flag = False  # 原始图像是否正在传输
    task_running_flag = False  # 任务是否正在运行


    def __init__(
        self,
        ser_port: str,
        pkgHEAD:str,
        pgkTAIL:str,
        sender: SendImg | None = None,
        deal_img_method: str = "hide"
    ) -> None:
        """
        主系统
        ----
        Args:
            ser_port (str): 串口号
            pakHEAD (str): 包头
            pgkTAIL (str): 包尾
            sender (SendImg): 图传发送器
            deal_img_method (str): 处理图像的方法,包含"show"(显示)、"hide"(隐藏)、"send"(发送)
        """
        self.cap = Cap()
        self.solution = Solution.Solution(ser_port)
        self.switch = Switch(18)
        self.sender = sender
        self.HEAD = pkgHEAD
        self.TAIL = pgkTAIL
        self.DEAL_IMG_DICT = {"show": Solution.show, "hide": lambda x: None}
        if self.sender:
            self.DEAL_IMG_DICT["send"] = self.sender.send

        self.TASK_DICT = {
            "1": self.solution.material_moving_detect,  # 物料运动检测
            "2": self.solution.get_material,  # 获取物料位号
            "3": self.solution.right_angle_detect,  # 直角检测
            "4": self.solution.annulus_top,  # 圆环检测
        }

        self.deal_img_method = deal_img_method

    def main(self):
        """
        主函数
        ----
        """
        while True:
            switch_status = self.switch.read_status()

            if switch_status:
                # 开关状态1，开图传，关任务
                print(
                    Fore.YELLOW + f"[{getTimeStamp()}]:" + Fore.RESET,
                    Fore.WHITE + "模式切换为" + Fore.RESET,
                    Fore.CYAN + "图传" + Fore.RESET
                )

                # 检查sender
                if self.sender is None:
                    print(
                        Fore.RED + f"[{getTimeStamp()}]:" + Fore.RESET,
                        Fore.RED + "没有设置图传发送器对象" + Fore.RESET
                    )
                    break

                # 设置标志
                self.ori_imgTrans_running_flag = True
                self.task_running_flag = False

                # 等待连接
                print(
                    Fore.YELLOW + f"[{getTimeStamp()}]:" + Fore.RESET,
                    Fore.WHITE + "等待图传连接\tIP:" + Fore.RESET,
                    Fore.CYAN + f"{self.sender.host}" + Fore.RESET,
                )
                while self.ori_imgTrans_running_flag:
                    if self.sender.connecting():
                        break
                    if not self.switch.read_status():
                        # 开关状态2，关闭图传
                        self.ori_imgTrans_running_flag = False
                        break

                print(
                    Fore.YELLOW + f"[{getTimeStamp()}]:" + Fore.RESET,
                    Fore.WHITE + "图传连接成功" + Fore.RESET,
                )

                while self.ori_imgTrans_running_flag:
                    _, img = self.cap.read()

                    # 检查开关
                    if not self.switch.read_status():
                        # 开关状态2，关闭图传
                        self.ori_imgTrans_running_flag = False
                        break

                    if img is None:
                        continue

                    # 发送图像
                    try:
                        self.sender.send(img)
                    except NeedReConnect:
                        print(
                            Fore.RED + f"[{getTimeStamp()}]:" + Fore.RESET,
                            Fore.RED + "图传连接中断" + Fore.RESET
                        )

                        # 检查开关
                        if not self.switch.read_status():
                            # 开关状态2，关闭图传
                            self.ori_imgTrans_running_flag = False
                            break
                        else:
                            # 重新连接
                            print(
                                Fore.YELLOW + f"[{getTimeStamp()}]:" + Fore.RESET,
                                Fore.WHITE + "重新连接" + Fore.RESET
                            )
                            while self.ori_imgTrans_running_flag:
                                if not self.switch.read_status():
                                    # 开关状态2，关闭图传
                                    self.ori_imgTrans_running_flag = False
                                    break
                                if self.sender.connecting():
                                    continue

                    # 检查开关
                    if not self.switch.read_status():
                        # 开关状态2，关闭图传
                        self.ori_imgTrans_running_flag = False
                        break

            else:
                # 开关状态2，开任务线程，关图传线程
                print(
                    Fore.YELLOW + f"[{getTimeStamp()}]:" + Fore.RESET,
                    Fore.WHITE + "模式切换为" + Fore.RESET,
                    Fore.CYAN + "任务模式" + Fore.RESET
                )

                # 设置标志
                self.ori_imgTrans_running_flag = False
                self.task_running_flag = True

                # 连接图传
                if self.deal_img_method == "send" and self.sender:
                    print(
                        Fore.YELLOW + f"[{getTimeStamp()}]:" + Fore.RESET,
                        Fore.WHITE + "等待图传连接\tIP:" + Fore.RESET,
                        Fore.CYAN + f"{self.sender.host}" + Fore.RESET,
                    )
                    while self.task_running_flag:
                        if self.sender.connecting():
                            print(
                                Fore.YELLOW + f"[{getTimeStamp()}]:" + Fore.RESET,
                                Fore.WHITE + "图传连接成功" + Fore.RESET,
                            )
                            break
                        if self.switch.read_status():
                            self.task_running_flag = False
                            break

                # 开始任务
                while self.task_running_flag:
                    # 读取串口信号
                    sign = self.solution.uart.new_read(self.HEAD, self.TAIL)

                    if sign is None:
                        # 检查开关
                        if self.switch.read_status():
                            self.task_running_flag = False
                            break
                        else:
                            continue

                    if sign not in self.TASK_DICT.keys():
                        print(
                            Fore.RED + f"[{getTimeStamp()}]:" + Fore.RESET,
                            Fore.RED + "非法信号" + Fore.RESET
                        )
                        # 检查开关
                        if self.switch.read_status():
                            self.task_running_flag = False
                            break
                        else:
                            continue

                    # 执行任务
                    t0 = time.perf_counter()
                    num = 0
                    while self.task_running_flag:
                        if sign in ["1", "2"]:
                            # 去除缓冲区图像
                            for i in range(30):
                                _, img = self.cap.read()
                                cv2.putText(
                                    img,
                                    "Cleaning Buffer...",
                                    (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1,
                                    (0, 0, 255),
                                )
                                self.DEAL_IMG_DICT[self.deal_img_method](img)

                        _, img = self.cap.read()
                        # 切割图片
                        img = img[:400,:]

                        res, res_img = self.TASK_DICT[sign](img)

                        num += 1

                        print(
                            Fore.GREEN + f"[{getTimeStamp()}]" + Fore.RESET,
                            Fore.WHITE + "result:" + Fore.RESET,
                            Fore.MAGENTA + f"{res}" + Fore.RESET,
                        )

                        self.DEAL_IMG_DICT[self.deal_img_method](res_img)

                        if res:
                            t1 = time.perf_counter()
                            used_time_ms = (t1 - t0) * 1000
                            if used_time_ms < 40:
                                color = Fore.GREEN
                            elif used_time_ms < 60:
                                color = Fore.YELLOW
                            else:
                                color = Fore.RED

                            print(
                                Fore.GREEN + f"[{getTimeStamp()}]" + Fore.RESET,
                                Fore.WHITE + "sended:" + Fore.RESET,
                                Fore.MAGENTA + f"{res}\t" + Fore.RESET,
                                Fore.WHITE + "used time:" + Fore.RESET,
                                color + f"{used_time_ms:.2f}ms" + Fore.RESET,
                            )
                            self.solution.uart.write(res)
                            break

                        # 每30帧检查一次开关
                        if num % 30 == 0:
                            if not self.switch.read_status():
                                self.task_running_flag = False
                                break


def getTimeStamp():
    """
    获取时间戳(包含毫秒)
    ----
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]


if __name__ == "__main__":
    mainsystem = MainSystem(
        ser_port="/dev/ttyUSB0",
        pkgHEAD="@",
        pgkTAIL="#",
        sender=SendImg("wlan1", 4444),
        deal_img_method="send"
    )
    mainsystem.main()
# end main
