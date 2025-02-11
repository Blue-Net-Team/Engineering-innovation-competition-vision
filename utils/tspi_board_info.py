def get_CPU_temp():
    """
    获取CPU温度
    ----
    Returns:
        temp: CPU温度
    """
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = int(f.read()) / 1000
    return temp

def get_GPU_temp():
    """
    获取GPU温度
    ----
    Returns:
        temp: GPU温度
    """
    try:
        with open("/sys/class/thermal/thermal_zone1/temp", "r") as f:
            temp = int(f.read()) / 1000
    except FileNotFoundError:
        temp = None
    return temp
