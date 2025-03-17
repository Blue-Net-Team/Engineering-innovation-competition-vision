r"""
远程图传
====
该模块包含两个类：

`VideoStreaming`:
----
视频流传输类(服务端)

方法:
    - `__init__(self, host, port)`: 初始化，设置主机IP地址和端口号
    - `connecting(self)`: 连接客户端
    - `start(self)`: 开始传输视频流
    - `send(self, _img: cv2.typing.MatLike) -> bool`: 发送图像数据

`ReceiveImg`:
----
接收视频流类(客户端)

方法:
    - `__init__(self, host, port)`: 初始化，设置主机IP地址和端口号
    - `read(self)`: 读取图像数据

注意:
----
服务端不能主动向客户端发送数据，只能等待客户端连接后发送数据
"""
import io
import socket
import struct
import cv2
import numpy as np
from colorama import Fore, Style, init
# import fcntl

from .logger import printLog

init(autoreset=True)

class NeedReConnect(Exception):
    """需要重新连接"""
    pass

class SendImg(object):
    """服务端视频发送"""
    _host:str = ""
    _interface:str = ""

    @property
    def host(self):
        return self._host

    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, value:str):
        self._interface = value
        self._host = self.get_ip_address(value)

    def __init__(self, interface:str, port:int=4444):
        """初始化
        ----
        Args:
            host (str): 主机IP地址
            port (int): 端口号
        """
        self.is_open = False
        self.interface = interface
        self.port = port
        self.host_name = ""
        self.client_address = ""

        self.open_socket()

    def open_socket(self):
        if self.host and self.port:
            try:
                self.server_socket = socket.socket()
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen(5)
                self.server_socket.settimeout(0.05)
                self.connection = None
                self.connect = None
                self.stream = io.BytesIO()
                self.is_open = True
            except Exception as e:
                printLog(Fore.RED + f"Error: {e}", Fore.RED)

    @staticmethod
    def get_ip_address(interface: str) -> str:
        """
        获取IP地址
        ----
        用于树莓派获取IP地址

        Args:
            interface (str): 网卡名称，lo为本地回环网卡，eth0为以太网网卡等
        Returns:
            ip (str): IP地址
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', interface[:15].encode('utf-8'))
            )[20:24])
        except:
            return ""

    def update_host(self):
        self._host = self.get_ip_address(self.interface)

    def connecting(self):
        """
        连接客户端
        ----
        """
        def _connect(self):
            try:
                self.connection, self.client_address = self.server_socket.accept()
                self.connect = self.connection.makefile("wb")
                self.host_name = socket.gethostname()
                self.host_ip = socket.gethostbyname(self.host_name)

                return True
            except socket.timeout:
                return False
        if self.is_open:
            return _connect(self)
        else:
            # 重新初始化
            self.open_socket()
            return _connect(self)

    def start(self) -> None:
        """
        开始传输视频流
        ----
        运行这个函数之前，必须先运行`connecting`函数
        """
        printLog("Client Host Name:", self.host_name)
        printLog("Connection from: ", self.client_address)
        printLog("Streaming...")

    def send(self, _img: cv2.typing.MatLike) -> bool:
        """
        发送图像数据
        ----
        运行这个函数之前，必须运行`connecting`函数

        Args:
            _img (cv2.typing.MatLike): 图像数据
        Returns:
            res (bool): 发送是否成功
        """
        if self.is_open:
            try:
                if self.connect is None:
                    raise ConnectionError("未连接到客户端")

                img_encode = cv2.imencode(".jpg", _img, [int(cv2.IMWRITE_JPEG_QUALITY), 70])[1]
                data_encode = np.array(img_encode)
                self.stream.write(data_encode) # type: ignore
                self.connect.write(struct.pack("<L", self.stream.tell()))
                self.connect.flush()
                self.stream.seek(0)
                self.connect.write(self.stream.read())
                self.stream.seek(0)
                self.stream.truncate()
                self.connect.write(struct.pack("<L", 0))
                return True
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
                printLog(Fore.RED + f"Connection error: {e}", Fore.RED)
                self.close()
                raise NeedReConnect("连接已断开，请重新连接")
            except OSError as e:
                printLog(Fore.RED + f"OS error: {e}", Fore.RED)
                self.close()
                raise NeedReConnect("连接已断开，请重新连接")
        else:
            return False

    def close(self):
        """关闭连接"""
        if self.is_open:
            if self.connect:
                try:
                    self.connect.close()
                except OSError as e:
                    printLog(Fore.RED + f"Error closing connect: {e}", Fore.RED)
            if self.connection:
                try:
                    self.connection.close()
                except OSError as e:
                    printLog(Fore.RED + f"Error closing connection: {e}", Fore.RED)
            if self.server_socket:
                try:
                    self.server_socket.close()
                except OSError as e:
                    printLog(Fore.RED + f"Error closing server_socket: {e}", Fore.RED)
            self.is_open = False

class ReceiveImg(object):
    """客户端接收视频流"""

    def __init__(self, host, port):
        """初始化"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.connection = self.client_socket.makefile("rb")
            self.stream_bytes = b" "

            printLog("已连接到服务端：")
            printLog(f"Host : {host}" )
            printLog("请按‘q’退出图像传输!")
        except Exception as e:
            printLog(Fore.RED + f"Error: {e}", Fore.RED)
            exit()

    def read(self):
        """读取图像数据"""
        try:
            msg = self.connection.read(4096)
            self.stream_bytes += msg
            first = self.stream_bytes.find(b"\xff\xd8")
            last = self.stream_bytes.find(b"\xff\xd9")

            if first != -1 and last != -1:
                jpg = self.stream_bytes[first : last + 2]
                self.stream_bytes = self.stream_bytes[last + 2 :]
                image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                return True, image

        except:
            printLog("Error：连接出错！")
        return False, None

    def release(self):
        """释放资源"""
        self.connection.close()
        self.client_socket.close()


class LoadWebCam:
    """读取远程图传的迭代器"""
    def __init__(self, ip:str, port:int):
        """
        初始化
        ----
        Args:
            ip (str): 服务端IP地址
            port (int): 端口号
        """
        self.streaming = ReceiveImg(ip, port)

    def __iter__(self):
        return self

    def __next__(self):
        _, img = self.streaming.read()
        return img

    def release(self):
        """释放资源"""
        self.streaming.connection.close()
        self.streaming.client_socket.close()
