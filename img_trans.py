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


class VideoStreaming(object):
    """服务端视频发送"""

    def __init__(self, host, port):
        """初始化
        ----
        Args:
            host (str): 主机IP地址
            port (int): 端口号
        """
        self.server_socket = socket.socket()  # 获取socket.socket()实例
        self.server_socket.bind((host, port))  # 绑定主机IP地址和端口号
        self.server_socket.listen(5)  # 设置监听数量

    def connecting(self):
        """连接客户端"""
        print("等待连接")
        self.connection, self.client_address = (
            self.server_socket.accept()
        )  # 等待Client连接，返回实例和IP地址
        self.connect = self.connection.makefile(
            "wb"
        )  # 创建一个传输文件 写功能 写入数据时b''二进制类型数据
        self.host_name = socket.gethostname()  # 获得服务端主机名
        self.host_ip = socket.gethostbyname(self.host_name)  # 获得服务端主机IP地址
        print("连接成功")

    def start(self) -> None:
        """
        开始传输视频流
        ----
        调用之前必须先调用`connecting`方法
        """
        print("Client Host Name:", self.host_name)
        print("Connection from: ", self.client_address)
        print("Streaming...")
        self.stream = io.BytesIO()  # 创建一个io流，用于存放二进制数据

    def send(self, _img: cv2.typing.MatLike) -> bool:
        """
        发送图像数据
        ----
        调用之前必须先调用`start`方法
        
        Args:
            _img (cv2.typing.MatLike): 图像数据
        Returns:
            bool: 发送是否成功
        """
        try:
            try:
                img_encode = cv2.imencode(".jpg", _img)[1]  # 编码
            except:
                print("没有读取到图像")
                return False
            data_encode = np.array(img_encode)  # 将编码数据转换成二进制数据
            self.stream.write(data_encode)  # 将二进制数据存放到io流
            self.connect.write(
                struct.pack("<L", self.stream.tell())
            )  # struct.pack()将数据转换成什么格式    stream.tell()获得目前指针的位置，将数据写入io流后，数据指针跟着后移，
            # 也就是将数据长度转换成'<L'类型（无符号长整型），写入makefile传输文件
            # 它的作用相当于 帧头数据，单独收到这个数据表示开始传输一帧图片数据，因为图片大小确定，这个数也就定下不变
            self.connect.flush()  # 刷新，将数据长度发送出去
            self.stream.seek(0)  # 更新io流，将指针指向0
            self.connect.write(
                self.stream.read()
            )  # 指针指向0后，从头开始读数据，然后写到makefile传输文件
            self.stream.seek(0)  # 更新指针
            self.stream.truncate()  # 更新io流数据，删除指针后面的数据

            self.connect.write(
                struct.pack("<L", 0)
            )  # 发送0，相当于帧尾数据，单独收到这个数表示一帧图片传输结束
            return True
        except ConnectionResetError:
            print("连接已重置")
            self.connecting()
            return False


class ReceiveImg(object):
    """客户端接收视频流"""
    def __init__(self, host, port):
        """
        初始化
        ----
        Args:
            host (str): 主机IP地址
            port (int): 端口号
        """
        self.client_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )  # 设置创建socket服务的Client客服务的参数
        self.client_socket.connect((host, port))  # 连接的主机IP地址和端口
        self.connection = self.client_socket.makefile(
            "rb"
        )  # 创建一个makefile传输文件，读功能，读数据是b''二进制类型
        # need bytes here
        self.stream_bytes = b" "  # 创建一个变量，存放的数据类型是b''二进制类型数据

        print(" ")
        print("已连接到服务端：")
        print("Host : ", host)
        print("请按‘q’退出图像传输!")

    def read(self):
        """
        读取图像数据
        ----
        读取前必须先启动服务端
        
        Returns:
            bool: 读取是否成功
            np.ndarray: 图像数据
        """
        try:
            msg = self.connection.read(1024)  # 读makefile传输文件，一次读1024个字节
            self.stream_bytes += msg
            first = self.stream_bytes.find(b"\xff\xd8")  # 检测帧头位置
            last = self.stream_bytes.find(b"\xff\xd9")  # 检测帧尾位置

            if first != -1 and last != -1:
                jpg = self.stream_bytes[
                    first : last + 2
                ]  # 帧头和帧尾中间的数据就是二进制图片数据（编码后的二进制图片数据，需要解码后使用）
                self.stream_bytes = self.stream_bytes[
                    last + 2 :
                ]  # 更新stream_bytes数据
                image = cv2.imdecode(
                    np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR
                )  # 将二进制图片数据转换成numpy.uint8格式（也就是图片格式）数据，然后解码获得图片数据
                return True, image

        except:
            print("Error：连接出错！")
        return False, None


if __name__ == "__main__":
    stream = VideoStreaming("192.168.137.141", 8000)
    cap = cv2.VideoCapture(0)
    stream.connecting()
    stream.start()
    while True:
        img = cap.read()[1]
        stream.send(img)
