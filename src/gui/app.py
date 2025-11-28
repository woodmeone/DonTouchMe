"""
主GUI应用程序
系统托盘应用
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction,
    QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal

from ..core.monitor import Monitor
from ..utils.logger import Logger
from .config_window import ConfigWindow
from .history_window import HistoryWindow

logger = Logger()


class MonitorThread(QThread):
    """监控线程"""

    finished = pyqtSignal(dict)  # 监控完成信号

    def __init__(self, trigger_type='manual'):
        super().__init__()
        self.trigger_type = trigger_type

    def run(self):
        """执行监控任务"""
        try:
            monitor = Monitor()
            result = monitor.execute(trigger_type=self.trigger_type)
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"监控线程异常: {e}")
            self.finished.emit({'success': False, 'error': str(e)})


class DonTouchMeApp(QApplication):
    """DonTouchMe 主应用程序"""

    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出程序

        # 状态
        self.monitoring_enabled = True  # 监控是否启用
        self.monitor_thread = None

        # 窗口
        self.config_window = None
        self.history_window = None

        # 创建系统托盘
        self._init_tray()

        logger.info("DonTouchMe GUI 应用已启动")

    def _init_tray(self):
        """初始化系统托盘"""
        # 创建托盘图标（使用系统默认图标）
        self.tray_icon = QSystemTrayIcon(self)

        # 尝试加载自定义图标，如果不存在则使用默认图标
        icon_path = Path(__file__).parent / 'resources' / 'icon.png'
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            # 使用默认的信息图标
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_MessageBoxInformation))

        # 创建托盘菜单
        self.tray_menu = QMenu()

        # 菜单项：打开配置
        self.action_config = QAction("配置设置", self)
        self.action_config.triggered.connect(self.show_config)
        self.tray_menu.addAction(self.action_config)

        # 菜单项：查看历史
        self.action_history = QAction("历史记录", self)
        self.action_history.triggered.connect(self.show_history)
        self.tray_menu.addAction(self.action_history)

        self.tray_menu.addSeparator()

        # 菜单项：启用/禁用监控
        self.action_toggle_monitor = QAction("禁用监控", self)
        self.action_toggle_monitor.triggered.connect(self.toggle_monitoring)
        self.tray_menu.addAction(self.action_toggle_monitor)

        # 菜单项：手动触发
        self.action_manual_trigger = QAction("手动触发", self)
        self.action_manual_trigger.triggered.connect(self.manual_trigger)
        self.tray_menu.addAction(self.action_manual_trigger)

        self.tray_menu.addSeparator()

        # 菜单项：退出
        self.action_quit = QAction("退出", self)
        self.action_quit.triggered.connect(self.quit_app)
        self.tray_menu.addAction(self.action_quit)

        # 设置托盘菜单
        self.tray_icon.setContextMenu(self.tray_menu)

        # 双击托盘图标打开配置窗口
        self.tray_icon.activated.connect(self.on_tray_activated)

        # 显示托盘图标
        self.tray_icon.show()
        self.tray_icon.setToolTip("DonTouchMe - 监控运行中")

        logger.info("系统托盘已初始化")

    def on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            # 双击打开配置窗口
            self.show_config()

    def show_config(self):
        """显示配置窗口"""
        if self.config_window is None:
            self.config_window = ConfigWindow()
            self.config_window.config_saved.connect(self.on_config_saved)

        self.config_window.show()
        self.config_window.activateWindow()
        logger.info("打开配置窗口")

    def show_history(self):
        """显示历史记录窗口"""
        if self.history_window is None:
            self.history_window = HistoryWindow()

        self.history_window.show()
        self.history_window.activateWindow()
        logger.info("打开历史记录窗口")

    def toggle_monitoring(self):
        """切换监控启用/禁用状态"""
        self.monitoring_enabled = not self.monitoring_enabled

        if self.monitoring_enabled:
            self.action_toggle_monitor.setText("禁用监控")
            self.tray_icon.setToolTip("DonTouchMe - 监控运行中")
            logger.info("监控已启用")
            self.show_notification("监控已启用", "DonTouchMe 将监控电脑开机和唤醒事件")
        else:
            self.action_toggle_monitor.setText("启用监控")
            self.tray_icon.setToolTip("DonTouchMe - 监控已禁用")
            logger.info("监控已禁用")
            self.show_notification("监控已禁用", "DonTouchMe 不再自动监控，手动触发仍然可用")

    def manual_trigger(self):
        """手动触发监控"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.show_notification("提示", "监控任务正在执行中，请稍候...")
            return

        logger.info("手动触发监控任务")
        self.show_notification("手动触发", "正在执行监控任务...")

        self.monitor_thread = MonitorThread(trigger_type='manual')
        self.monitor_thread.finished.connect(self.on_monitor_finished)
        self.monitor_thread.start()

    def on_monitor_finished(self, result):
        """监控任务完成回调"""
        if result.get('success'):
            message = "监控任务执行成功"
            if result.get('notification_sent'):
                message += "\n微信通知已发送"
            self.show_notification("成功", message)
            logger.info("监控任务执行成功")
        else:
            error_msg = result.get('error', '未知错误')
            self.show_notification("失败", f"监控任务执行失败: {error_msg}")
            logger.error(f"监控任务执行失败: {error_msg}")

    def on_config_saved(self):
        """配置保存回调"""
        self.show_notification("配置已保存", "配置已成功保存并生效")
        logger.info("配置已保存")

    def show_notification(self, title, message):
        """显示系统托盘通知"""
        self.tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.Information,
            3000  # 显示3秒
        )

    def quit_app(self):
        """退出应用"""
        reply = QMessageBox.question(
            None,
            '退出确认',
            '确定要退出 DonTouchMe 吗？\n退出后将停止所有监控功能。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            logger.info("用户退出应用")
            self.tray_icon.hide()
            self.quit()


def main():
    """主函数"""
    app = DonTouchMeApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
