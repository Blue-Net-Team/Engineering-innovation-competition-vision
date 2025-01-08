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
import threading
import cv2
import Solution
from utils import SendImg, Cap
from utils import Switch
import numpy as np

from utils.ImgTrans import NeedReConnect

class MainSystem:

    sending_flag = False

    def __init__(
        self,
        ser_port: str,
        sender: SendImg | None=None
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
                if not self.sending_flag:   # 如果线程未启动
                    print("Start sending image")
                    self.sending_flag = True
                    img_sending_thread = threading.Thread(target=self.__send_ori_img)
                    img_sending_thread.start()
            else:
                if self.sending_flag:       # 如果线程已启动
                    print("Stop sending image")
                    self.sending_flag = False
                    img_sending_thread.join()

    def __send_ori_img(self):
        """
        发送原始图像
        ----
        """
        if self.sender:
            while self.sending_flag:
                if self.sender.connecting():
                    break
            while self.sending_flag:
                try:
                    self.sender.send(self.img)
                except NeedReConnect:
                    while self.sending_flag:
                        if self.sender.connecting():
                            break

    def __read_img(self):
        """
        读取图像
        ----
        """
        while True:
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