import threading
import RPi.GPIO as GPIO

# 设置GPIO模式为BCM
GPIO.setmode(GPIO.BCM)

class Switch:
    """开关类"""

    status: bool = False
    readFlag: bool = True

    def __init__(self, _InPin:int, pull_up_down:int=22, _PowPin:int|None=None) -> None:
        """
        初始化开关
        ----
        Args:
            _InPin: 输入引脚，该类回读取这个引脚的电平作为开关状态
            pull_up_down: 上下拉电阻
            _PowPin: 电源引脚,设置了的话,将会在初始化时将其设置为高电平
        """
        self.InPin = _InPin
        self.PowPin = _PowPin

        # 设置输入引脚
        GPIO.setup(self.InPin, GPIO.IN, pull_up_down=pull_up_down)

        # 设置电源引脚
        if self.PowPin:
            GPIO.setup(self.PowPin, GPIO.OUT)
            GPIO.output(self.PowPin, GPIO.HIGH)

    def read_status(self) -> bool:
        """读取开关状态"""
        self.status = GPIO.input(self.InPin)
        return self.status

    def __read_statusAlway(self) -> None:
        """一直读取开关状态"""
        while self.readFlag:
            self.status = GPIO.input(self.InPin)

    def read_statusAlway(self) -> None:
        """一直读取开关状态"""
        self.t = threading.Thread(target=self.__read_statusAlway)
        self.t.start()

    def stop_read(self) -> None:
        """停止读取开关状态"""
        self.readFlag = False
        self.t.join()

    def __del__(self) -> None:
        """析构函数"""
        self.stop_read()
        GPIO.cleanup(self.InPin)
        if self.PowPin:
            GPIO.cleanup(self.PowPin)

class Toggleswitch(Switch):
    """可切换状态的开关类"""
    def __init__(self,_InPin:int, pull_up_down:int = GPIO.PUD_UP,_PowPin:int | None = None) -> None:
        """初始化开关"""
        super().__init__(_InPin,pull_up_down,_PowPin)
        self.toggle_state: int = 0

    def _read_statusAlway(self) -> None:
        """一直读取开关状态"""
        last_button_state = GPIO.input(self.InPin)
        while self.readFlag:
            current_button_state = GPIO.input(self.InPin)
            if current_button_state != last_button_state and current_button_state == GPIO.LOW:
               #检测按钮按下
              self.toggle_state = (self.toggle_state + 1) % 3
            print(f"Button pressed! Toggle state changed to {self.toggle_state}")
            last_button_state = current_button_state


    def get_toggle_state(self) -> int:
        """获取切换后的状态"""
        return self.toggle_state

