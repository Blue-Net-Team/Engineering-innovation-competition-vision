from utils.gpio import *
import time

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

def test_toggle_switch():
    toggle_switch = Toggleswitch(_InPin=18)
    toggle_switch.read_statusAlway()
    try:
        while True:
            print(toggle_switch.get_toggle_state())
            time.sleep(0.1)
    except KeyboardInterrupt:
        toggle_switch.stop_read()
        print("stop read")
    finally:
        toggle_switch.stop_read()

if __name__ == "__main__":
    # test_toggle_switch()
    test_switch()