import json
import cv2
import numpy as np
import yaml


class Detect:
    """
    检测器基类
    ----
    提供了卷积锐化的方法--sharpen
    """

    def sharpen(self, _img):
        """
        锐化图片
        ----
        :param img: 需要锐化的图片
        """
        # 锐化卷积核
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        img = _img.copy()
        img = cv2.filter2D(img, -1, kernel)  # 锐化
        for i in range(3):
            img = cv2.GaussianBlur(img, (3, 3), 0)  # 高斯模糊
        return img

    def save_config(self, path: str, config: dict):
        """
        重写配置
        ----
        此方法需要先读取配置并且修改后再调用，否则会覆盖原有配置

        Args:
            path (str): 保存路径
            config (dict): 配置字典
        """
        with open(path, "w") as f:
            json.dump(config, f, indent=4)

    def load_config(self, _config: str|dict):
        """
        加载配置
        ----
        Args:
            _config (str|dict): 配置文件路径
        Returns:
            config (dict): 配置字典
        """
        if isinstance(_config, dict):
            return _config
        elif isinstance(_config, str):
            with open(_config, "r") as f:
                if _config.endswith("json"):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
            return config
        else:
            raise TypeError("config must be str or dict")
