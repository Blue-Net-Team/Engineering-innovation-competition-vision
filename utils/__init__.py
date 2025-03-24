"""
Copyright (C) 2025 IVEN-CN(He Yunfeng) and Anan-yy(Weng Kaiyi)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from ._cap import InterpolatedCap, LoadCap, Cap
from .UART import Uart
from .typingCheck import check_args
from .gpio import Switch, OLED_I2C, LED
from .tspi_board_info import get_CPU_temp, get_GPU_temp
from .wifi_connect import connect_to_wifi
from .logger import printLog
from .ConfigLoader import ConfigLoader
from .Recorder import Recorder

__all__ = [
    "Cap",
    "InterpolatedCap",
    "LoadCap",
    "Uart",
    "check_args",
    "Switch",
    "OLED_I2C",
    "LED",
    "get_CPU_temp",
    "get_GPU_temp",
    "connect_to_wifi",
    "printLog",
    "ConfigLoader",
    "Recorder",
]
