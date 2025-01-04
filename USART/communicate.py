r"""
该模块定义了一个用于串口通信的类 `Usart`，继承自 `serial.Serial` 类。

模块功能：
- 通过指定包头和包尾来接收数据
- 发送数据时可以指定包头和包尾
- 清除串口缓存区

Usart类
----
串口通信类，继承自 `serial.Serial`，提供了读取、发送和清除缓存区的方法。

方法：
- `__init__(self, port, baudrate=9600, timeout=None)`:
    初始化串口通信对象。

    参数:
        - `port`: 串口端口
        - `baudrate`: 波特率，默认9600
        - `timeout`: 超时时间，默认无
- `read(self, head: str, tail: str = "\n") -> str`:
    读取数据，直到遇到指定的包头和包尾。

    参数:
        - `head`: 包头
        - `tail`: 包尾，默认值为换行符
    返回:
        - 去掉包尾的数据字符串
- `write(self, data: str, head: str = "", tail: str = "")`:
    发送数据，附加指定的包头和包尾。

    参数:
        - `data`: 要发送的数据
        - `head`: 包头，默认值为空字符串
        - `tail`: 包尾，默认值为空字符串
- `clear(self)`: 清除串口的输入和输出缓存区。
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
    port: str|None = None

    def __init__(self, port, baudrate=9600, timeout=None):
        self.port = port
        if self.port:
            super().__init__(port=port, baudrate=baudrate, timeout=timeout)

    if port:
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
    else:
        def read(self, head: str, tail: str = "\n") -> str:
            return ""

        def write(self, data: str, head: str = "", tail: str = ""):
            pass

        def clear(self):
            pass