#!./.venv/Scripts/python.exe
# -*- coding: utf-8 -*-
r"""
* author: git config IVEN_CN && git config 13377529851@QQ.com
* Date: 2024-09-17 14:37:30 +0800
* LastEditTime: 2024-09-17 14:53:48 +0800
* FilePath: \工创2025\USART\communicate.py
* details: 通信文件，用于存放串口通信相关代码
* Copyright (c) 2024 by IVEN, All Rights Reserved. 
"""
import sys
sys.path.append("/usr/local/lib/python3.6/dist-packages")
print("add sys path /usr/local/lib/python3.6/dist-packages")
sys.path.append("/home/iven/.local/lib/python3.6/site-packages")
print("add sys path /home/iven/.local/lib/python3.6/site-packages")

import serial


class Usart(serial.Serial):
    """
    串口通信类
    ----
    * 继承了serial.Serial类，实现了使用包头包尾接受数据的方法
    * 发送数据的时候可以指定包头包尾
    """

    def __init__(self, port, baudrate=9600, timeout=None):
        super().__init__(port=port, baudrate=baudrate, timeout=timeout)

    def read(self, head: str, tail: str = "\n") -> str:
        """
        读取数据
        ----
        :param head: 包头
        :param tail: 包尾
        :return: 数据
        """
        HEAD, TAIL = head.encode("ascii"), tail.encode("ascii")
        data = b""
        while True:
            byte = super().read(1)
            if not byte:
                continue
            data += byte
            if data.endswith(HEAD):
                break

        # -----读到包头-----
        data = b""
        while True:
            byte = super().read(1)
            if not byte:
                continue
            data += byte
            if data.endswith(TAIL):
                return data[: -len(TAIL)].decode("ascii")  # 返回去掉包尾的数据

    def write(self, data: str, head: str = "", tail: str = ""):
        """
        发送数据
        ----
        :param data: 数据
        :param head: 包头
        :param tail: 包尾
        """
        HEAD, TAIL = head.encode("ascii"), tail.encode("ascii")
        super().write(HEAD + data.encode("ascii") + TAIL)

    def clear(self):
        """
        清除缓存区
        """
        super().reset_input_buffer()
        super().reset_output_buffer()
