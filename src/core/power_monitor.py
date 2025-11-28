"""
Windows 电源事件监听器
监听系统休眠/唤醒事件
"""

import sys
import time
import threading
import ctypes
from ctypes import wintypes
from typing import Callable, Optional

# Windows API
try:
    import win32gui
    import win32con
    import win32api
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

from ..utils.logger import Logger

logger = Logger()


class PowerEventMonitor:
    """
    Windows 电源事件监听器

    监听 WM_POWERBROADCAST 消息，检测系统休眠/唤醒事件
    """

    def __init__(self, on_boot_callback: Optional[Callable] = None,
                 on_wake_callback: Optional[Callable] = None):
        """
        初始化监听器

        Args:
            on_boot_callback: 开机事件回调函数
            on_wake_callback: 唤醒事件回调函数
        """
        if not HAS_PYWIN32:
            raise RuntimeError("pywin32 未安装，无法使用电源事件监听功能")

        if sys.platform != 'win32':
            raise RuntimeError("此模块仅支持 Windows 系统")

        self.on_boot_callback = on_boot_callback
        self.on_wake_callback = on_wake_callback

        # 防重复触发
        self.last_trigger_time = {}
        self.debounce_interval = 30  # 秒

        # 窗口和线程
        self.hwnd = None
        self.running = False
        self.monitor_thread = None

        logger.info("电源事件监听器已初始化")

    def start(self):
        """启动监听（在独立线程中运行）"""
        if self.running:
            logger.warning("监听器已在运行中")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._message_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("电源事件监听器已启动")

    def stop(self):
        """停止监听"""
        if not self.running:
            return

        self.running = False

        # 销毁窗口
        if self.hwnd:
            try:
                win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
            except Exception as e:
                logger.error(f"销毁窗口失败: {e}")

        # 等待线程结束
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)

        logger.info("电源事件监听器已停止")

    def _create_window(self):
        """创建隐藏窗口用于接收Windows消息"""
        # 注册窗口类
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wndproc
        wc.lpszClassName = "DonTouchMePowerMonitor"
        wc.hInstance = win32api.GetModuleHandle(None)

        try:
            class_atom = win32gui.RegisterClass(wc)
        except Exception as e:
            logger.error(f"注册窗口类失败: {e}")
            raise

        # 创建隐藏窗口
        self.hwnd = win32gui.CreateWindow(
            class_atom,
            "DonTouchMe Power Monitor",
            0,  # 无样式（隐藏窗口）
            0, 0, 0, 0,  # 位置和大小
            0,  # 无父窗口
            0,  # 无菜单
            wc.hInstance,
            None
        )

        logger.info(f"电源监听窗口已创建: hwnd={self.hwnd}")

    def _wndproc(self, hwnd, msg, wparam, lparam):
        """Windows 消息处理函数"""
        if msg == win32con.WM_POWERBROADCAST:
            self._handle_power_event(wparam)
            return 0
        elif msg == win32con.WM_CLOSE:
            win32gui.DestroyWindow(hwnd)
            return 0
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _handle_power_event(self, event_type):
        """处理电源事件"""
        # PBT_APMRESUMEAUTOMATIC: 系统从休眠恢复
        if event_type == win32con.PBT_APMRESUMEAUTOMATIC:
            logger.info("电源事件: 系统从休眠自动恢复 (PBT_APMRESUMEAUTOMATIC)")
            if self._should_trigger('wake'):
                self._trigger_wake()

        # PBT_APMRESUMESUSPEND: 用户输入导致唤醒
        elif event_type == win32con.PBT_APMRESUMESUSPEND:
            logger.info("电源事件: 系统从挂起恢复 (PBT_APMRESUMESUSPEND)")
            if self._should_trigger('wake'):
                self._trigger_wake()

        # PBT_APMSUSPEND: 系统即将休眠（仅记录日志）
        elif event_type == win32con.PBT_APMSUSPEND:
            logger.info("电源事件: 系统即将休眠 (PBT_APMSUSPEND)")

        # PBT_APMPOWERSTATUSCHANGE: 电源状态变化
        elif event_type == win32con.PBT_APMPOWERSTATUSCHANGE:
            logger.debug("电源事件: 电源状态变化 (PBT_APMPOWERSTATUSCHANGE)")

    def _should_trigger(self, event_type: str) -> bool:
        """
        判断是否应该触发回调（防重复）

        Args:
            event_type: 事件类型 ('boot' 或 'wake')

        Returns:
            是否应该触发
        """
        now = time.time()
        last = self.last_trigger_time.get(event_type, 0)

        if now - last < self.debounce_interval:
            logger.debug(f"防重复触发: {event_type} 事件在 {self.debounce_interval} 秒内已触发过")
            return False

        self.last_trigger_time[event_type] = now
        return True

    def _trigger_wake(self):
        """触发唤醒回调"""
        if self.on_wake_callback:
            # 在独立线程中执行回调，避免阻塞消息循环
            threading.Thread(target=self.on_wake_callback, daemon=True).start()
        else:
            logger.warning("唤醒回调函数未设置")

    def _message_loop(self):
        """消息循环（在独立线程中运行）"""
        try:
            self._create_window()

            logger.info("开始消息循环...")

            # 定义 MSG 结构
            class MSG(ctypes.Structure):
                _fields_ = [
                    ("hwnd", wintypes.HWND),
                    ("message", wintypes.UINT),
                    ("wParam", wintypes.WPARAM),
                    ("lParam", wintypes.LPARAM),
                    ("time", wintypes.DWORD),
                    ("pt", wintypes.POINT)
                ]

            msg = MSG()
            lpmsg = ctypes.byref(msg)

            # 使用 ctypes 调用 GetMessage
            # 这样可以正确处理消息结构，避免 PyWin32 的参数格式问题
            while self.running:
                try:
                    # GetMessage: 返回值 > 0 表示有消息, 0 表示 WM_QUIT, -1 表示错误
                    ret = ctypes.windll.user32.GetMessageW(lpmsg, None, 0, 0)

                    if ret == 0:  # WM_QUIT
                        logger.info("收到 WM_QUIT 消息")
                        break
                    elif ret == -1:  # 错误
                        logger.error("GetMessage 返回错误")
                        break

                    # 处理消息
                    ctypes.windll.user32.TranslateMessage(lpmsg)
                    ctypes.windll.user32.DispatchMessageW(lpmsg)

                except Exception as e:
                    if self.running:  # 只在运行时记录错误
                        logger.error(f"消息处理异常: {e}")
                        time.sleep(1)  # 避免快速错误循环
                    else:
                        break

            logger.info("消息循环已退出")

        except Exception as e:
            logger.error(f"启动消息循环失败: {e}")
        finally:
            self.running = False


if __name__ == '__main__':
    # 测试
    print("=== 电源事件监听器测试 ===")
    print("请在测试期间执行以下操作:")
    print("1. 让系统进入睡眠状态 (Windows + X -> 睡眠)")
    print("2. 唤醒系统")
    print("3. 观察是否收到事件通知")
    print()

    def on_wake():
        print("!!! 检测到唤醒事件 !!!")

    monitor = PowerEventMonitor(on_wake_callback=on_wake)
    monitor.start()

    try:
        print("监听器运行中，按 Ctrl+C 退出...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止...")
        monitor.stop()
        print("已停止")
