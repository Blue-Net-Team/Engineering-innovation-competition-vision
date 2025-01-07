import time
import threading
from utils.gpio import *


def test_switch():
    switch = Switch(_InPin=18)
    switch.read_statusAlway()
    try:
        while True:
            print(switch.read_status())
            time.sleep(0.1)
    except KeyboardInterrupt:
        switch.stop_read()
        print("stop read")
    finally:
        switch.stop_read()

def test_ToggleSwitch():
    toggle_switch = ToggleSwitch(_InPin=18)
    toggle_switch.read_statusAlway()
    try:
        while True:
            print(toggle_switch.read_status())
            time.sleep(0.1)
    except KeyboardInterrupt:
        toggle_switch.stop_read()
        print("stop read")


if __name__ == "__main__":
    test_ToggleSwitch()
    # test_switch()