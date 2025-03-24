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
import json

import yaml
from colorama import Fore


class ConfigLoader:
    """
    配置加载器，用于加载config配置
    """
    def save_config(self, path: str, config: dict):
        """
        重写配置
        ----
        此方法需要先读取配置并且修改后再调用，否则会覆盖原有配置

        Args:
            path (str): 保存路径
            config (dict): 配置字典
        """
        with open(path, "w", encoding="utf-8") as f:
            if path.endswith("json"):
                json.dump(config, f, indent=4)
            else:
                yaml.dump(config, f, default_flow_style=False)

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
            with open(_config, "r", encoding="utf-8") as f:
                if _config.endswith("json"):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
            return config
        else:
            raise TypeError("config must be str or dict")

    def load_param(self, config:dict, key:str, attr_name:str|None=None):
        """
        通用参数加载方法
        ----
        Args:
            config (dict): 配置文件
            key (str): 键
            attr_name (str): 属性名，如果没有指定，则使用 key 作为属性名
        Returns:
            str: 错误信息
        """
        res_str = ""
        attr_name = attr_name or key  # 如果没有指定属性名，则使用 key 作为属性名
        if key in config:
            setattr(self, attr_name, config[key])  # 动态赋值
        else:
            res_str += Fore.RED + f"配置文件读取 {attr_name} 参数失败"
        return res_str
