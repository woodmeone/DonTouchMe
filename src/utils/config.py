"""
配置管理模块
负责读取、写入和管理配置文件
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

from .logger import Logger

logger = Logger()


class Config:
    """配置管理器"""

    # 默认配置
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "notification": {
            "enabled": True,
            "provider": "pushplus",
            "token": "",  # 用户需要填写
            "send_camera": True,
            "send_screenshot": True
        },
        "camera": {
            "enabled": True,
            "device_id": 0,
            "resolution": [1280, 720],
            "save_local": True
        },
        "screenshot": {
            "enabled": True,
            "save_local": True,
            "quality": 85
        },
        "storage": {
            "max_images": 100,
            "auto_cleanup": True,
            "retention_days": 30
        },
        "trigger": {
            "on_boot": True,
            "on_wake": True,
            "delay_seconds": 10
        },
        "background_monitor": {
            "enabled": True,
            "boot_detection_threshold": 120,
            "debounce_interval": 30
        },
        "autostart": {
            "enabled": False
        },
        "advanced": {
            "debug_mode": False,
            "log_level": "INFO"
        }
    }

    def __init__(self, config_path: str = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，默认为 data/config.json
        """
        if config_path is None:
            # 默认配置文件路径
            project_root = Path(__file__).parent.parent.parent
            self.config_path = project_root / 'data' / 'config.json'
        else:
            self.config_path = Path(config_path)

        self.config = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置字典
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"配置文件加载成功: {self.config_path}")

                # 合并默认配置（处理新增配置项）
                self.config = self._merge_config(self.DEFAULT_CONFIG, self.config)
            else:
                # 配置文件不存在，使用默认配置
                logger.warning(f"配置文件不存在，使用默认配置: {self.config_path}")
                self.config = self.DEFAULT_CONFIG.copy()
                self.save()  # 保存默认配置

            return self.config

        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            # 使用默认配置
            self.config = self.DEFAULT_CONFIG.copy()
            return self.config

    def save(self) -> bool:
        """
        保存配置到文件

        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)

            logger.info(f"配置文件保存成功: {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置项路径，支持点号分隔，如 'notification.enabled'
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        设置配置项

        Args:
            key: 配置项路径，支持点号分隔
            value: 配置值
            save: 是否立即保存到文件

        Returns:
            是否设置成功
        """
        keys = key.split('.')

        try:
            config = self.config
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            config[keys[-1]] = value

            if save:
                return self.save()
            return True

        except Exception as e:
            logger.error(f"设置配置项失败 ({key}): {e}")
            return False

    def get_all(self) -> Dict[str, Any]:
        """获取完整配置字典"""
        return self.config.copy()

    def reset_to_default(self) -> bool:
        """
        重置为默认配置

        Returns:
            是否重置成功
        """
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save()

    @staticmethod
    def _merge_config(default: Dict, custom: Dict) -> Dict:
        """
        合并配置，保留用户配置，补充默认配置中的新项

        Args:
            default: 默认配置
            custom: 用户配置

        Returns:
            合并后的配置
        """
        result = default.copy()

        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._merge_config(result[key], value)
            else:
                result[key] = value

        return result


# 全局配置实例
_global_config = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


if __name__ == '__main__':
    # 测试配置管理
    config = Config()
    print("配置文件路径:", config.config_path)
    print("通知启用状态:", config.get('notification.enabled'))
    print("摄像头分辨率:", config.get('camera.resolution'))

    # 测试设置配置
    config.set('notification.token', 'test_token_123', save=False)
    print("设置 Token:", config.get('notification.token'))
