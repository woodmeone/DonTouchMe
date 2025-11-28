"""
日志系统模块
提供统一的日志记录功能
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class Logger:
    """日志管理器"""

    _instance = None
    _logger = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化日志系统"""
        if self._logger is not None:
            return

        # 创建日志目录
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        # 日志文件名包含日期
        log_file = log_dir / f'dontouchme_{datetime.now().strftime("%Y%m%d")}.log'

        # 创建 logger
        self._logger = logging.getLogger('DonTouchMe')
        self._logger.setLevel(logging.DEBUG)

        # 避免重复添加 handler
        if not self._logger.handlers:
            # 文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # 日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

    def get_logger(self):
        """获取 logger 实例"""
        return self._logger

    @staticmethod
    def debug(msg, *args, **kwargs):
        """调试日志"""
        Logger()._logger.debug(msg, *args, **kwargs)

    @staticmethod
    def info(msg, *args, **kwargs):
        """信息日志"""
        Logger()._logger.info(msg, *args, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        """警告日志"""
        Logger()._logger.warning(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        """错误日志"""
        Logger()._logger.error(msg, *args, **kwargs)

    @staticmethod
    def critical(msg, *args, **kwargs):
        """严重错误日志"""
        Logger()._logger.critical(msg, *args, **kwargs)


# 便捷的全局日志函数
def get_logger():
    """获取日志记录器"""
    return Logger().get_logger()


# 导出日志函数
debug = Logger.debug
info = Logger.info
warning = Logger.warning
error = Logger.error
critical = Logger.critical


if __name__ == '__main__':
    # 测试日志系统
    info("这是一条信息日志")
    debug("这是一条调试日志")
    warning("这是一条警告日志")
    error("这是一条错误日志")
    print("日志测试完成，请查看 logs 目录")
