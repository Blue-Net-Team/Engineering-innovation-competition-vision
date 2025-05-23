r"""
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
import numpy as np

import Solution
from ImgTrans import SendImg, SendImgTCP, SendImgUDP
from utils import Cap, Switch, LED, OLED_I2C, connect_to_wifi, get_CPU_temp, get_GPU_temp, printLog
from ImgTrans.ImgTrans import NeedReConnect
from utils.UART import Uart

init(autoreset=True)

class MainSystem:
    """
    主任务系统
    """
    ori_imgTrans_running_flag = False  # 原始图像是否正在传输
    task_running_flag = False  # 任务是否正在运行
    read_empty_frame_num:int = 0  # 读取空帧的次数
    missed_frames:int = 0  # 没有识别到图像的帧数


    def __init__(
        self,
        ser_port: str,
        pkgHEAD:str,
        pgkTAIL:str,
        sender_debug: SendImg | None = None,
        config_path: str = "config.yaml",
    ) -> None:
        """
        主系统
        ----
        Args:
            ser_port (str): 串口号
            pkgHEAD (str): 包头
            pgkTAIL (str): 包尾
            sender_debug (SendImg): 调试图传发送器
            config_path (str): 配置文件路径
        """
        self.solution = Solution.Solution(ser_port, config_path)
        self.shower = Uart("/dev/ttyUSB0", 115200)
        self.cap = Cap()
        self.switch = Switch("GPIO3-A3", True)
        self.start_LED = LED("GPIO3-A2")
        self.detecting_LED = LED("GPIO3-A4")
        self.oled = OLED_I2C(2,0x3c)
        self.sender_debug = sender_debug
        self.HEAD = pkgHEAD
        self.TAIL = pgkTAIL
        self.DEAL_IMG_DICT = {"hide": lambda x: None}

        self.TASK_DICT = {
            "1": self.solution.material_moving_detect,  # 物料运动检测
            "2": self.solution.get_material,  # 获取物料位号
            "3": self.solution.right_angle_detect,  # 直角检测
            "4": self.solution.annulus_top,  # 圆环检测
            "5": self.clear_img_buffer,  # 清空缓冲区
            None: lambda x: tuple(["1",cv2.putText(
                                    np.zeros((240, 320, 3), dtype=np.uint8),
                                    "no any sign",
                                    (20, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1,
                                    (0, 0, 255),
                                    2
                                )])
        }

        # 先读取20帧，打开摄像头
        for i in range(20):
            tmp_img = self.cap.read()[1]
            self.DEAL_IMG_DICT["hide"](tmp_img)

    def checkWlan(self):
        """
        检查wlan是否连接
        """
        if self.sender_debug.host == "":
            printLog(
                Fore.RED + "未连接到图传网络,尝试连接" + Fore.RESET
            )

            self.oled.clear()
            self.oled.text("未连接到图传网络\n尝试连接...", (1, 1))
            self.oled.display()

            while self.sender_debug.host == "":
                conn_res = connect_to_wifi("EIC-FF", "lckfb666")
                if conn_res[0]:
                    printLog(
                        Fore.GREEN + "连接成功" + Fore.RESET
                    )

                    self.oled.clear()
                    self.oled.text("连接成功", (1, 1))
                    self.oled.display()

                    # 更新host
                    self.sender_debug.update_host()
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

    def main(self):
        """
        主函数
        ----
        """
        self.start_LED.on()
        while True:
            switch_status = self.switch.read_status()

            if switch_status:
                # 切换到图传模式，终止记录
                # 更新配置
                self.updateConfig()

                # 开关状态1，开图传，关任务
                printLog(
                    Fore.WHITE + "模式切换为" + Fore.RESET +
                    Fore.CYAN + "图传" + Fore.RESET
                )

                # 检查sender
                if self.sender_debug is None:
                    printLog(Fore.RED + "没有设置图传发送器对象" + Fore.RESET)
                    break

                # 检查wlan
                self.checkWlan()
                if not self.switch.read_status():
                    # 切换模式，使用continue跳过本次循环
                    continue

                # 设置标志
                self.ori_imgTrans_running_flag = True
                self.task_running_flag = False

                # 等待tcp握手
                if isinstance(self.sender_debug, SendImgTCP):
                    # region 等待连接
                    printLog(
                        Fore.WHITE + "等待TCP连接\tIP:" + Fore.RESET +
                        Fore.CYAN + f"{self.sender_debug.host}" + Fore.RESET, )
                    self.oled.clear()
                    self.oled.text(f"TCP图传模式\n等待图传连接\nIP:{self.sender_debug.host}", (1, 1))
                    self.oled.display()
                    while self.ori_imgTrans_running_flag:
                        if self.sender_debug.connecting():
                            break
                        if not self.switch.read_status():
                            # 开关状态2，关闭图传
                            self.ori_imgTrans_running_flag = False
                            break

                    if not self.ori_imgTrans_running_flag:
                        continue

                    printLog(Fore.WHITE + "TCP图传连接成功" + Fore.RESET)


                    self.oled.clear()
                    self.oled.text("TCP图传连接成功", (1,1))
                    self.oled.display()
                    # endregion
                # udp直接发送，不等待连接
                elif isinstance(self.sender_debug, SendImgUDP):
                    self.oled.clear()
                    self.oled.text(f"UDP图传模式\nIP:{self.sender_debug.host}", (1, 1))
                    self.oled.display()
                else:
                    raise TypeError("不支持的图传发送器类型")

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
                        self.sender_debug.send(img)
                    # 只有tcp会跑出此异常
                    except NeedReConnect:
                        self.sender_debug.close()
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
                                if self.sender_debug.connecting():
                                    printLog(Fore.WHITE + "图传连接成功" + Fore.RESET,)
                                    self.oled.clear()
                                    self.oled.text("图传连接成功", (1,1))
                                    self.oled.display()
                                    break
                    except BlockingIOError as e:
                        printLog(Fore.RED + f"图传发送失败，稍后重试: {e}" + Fore.RESET)
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

                self.oled.text(f"任务模式", (1,1))
                self.oled.display()

                # 设置标志
                self.ori_imgTrans_running_flag = False
                self.task_running_flag = True

                # 加载参数
                self.updateConfig()

                # 开始任务
                while self.task_running_flag:
                    # 读取空帧的次数
                    self.read_empty_frame_num = 0
                    # 丢图数置零
                    self.missed_frames = 0
                    # 读取串口信号
                    sign = self.solution.uart.new_read(self.HEAD, self.TAIL)

                    if sign is not None and "+" in sign:
                        tasks = sign.split("+")
                        need2write = f"({tasks[0]}{tasks[1]})"
                        self.shower.write(need2write)
                    else:
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
                        if sign is not None:
                            printLog(Fore.WHITE + f"收到信号 {sign}" + Fore.RESET)
                            self.detecting_LED.on()

                        if sign == "1":
                            self.solution.position_id_stack = []

                        t0 = time.perf_counter()

                        while self.task_running_flag:
                            _, img = self.cap.read()

                            if img is None:
                                continue

                            res, res_img = self.TASK_DICT[sign](img)

                            if sign is None:
                                if self.switch.read_status():
                                    self.task_running_flag = False
                                break

                            # 如果有识别结果
                            if res:
                                # 计算丢图率
                                miss_present = self.missed_frames / (self.missed_frames + 1)
                                t1 = time.perf_counter()
                                used_time_ms = (t1 - t0) * 1000
                                if used_time_ms < 40:
                                    color = Fore.GREEN
                                elif used_time_ms < 60:
                                    color = Fore.YELLOW
                                else:
                                    color = Fore.RED

                                if miss_present < 0.20:
                                    loss_color = Fore.GREEN
                                elif miss_present < 0.60:
                                    loss_color = Fore.YELLOW
                                else:
                                    loss_color = Fore.RED

                                # 打印定位信息
                                if res[0] == "L" and res[-1] == "E":
                                    printLog(
                                        Fore.WHITE + "res:" + Fore.RESET +
                                        Fore.WHITE + "角度:" + Fore.RESET +
                                        Fore.GREEN + f"{'+' if res[1]=='1' else '-'}{res[2:4]}.{res[4]}\t" + Fore.RESET +
                                        Fore.WHITE + f"X:" + Fore.RESET +
                                        Fore.GREEN + f"{res[5:8]}\t" + Fore.RESET +
                                        Fore.WHITE + "Y:" + Fore.RESET +
                                        Fore.GREEN + f"{res[8:11]}\t" + Fore.RESET +
                                        Fore.WHITE + "used time:" + Fore.RESET +
                                        color + f"{used_time_ms:.2f}ms\t" + Fore.RESET +
                                        Fore.WHITE + "loss:" + Fore.RESET +
                                        loss_color + f"{miss_present:.2%}" + Fore.RESET
                                    )
                                    oled_txt = f"角度：{'+' if res[1]=='1' else '-'}{res[2:4]}.{res[4]}\nX:{res[5:8]}  Y:{res[8:11]}"
                                # 打印物料位号
                                elif res[0] == "C" and res[-1] == "E":
                                    printLog(
                                        Fore.WHITE + "res:" + Fore.RESET +
                                        Fore.RED + res[1] + "\t" + Fore.RESET +
                                        Fore.GREEN + res[2] + "\t" + Fore.RESET +
                                        Fore.BLUE + res[3] + "\t" + Fore.RESET +
                                        Fore.WHITE + "used time:" + Fore.RESET +
                                        color + f"{used_time_ms:.2f}ms\t" + Fore.RESET +
                                        Fore.WHITE + "loss:" + Fore.RESET +
                                        loss_color + f"{miss_present:.2%}" + Fore.RESET
                                    )
                                    oled_txt = f"物料位号：R{res[1]} G{res[2]} B{res[3]}"
                                # 其他情况直接打印res
                                else:
                                    printLog(
                                        Fore.WHITE + "res:" + Fore.RESET +
                                        Fore.MAGENTA + f"{res}\t" + Fore.RESET +
                                        Fore.WHITE + "used time:" + Fore.RESET +
                                        color + f"{used_time_ms:.2f}ms\t" + Fore.RESET +
                                        Fore.WHITE + "loss:" + Fore.RESET +
                                        loss_color + f"{miss_present:.2%}" + Fore.RESET
                                    )
                                    oled_txt = f"res:{res}"

                                self.oled.clear()
                                self.oled.text(f"收到信号{sign}\n{oled_txt}", (1, 1))
                                self.oled.display()
                                # 清空缓冲区的时候结果为1，这个结果不发送
                                if res != "1":
                                    self.solution.uart.write(res)

                                # 关闭识别指示灯
                                self.detecting_LED.off()
                                break
                            else:
                                self.missed_frames += 1


        self.start_LED.off()


    def updateConfig(self):
        """
        更新配置，此方法会更新图传发送器的ip和摄像头底部裁剪的高度
        """
        self.solution.load_config()
        # 更新裁剪参数
        self.cap.NEED2CUT = self.solution.NEED2CUT
        # 更新客户端ip
        if isinstance(self.sender_debug, SendImgUDP):
            self.sender_debug.clients_ip = self.solution.clientsIp_debug

    def clear_img_buffer(self, img:cv2.typing.MatLike):
        """
        去除缓冲区图像
        ----
        Args:
            img (cv2.typing.MatLike): 图像数据
        Returns:
            res (str): 返回值，完成清除缓冲区操作的信号
            img (cv2.typing.MatLike): 图像数据，读出来的图像数据
        """
        cv2.putText(
            img,
            "Cleaning Buffer...",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
        )
        res = None
        self.read_empty_frame_num += 1
        if self.read_empty_frame_num > 30:
            res = "1"
        return res, img


if __name__ == "__main__":
    # region 获取命令行参数deal_method
    parser = argparse.ArgumentParser(description="MainSystem")
    parser.add_argument(
        "-c", "--config_path",
        type=str,
        default="config.yaml",
        help="配置文件路径",
    )
    args = parser.parse_args()
    config_path = args.config_path
    # endregion

    # 设置图传发送器
    sender_wired = SendImgUDP("eth0", 4444)

    mainsystem = MainSystem(
        ser_port="/dev/ttyS3",
        pkgHEAD="@",
        pgkTAIL="#",
        sender_debug=sender_wired,
        config_path=config_path,
    )

    try:
        mainsystem.main()
    except KeyboardInterrupt:
        printLog(Fore.RED + "程序被中断（用户终止）" + Fore.RESET)
        mainsystem.start_LED.off()
# end main
