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
import datetime
from colorama import Fore, init, Style

init(autoreset=True)

def printLog(logData, time_color:str=Fore.YELLOW) -> None:
    """
    打印日志信息和时间戳(包含毫秒)
    ----
    Args:
        logData (str): 日志信息
        time_color (str): 时间戳颜色，默认为黄色
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
    print(
        f"{time_color}[{timestamp}] {Style.RESET_ALL}" + str(logData)
    )