import threading
import RPi.GPIO as GPIO
import time


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

class ToggleSwitch(Switch):
    """线程切换开关类"""

    def __init__(self, _InPin: int, pull_up_down: int = 22, _PowPin: int | None = None) -> None:
        super().__init__(_InPin, pull_up_down, _PowPin)
        self.current_thread = None
        self.thread1 = threading.Thread(target=self.thread1_function)
        self.thread2 = threading.Thread(target=self.thread2_function)
        self.button_press_count = 0

    def thread1_function(self) -> None:
        """线程1的执行函数"""
        print("Thread 1 is running")

    def thread2_function(self) -> None:
        """线程2的执行函数"""
        print("Thread 2 is running")

    def switch_threads(self) -> None:
        """切换线程"""
        self.button_press_count += 1
        if self.button_press_count % 2 == 1:
            if self.current_thread == self.thread2:
                self.current_thread.join()
            self.current_thread = self.thread1
            self.thread1.start()
        else:
            if self.current_thread == self.thread1:
                self.current_thread.join()
            self.current_thread = self.thread2
            self.thread2.start()

    def read_statusAlway(self) -> None:
        """一直读取开关状态，并在状态变化时切换线程"""
        while self.readFlag:
            current_status = GPIO.input(self.InPin)
            if current_status != self.status:
                self.status = current_status
                if self.status:
                    self.switch_threads()
            time.sleep(0.1)

class ToggleStateSwitch(Switch):
    """状态切换开关类"""

    def __init__(self, _InPin: int, pull_up_down: int = 22, _PowPin: int | None = None) -> None:
        super().__init__(_InPin, pull_up_down, _PowPin)
        self.current_state = 0
        self.last_button_status = False
        self.button_press_count = 0

    def switch_state(self) -> None:
        """切换状态"""
        self.button_press_count += 1
        if self.button_press_count % 2 == 1:
            self.current_state = 1
            print("Switched to State 1")
        else:
            self.current_state = 2
            print("Switched to State 2")

    def read_statusAlway(self) -> None:
        """一直读取开关状态，并在状态变化时切换状态"""
        while self.readFlag:
            current_status = GPIO.input(self.InPin)
            if current_status != self.last_button_status and current_status:
                self.last_button_status = current_status
                self.switch_state()
            elif current_status == 0:
                self.last_button_status = current_status
            time.sleep(0.1)


