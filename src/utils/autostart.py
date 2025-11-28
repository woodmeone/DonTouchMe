"""
Windows 开机自启动管理模块
通过注册表管理程序开机自启动
"""

import sys
import winreg
from pathlib import Path
from typing import Optional

from .logger import Logger

logger = Logger()


class AutoStartManager:
    """Windows 开机自启动管理器"""

    # 注册表路径
    REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    # 应用名称（注册表键名）
    APP_NAME = "DonTouchMe"

    @staticmethod
    def is_enabled() -> bool:
        """
        检查是否已启用开机自启动

        Returns:
            如果已启用返回 True，否则返回 False
        """
        try:
            # 打开注册表键（只读）
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                AutoStartManager.REGISTRY_PATH,
                0,
                winreg.KEY_READ
            )

            try:
                # 尝试读取值
                value, _ = winreg.QueryValueEx(key, AutoStartManager.APP_NAME)
                winreg.CloseKey(key)
                logger.debug(f"检测到自启动项: {value}")
                return True
            except FileNotFoundError:
                # 键不存在
                winreg.CloseKey(key)
                return False

        except Exception as e:
            logger.error(f"检查自启动状态失败: {e}")
            return False

    @staticmethod
    def enable(gui_script_path: Optional[str] = None) -> bool:
        """
        启用开机自启动

        Args:
            gui_script_path: GUI 启动脚本路径，默认为项目的 gui.py

        Returns:
            操作是否成功
        """
        try:
            # 确定 GUI 脚本路径
            if gui_script_path is None:
                # 默认为项目根目录的 gui.py
                gui_script_path = str(Path(__file__).parent.parent.parent / 'gui.py')

            # 检查文件是否存在
            if not Path(gui_script_path).exists():
                logger.error(f"GUI 脚本不存在: {gui_script_path}")
                return False

            # 使用 pythonw.exe 避免显示控制台窗口
            pythonw = sys.executable.replace('python.exe', 'pythonw.exe')
            if not Path(pythonw).exists():
                logger.warning(f"pythonw.exe 不存在，使用 python.exe: {pythonw}")
                pythonw = sys.executable

            # 构建启动命令
            command = f'"{pythonw}" "{gui_script_path}"'

            # 打开注册表键（写入）
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                AutoStartManager.REGISTRY_PATH,
                0,
                winreg.KEY_SET_VALUE
            )

            # 写入值
            winreg.SetValueEx(
                key,
                AutoStartManager.APP_NAME,
                0,
                winreg.REG_SZ,
                command
            )

            winreg.CloseKey(key)

            logger.info(f"已启用开机自启动: {command}")
            return True

        except Exception as e:
            logger.error(f"启用开机自启动失败: {e}")
            return False

    @staticmethod
    def disable() -> bool:
        """
        禁用开机自启动

        Returns:
            操作是否成功
        """
        try:
            # 打开注册表键（写入）
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                AutoStartManager.REGISTRY_PATH,
                0,
                winreg.KEY_SET_VALUE
            )

            try:
                # 删除值
                winreg.DeleteValue(key, AutoStartManager.APP_NAME)
                winreg.CloseKey(key)
                logger.info("已禁用开机自启动")
                return True
            except FileNotFoundError:
                # 键不存在（已经是禁用状态）
                winreg.CloseKey(key)
                logger.debug("自启动项不存在，无需删除")
                return True

        except Exception as e:
            logger.error(f"禁用开机自启动失败: {e}")
            return False

    @staticmethod
    def get_startup_command() -> Optional[str]:
        """
        获取当前的启动命令

        Returns:
            启动命令字符串，如果未启用返回 None
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                AutoStartManager.REGISTRY_PATH,
                0,
                winreg.KEY_READ
            )

            try:
                value, _ = winreg.QueryValueEx(key, AutoStartManager.APP_NAME)
                winreg.CloseKey(key)
                return value
            except FileNotFoundError:
                winreg.CloseKey(key)
                return None

        except Exception as e:
            logger.error(f"获取启动命令失败: {e}")
            return None


if __name__ == '__main__':
    # 测试
    print("=== Windows 开机自启动管理器测试 ===\n")

    # 检查当前状态
    is_enabled = AutoStartManager.is_enabled()
    print(f"当前状态: {'已启用' if is_enabled else '未启用'}")

    if is_enabled:
        command = AutoStartManager.get_startup_command()
        print(f"启动命令: {command}\n")

    # 交互式测试
    print("\n可用操作:")
    print("1. 启用开机自启动")
    print("2. 禁用开机自启动")
    print("3. 查看启动命令")
    print("0. 退出")

    while True:
        choice = input("\n请选择操作 (0-3): ").strip()

        if choice == '0':
            break
        elif choice == '1':
            success = AutoStartManager.enable()
            if success:
                print("✓ 已启用开机自启动")
                command = AutoStartManager.get_startup_command()
                print(f"  启动命令: {command}")
            else:
                print("✗ 启用失败")
        elif choice == '2':
            success = AutoStartManager.disable()
            if success:
                print("✓ 已禁用开机自启动")
            else:
                print("✗ 禁用失败")
        elif choice == '3':
            if AutoStartManager.is_enabled():
                command = AutoStartManager.get_startup_command()
                print(f"启动命令: {command}")
            else:
                print("未启用开机自启动")
        else:
            print("无效选择")
