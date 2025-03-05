try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import sh1106
    from PIL import ImageFont, ImageDraw, Image

    def check_raspberry_pi():
        """检查是否为树莓派"""
        try:
            with open('/proc/device-tree/model', 'r') as file:
                model = file.read().strip()
                print(f"设备型号: {model}")
                if "Raspberry Pi" in model:
                    return True
                else:
                    return False
        except FileNotFoundError:
            print("无法访问设备树信息")
            return False
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return False

    if check_raspberry_pi():
        import RPi.GPIO as GPIO

        # 设置GPIO模式为BCM
        GPIO.setmode(GPIO.BCM)

        class LED:
            def __init__(self, _OutPin: str) -> None:
                """
                初始化LED
                ----
                Args:
                    _OutPin: 输出引脚(BCM编号)，该类会将这个引脚设置为输出模式
                """
                self.OutPin = int(_OutPin)
                GPIO.setup(self.OutPin, GPIO.OUT)

            def on(self):
                """开启LED"""
                GPIO.output(self.OutPin, GPIO.HIGH)

            def off(self):
                """关闭LED"""
                GPIO.output(self.OutPin, GPIO.LOW)

        class Switch:
            """开关类"""

            status: bool = False
            readFlag: bool = True

            def __init__(
                self,
                _InPin: str,
                pull_up_down: int = 22,
                _PowPin: int | None = None,
                reverse: bool = False
            ) -> None:
                """
                初始化开关
                ----
                Args:
                    _InPin: 输入引脚，该类回读取这个引脚的电平作为开关状态
                    pull_up_down: 上下拉电阻
                    _PowPin: 电源引脚,设置了的话,将会在初始化时将其设置为高电平
                    reverse: 是否反转开关状态
                """
                self.InPin = int(_InPin)
                self.PowPin = _PowPin
                self.reverse = reverse

                # 设置输入引脚
                GPIO.setup(self.InPin, GPIO.IN, pull_up_down=pull_up_down)

                # 设置电源引脚
                if self.PowPin:
                    GPIO.setup(self.PowPin, GPIO.OUT)
                    GPIO.output(self.PowPin, GPIO.HIGH)

            def read_status(self) -> bool:
                """
                读取开关状态
                ----
                Returns:
                    status: 开关状态
                """
                self.status = GPIO.input(self.InPin)
                return self.status if not self.reverse else not self.status

            def __del__(self) -> None:
                """析构函数"""
                GPIO.cleanup(self.InPin)
                if self.PowPin:
                    GPIO.cleanup(self.PowPin)
    else:
        from periphery import GPIO

        def get_line_id(str_id:str):
            """
            从端口索引号得到总线id
            ----
            Args:
                str_id(str): 端口索引号,如"B1"
            """
            port = str_id[0]
            port_id = {
                "A": 0,
                "B": 1,
                "C": 2,
                "D": 3
            }[port]
            pin = int(str_id[1])
            return port_id*8 + pin

        class LED:
            def __init__(self, str_pin:str) -> None:
                """
                初始化LED
                ----
                Args:
                    str_pin(str): 端口索引号,如"GPIO1-A2"
                """
                self.chip = {
                    "GPIO0": "/dev/gpiochip0",
                    "GPIO1": "/dev/gpiochip1",
                    "GPIO2": "/dev/gpiochip2",
                    "GPIO3": "/dev/gpiochip3",
                    "GPIO4": "/dev/gpiochip4",
                }[str_pin.split("-")[0]]
                self.line = get_line_id(str_pin.split("-")[1])

                self.led = GPIO(self.chip, self.line, "out")

            def on(self):
                """开启LED"""
                self.led.write(True)

            def off(self):
                """关闭LED"""
                self.led.write(False)

            def close(self):
                """关闭LED"""
                self.led.write(False)
                self.led.close()

            def __del__(self):
                """析构函数"""
                self.close()


        class Switch:
            """开关类 - 适用于非树莓派设备"""

            status: bool = False
            readFlag: bool = True

            def __init__(
                self,
                str_pin: str,
                reverse: bool = False
            ) -> None:
                """
                初始化开关
                ----
                泰山派只能设置为下拉电阻

                Args:
                    str_pin: 端口索引号，如"GPIO1-A2"
                    reverse: 是否反转开关状态
                """
                self.chip = {
                    "GPIO0": "/dev/gpiochip0",
                    "GPIO1": "/dev/gpiochip1",
                    "GPIO2": "/dev/gpiochip2",
                    "GPIO3": "/dev/gpiochip3",
                    "GPIO4": "/dev/gpiochip4",
                }[str_pin.split("-")[0]]

                self.line = get_line_id(str_pin.split("-")[1])
                self.reverse = reverse

                # 设置输入引脚和上下拉
                self.switch = GPIO(self.chip, self.line, "in")

            def read_status(self) -> bool:
                """
                读取开关状态
                ----
                Returns:
                    status: 开关状态
                """
                self.status = self.switch.read()
                return self.status if not self.reverse else not self.status

            def __del__(self) -> None:
                """析构函数"""
                self.switch.close()


    class OLED_I2C:
        def __init__(self, port:int=1, add:int=0x3c, lang:str="zh-cn") -> None:
            """
            OLED初始化
            ----
            Args:
                port(int):i2c的总线编号，即i2cdetect -y 1的1
                add(int):16进制的i2c地址
                lang(str):语言,默认为zh-cn,可以改为us-en
            """
            self.Opened = False

            try:
                ser = i2c(port=port, address=add)
                self.device = sh1106(ser)
                # 创建一个空白图像
                self.image = Image.new('1', (self.device.width, self.device.height))
                self.draw = ImageDraw.Draw(self.image)
                if lang == "zh-cn":
                    self._font = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 12)
                elif lang == "us-en":
                    self._font = ImageFont.load_default()
                else:
                    raise ValueError("不支持的语言")
                self.Opened = True
            except:
                self.Opened = False


        def text(self, data:str, position:tuple[int, int]):
            """
            在画面中绘制文字
            ----
            Args:
                data(str):需要绘制的文字数据
                position(tuple[int,int]):绘制文字的位置
            """
            if self.Opened:
                self.draw.text(position, data, font=self._font, fill=255)

        def display(self,reverse:bool = False):
            """
            在屏幕上显示画面
            ----
            Args:
                reverse(bool):是否旋转180度
            """
            if self.Opened:
                if reverse:
                    self.image = self.image.rotate(180)
                self.device.display(self.image)

        def clear(self):
            """清空画面"""
            if self.Opened:
                self.draw.rectangle(self.device.bounding_box, fill="black")
except:
    print("无法使用GPIO相关的库")

    class LED :
        def __init__(self, _OutPin: int) -> None:
            pass

        def on(self):
            pass

        def off(self):
            pass

    class Switch:
        status: bool = False
        readFlag: bool = True

        def __init__(
            self,
            _InPin: int,
            pull_up_down: int = 22,
            _PowPin: int | None = None,
            reverse: bool = False
        ) -> None:
            pass

        def read_status(self) -> bool:
            return False

    class OLED_I2C:
        def __init__(self, port:int=1, add:int=0x3c) -> None:
            pass

        def text(self, data:str, position:tuple[int, int]):
            pass

        def display(self):
            pass

        def clear(self):
            pass
