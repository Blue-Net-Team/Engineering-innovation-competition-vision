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
from colorama import Fore, Style, init
import cv2
import Solution
from utils import SendImg, Cap, Switch
import numpy as np

from utils.ImgTrans import NeedReConnect

init(autoreset=True)

class MainSystem:

    sending_ori_flag = False    # 发送原始图像线程标志
    send_main_flag = False      # 发送主线程标志
    send_main = False       # 主函数是否要发送图像
    main_flag = False       # 主线程标志
    reading_flag = True     # 读取图像线程标志

    def __init__(
        self,
        ser_port: str,
        sender: SendImg | None=None,
        if_send_main: bool = False
    ) -> None:
        """
        主系统
        ----
        Args:
            ser_port (str): 串口号
        """
        self.cap = Cap()
        self.solution = Solution.Solution(ser_port)
        self.switch = Switch(18)
        self.sender = sender

        self.need_send_img:cv2.typing.MatLike = np.zeros((480, 640, 3), np.uint8)
        cv2.putText(
            self.need_send_img,
            "No Image",
            (100, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        self.img = self.need_send_img.copy()

        self.TASK_DICT = {
            "1": self.solution.material_moving_detect,  # 物料运动检测
            "2": self.solution.get_material,  # 获取物料位号
            "3": self.solution.right_angle_detect,  # 直角检测
            "4": self.solution.annulus_top,  # 圆环检测
        }

        self.send_main = if_send_main

    def main(self):
        """
        主函数
        ----
        """
        # 读取图像
        img_thread = threading.Thread(target=self.__read_img)
        img_thread.start()

        while True:
            switch_status = self.switch.read_status()

            if switch_status:
                if self.send_main_flag:  # 如果主线程图传线程已启动, 则关闭
                    print("Stop sending main")
                    self.send_main_flag = False
                    main_sending_thread.join()

                if not self.sending_ori_flag:  # 如果(原图像)图传线程未启动, 则启动
                    # TODO:更新self.need_send_img
                    print("Start sending image")
                    self.sending_ori_flag = True
                    img_ori_sending_thread = threading.Thread(
                        target=self.__send_img, args=(self.sending_ori_flag,)
                    )
                    img_ori_sending_thread.start()

                if self.main_flag:  # 如果主线程已启动, 则关闭
                    print("Stop main")
                    self.main_flag = False
                    self.solution.uart.read_falg = False
                    main_thread.join()

            else:
                if self.sending_ori_flag:  # 如果(原图像)图传线程已启动, 则关闭
                    print("Stop sending image")
                    self.sending_ori_flag = False
                    img_ori_sending_thread.join()

                if not self.main_flag:  # 如果主线程未启动, 则启动
                    print("Start main")
                    self.main_flag = True
                    self.solution.uart.read_falg = True
                    main_thread = threading.Thread(target=self.__main)
                    main_thread.start()

                    if self.send_main:
                        print("Start sending main")
                        self.send_main_flag = True
                        main_sending_thread = threading.Thread(
                            target=self.__send_img, args=(self.send_main_flag, False)
                        )
                        main_sending_thread.start()

    def __send_img(self, flag, if_ori_img: bool = True):
        """
        发送原始图像
        ----
        """
        if self.sender:
            self.__connecting()
            print(
                Fore.GREEN + f"[{self.__get_time()}]" + Fore.RESET,
                "Start sending image"
            )
            while flag:
                if if_ori_img:
                    self.need_send_img = self.img.copy()

                try:
                    self.sender.send(self.need_send_img)
                except NeedReConnect:
                    self.__connecting()
        else:
            print(
                Fore.RED + "No sender, please check the network connection" + Fore.RESET
            )

    def __connecting(self):
        if self.sender:
            print(
                Fore.YELLOW + f"[{self.__get_time()}]" + Fore.RESET,
                "Waiting for connecting...",
            )
            while self.sending_ori_flag:
                if self.sender.connecting():
                    break

    def __get_time(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def __main(self):
        while self.main_flag:
            sign = self.solution.uart.read("@", "#")

            if sign in self.TASK_DICT:
                while True:
                    img = self.img.copy()
                    img = img[:400,:]

                    t0 = datetime.datetime.now()
                    res, self.need_send_img = self.TASK_DICT[sign](img)
                    t1 = datetime.datetime.now()

                    if res is not None:
                        detect_time_ms = (t1 - t0).total_seconds() * 1000

                        if detect_time_ms < 40:
                            font_color = Fore.GREEN
                        elif detect_time_ms < 60:
                            font_color = Fore.YELLOW
                        else:
                            font_color = Fore.RED

                        print(
                            Fore.BLUE + f"[{self.__get_time()}]" + Fore.RESET,
                            f"res:",
                            Fore.MAGENTA + f"{res}" + Fore.RESET,
                            "\t detect time(s):",
                            font_color + f"{detect_time_ms:.2f}" + Fore.RESET,
                        )

                        self.solution.uart.write(res)
                        break

            else:
                print(
                    Fore.BLUE + f"[{self.__get_time()}]" + Fore.RESET,
                    Fore.RED + "Invalid sign" + Fore.RESET
                )

    def __read_img(self):
        """
        读取图像
        ----
        """
        while self.reading_flag:
            _, img = self.cap.read()
            if img is None:
                continue
            self.img = img


if __name__ == "__main__":
    mainsystem = MainSystem(
        ser_port="/dev/ttyUSB0",
        sender=SendImg("169.254.60.115", 4444)
    )
    mainsystem.main()
# end main
