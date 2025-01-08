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
from typing import Union, overload
from utils.typingCheck import check_args
import serial


class Uart(serial.Serial):
    """
    串口通信类
    ----
    * 继承了serial.Serial类，实现了使用包头包尾接受数据的方法
    * 发送数据的时候可以指定包头包尾
    """

    def __init__(self, port:str|None, baudrate:int=115200, timeout:float|None=None):
        """
        初始化串口通信对象
        ----
        Args:
            port (str): 串口端口
            baudrate (int): 波特率，默认9600
            timeout (float): 超时时间，默认无
        """
        super().__init__(port=port, baudrate=baudrate, timeout=timeout)

    def read(self, head: str, tail: str = "\n") -> str:
        """
        读取数据
        ----
        Args:
            head (str): 包头
            tail (str): 包尾，默认为换行符
        Returns:
            result (str): 去掉包尾的数据字符串
        """
        if self.is_open:
            self.clear()
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
        else:
            return ""

    @overload
    def write(self, data: str, head: str = "", tail: str = "") -> None: ...
    @overload
    def write(self, data:int, head: bytes = b"", tail: bytes = b"") -> None: ...
    @overload
    def write(self, data: list[int], head: bytes = b"", tail: bytes = b"") -> None: ...

    def write(
        self,
        data: Union[str, int, list[int]],
        head: Union[str, bytes] = "",
        tail: Union[str, bytes] = ""
    ):
        """
        发送数据
        ----
        Args:
            data (Union[str, int, list[int]]): 要发送的数据
            head (Union[str, bytes]): 包头，默认为空字符串或空字节串
            tail (Union[str, bytes]): 包尾，默认为空字符串或空字节串
        """
        if check_args(
            (data, str),
            (head, str),
            (tail, str)
        )[0]:
            super().write((head + data + tail).encode("ascii"))

        elif check_args(
            (data, int),
            (head, bytes),
            (tail, bytes)
        )[0]:
            data_bytes = data.to_bytes(4, byteorder="big", signed=True)
            super().write(head + data_bytes + tail)

        elif check_args(
            (data, list[int]),
            (head, bytes),
            (tail, bytes)
        )[0]:
            data_bytes = b""
            for item in data:
                data_bytes += item.to_bytes(4, byteorder="big", signed=True)
            super().write(head + data_bytes + tail)

        else:
            raise TypeError("Invalid data type")


    def clear(self):
        """
        清除缓存区
        """
        super().reset_input_buffer()
        super().reset_output_buffer()
