import subprocess

def connect_to_wifi(ssid:str, password:str) -> tuple[bool, str]:
    """
    连接到指定的WiFi网络
    ----
    Args:
        ssid(str): WiFi网络的SSID
        password(str): WiFi网络的密码
    Returns:
        tuple[bool, str]: 返回一个元组，第一个元素为bool类型，表示是否连接成功，第二个元素为str类型，表示错误信息
    """
    try:
        # 连接到指定的SSID
        subprocess.run(
            ["sudo", "nmcli", "device", "wifi", "connect", ssid, "password", password],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return True, ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr
