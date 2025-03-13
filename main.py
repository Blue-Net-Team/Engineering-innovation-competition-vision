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
import argparse

import cv2
from colorama import Fore, init

import Solution
from utils import SendImg, Cap, Switch, LED, OLED_I2C, connect_to_wifi, get_CPU_temp, get_GPU_temp
from utils.ImgTrans import NeedReConnect
from utils.logger import printLog

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
        deal_img_method: str = "hide",
        config_path: str = "config.json",
    ) -> None:
        """
        主系统
        ----
        Args:
            ser_port (str): 串口号
            pkgHEAD (str): 包头
            pgkTAIL (str): 包尾
            sender (SendImg): 图传发送器
            deal_img_method (str): 处理图像的方法,包含"show"(显示)、"hide"(隐藏)、"send"(发送)
            config_path (str): 配置文件路径
        """
        self.cap = Cap()
        self.solution = Solution.Solution(ser_port, config_path)
        self.switch = Switch("GPIO3-A3", True)
        self.start_LED = LED("GPIO3-A2")
        self.detecting_LED = LED("GPIO3-A4")
        self.oled = OLED_I2C(2,0x3c)
        self.sender = sender
        self.HEAD = pkgHEAD
        self.TAIL = pgkTAIL
        self.DEAL_IMG_DICT = {"show": Solution.show, "hide": lambda x: None}
        if self.sender and self.switch.read_status():
            self.DEAL_IMG_DICT["send"] = self.sender.send
            if self.sender.host == "":
                printLog(
                    Fore.RED + "未连接到图传网络,尝试连接" + Fore.RESET
                )

                self.oled.clear()
                self.oled.text("未连接到图传网络\n尝试连接...", (1,1))
                self.oled.display()

                while self.sender.host == "":
                    conn_res = connect_to_wifi("EIC-FF", "lckfb666")
                    if conn_res[0]:
                        printLog(
                            Fore.GREEN + "连接成功" + Fore.RESET
                        )

                        self.oled.clear()
                        self.oled.text("连接成功", (1,1))
                        self.oled.display()

                        # 更新host
                        self.sender.update_host()
                        break
                    else:
                        printLog(
                            Fore.RED + f"连接失败，{conn_res[1]}" + Fore.RESET
                        )

                        self.oled.clear()
                        self.oled.text(f"连接失败\n{conn_res[1]}", (1,1))
                        self.oled.display()
                        if not self.switch.read_status():
                            break
                        else:
                            time.sleep(0.5)

        self.TASK_DICT = {
            "1": self.solution.material_moving_detect,  # 物料运动检测
            "2": self.solution.get_material,  # 获取物料位号
            "3": self.solution.right_angle_detect,  # 直角检测
            "4": self.solution.annulus_top,  # 圆环检测
        }

        self.deal_img_method = deal_img_method
        printLog(
            Fore.WHITE + "deal_img_method为" + Fore.RESET +
            Fore.CYAN + deal_img_method + Fore.RESET
        )

        # 先读取20帧，打开摄像头
        for i in range(20):
            tmp_img = self.cap.read()[1]
            self.DEAL_IMG_DICT["hide"](tmp_img)

    def main(self):
        """
        主函数
        ----
        """
        self.start_LED.on()
        while True:
            switch_status = self.switch.read_status()

            if switch_status:
                # 开关状态1，开图传，关任务
                printLog(
                    Fore.WHITE + "模式切换为" + Fore.RESET +
                    Fore.CYAN + "图传" + Fore.RESET
                )

                # 检查sender
                if self.sender is None:
                    printLog(Fore.RED + "没有设置图传发送器对象" + Fore.RESET)
                    break

                # 检查wlan
                if self.sender.host == "":
                    printLog(
                        Fore.RED + "未连接到图传网络,尝试连接" + Fore.RESET
                    )

                    self.oled.clear()
                    self.oled.text("未连接到图传网络\n尝试连接...", (1, 1))
                    self.oled.display()

                    while True:
                        conn_res = connect_to_wifi("EIC-FF", "lckfb666")
                        if conn_res[0]:
                            printLog(
                                Fore.GREEN + "连接成功" + Fore.RESET
                            )

                            self.oled.clear()
                            self.oled.text("连接成功", (1, 1))
                            self.oled.display()

                            # 更新host
                            self.sender.update_host()
                            break
                        else:
                            printLog(
                                Fore.RED + f"连接失败，{conn_res[1]}" + Fore.RESET
                            )

                            self.oled.clear()
                            self.oled.text(f"连接失败\n{conn_res[1]}", (1, 1))
                            self.oled.display()
                            if not self.switch.read_status():
                                break
                            else:
                                time.sleep(0.5)
                if not self.switch.read_status():
                    continue

                # 设置标志
                self.ori_imgTrans_running_flag = True
                self.task_running_flag = False

                # 等待连接
                printLog(
                    Fore.WHITE + "等待图传连接\tIP:" + Fore.RESET +
                    Fore.CYAN + f"{self.sender.host}" + Fore.RESET,)

                self.oled.clear()
                self.oled.text(f"图传模式\n等待图传连接\nIP:{self.sender.host}", (1,1))
                self.oled.display()

                while self.ori_imgTrans_running_flag:
                    if self.sender.connecting():
                        break
                    if not self.switch.read_status():
                        # 开关状态2，关闭图传
                        self.ori_imgTrans_running_flag = False
                        break

                if not self.ori_imgTrans_running_flag:
                    continue

                printLog(Fore.WHITE + "图传连接成功" + Fore.RESET)


                self.oled.clear()
                self.oled.text("图传连接成功", (1,1))
                self.oled.display()

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
                        self.sender.close()
                        printLog(Fore.RED + "图传连接中断" + Fore.RESET)

                        self.oled.clear()
                        self.oled.text("图传连接中断", (1,1))
                        self.oled.display()

                        # 检查开关
                        if not self.switch.read_status():
                            # 开关状态2，关闭图传
                            self.ori_imgTrans_running_flag = False
                            break
                        else:
                            printLog(Fore.WHITE + "重新连接" + Fore.RESET)

                            self.oled.clear()
                            self.oled.text("等待重连", (1,1))
                            self.oled.display()

                            while self.ori_imgTrans_running_flag:
                                if not self.switch.read_status():
                                    # 开关状态2，关闭图传
                                    self.ori_imgTrans_running_flag = False
                                    break
                                if self.sender.connecting():
                                    printLog(Fore.WHITE + "图传连接成功" + Fore.RESET,)
                                    self.oled.clear()
                                    self.oled.text("图传连接成功", (1,1))
                                    self.oled.display()
                                    break

                    # 检查开关
                    if not self.switch.read_status():
                        # 开关状态2，关闭图传
                        self.ori_imgTrans_running_flag = False
                        break

            else:
                # 开关状态2，开任务线程，关图传线程
                printLog(Fore.WHITE + "模式切换为" + Fore.RESET +
                                  Fore.CYAN + "任务模式" + Fore.RESET)

                self.oled.clear()
                if self.deal_img_method == "send" and self.sender:
                    extension_txt = f"等待图传连接\nIP:{self.sender.host}"
                else:
                    extension_txt = ""
                self.oled.text(f"任务模式\n{extension_txt}", (1,1))
                self.oled.display()

                # 设置标志
                self.ori_imgTrans_running_flag = False
                self.task_running_flag = True

                # 加载参数
                self.solution.load_config()

                # 连接图传
                if self.deal_img_method == "send" and self.sender:
                    printLog(Fore.WHITE + "等待图传连接\tIP:" + Fore.RESET +
                                    Fore.CYAN + f"{self.sender.host}" + Fore.RESET)

                    while self.task_running_flag:
                        if self.sender.connecting():
                            printLog(Fore.WHITE + "图传连接成功" + Fore.RESET,)

                            self.oled.clear()
                            self.oled.text("图传连接成功", (1,1))
                            self.oled.display()

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
                        printLog(Fore.RED + f"非法信号 {sign}" + Fore.RESET)

                        self.oled.clear()
                        self.oled.text(f"非法信号 {sign}", (1,1))
                        self.oled.display()

                        # 检查开关
                        if self.switch.read_status():
                            self.task_running_flag = False
                            break
                        else:
                            continue

                    # 执行任务
                    self.detecting_LED.on()
                    self.oled.clear()
                    self.oled.text(f"收到信号{sign}", (1,1))
                    self.oled.display()
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

                        printLog(
                            Fore.WHITE + "result:" + Fore.RESET +
                            Fore.MAGENTA + f"{res}" + Fore.RESET
                        )

                        try:
                            self.DEAL_IMG_DICT[self.deal_img_method](res_img)
                        except Exception as e:
                            printLog(Fore.RED + f"图像处理失败:{e}" + Fore.RESET, Fore.RED)

                        if res:
                            t1 = time.perf_counter()
                            used_time_ms = (t1 - t0) * 1000
                            if used_time_ms < 40:
                                color = Fore.GREEN
                            elif used_time_ms < 60:
                                color = Fore.YELLOW
                            else:
                                color = Fore.RED

                            printLog(
                                Fore.WHITE + "sent:" + Fore.RESET +
                                Fore.MAGENTA + f"{res}\t" + Fore.RESET +
                                Fore.WHITE + "used time:" + Fore.RESET +
                                color + f"{used_time_ms:.2f}ms" + Fore.RESET
                            )
                            self.solution.uart.write(res)

                            self.detecting_LED.off()
                            break

                        # 每30帧检查一次开关
                        if num % 30 == 0:
                            # 检查核心温度
                            temp_cup = get_CPU_temp()
                            temp_gpu = get_GPU_temp()
                            self.oled.text(f"CPU温度:{temp_cup}\nGPU温度:{temp_gpu}", (1,30))
                            self.oled.display()
                            if not self.switch.read_status():
                                self.task_running_flag = False
                                break
        self.start_LED.off()


if __name__ == "__main__":
    # region 获取命令行参数deal_method
    parser = argparse.ArgumentParser(description="MainSystem")
    parser.add_argument(
        "-d", "--deal_method",
        type=str,
        default="send",
        help="处理图像的方法,包含show(显示)、hide(隐藏)、send(发送)",
    )
    parser.add_argument(
        "-c", "--config_path",
        type=str,
        default="config.json",
        help="配置文件路径",
    )
    parser.add_argument(
        "-i", "--interface",
        type=str,
        default="wlan0",
        help="图传发送器的网络接口",
    )
    args = parser.parse_args()
    deal_method = args.deal_method
    config_path = args.config_path
    interface = args.interface
    # endregion

    # 设置图传发送器
    sender = SendImg(interface, 4444)

    mainsystem = MainSystem(
        ser_port="/dev/ttyS3",
        pkgHEAD="@",
        pgkTAIL="#",
        sender=sender,
        deal_img_method=deal_method,
        config_path=config_path,
    )

    try:
        mainsystem.main()
    except KeyboardInterrupt:
        printLog(Fore.RED + "程序被中断（用户终止）" + Fore.RESET)
        mainsystem.start_LED.off()
# end main
