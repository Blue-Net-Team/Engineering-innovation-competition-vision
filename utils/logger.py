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