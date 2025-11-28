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
from ..core.power_monitor import PowerEventMonitor
from ..utils.logger import Logger
from ..utils.boot_detector import is_boot_start
from ..utils.autostart import AutoStartManager
from ..tasks.scheduler import WindowsScheduler
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

        # 电源监听器
        self.power_monitor = None

        # 创建系统托盘
        self._init_tray()

        # 检查是否为开机启动
        if is_boot_start(threshold_seconds=120):
            logger.info("检测到开机启动，将触发开机监控")
            self._on_boot_trigger()

        # 启动电源事件监听
        self._start_power_monitoring()

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

        # 菜单项：任务计划管理
        self.action_task_manager = QAction("任务计划管理", self)
        self.action_task_manager.triggered.connect(self.show_task_manager)
        self.tray_menu.addAction(self.action_task_manager)

        self.tray_menu.addSeparator()

        # 菜单项：开机自启动
        self.action_autostart = QAction("开机自启动", self)
        self.action_autostart.setCheckable(True)
        self.action_autostart.setChecked(AutoStartManager.is_enabled())
        self.action_autostart.triggered.connect(self.toggle_autostart)
        self.tray_menu.addAction(self.action_autostart)

        # 菜单项：启用/禁用后台监控
        self.action_toggle_monitor = QAction("禁用后台监控", self)
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

    def _start_power_monitoring(self):
        """启动电源事件监听"""
        if not self.monitoring_enabled:
            logger.info("监控已禁用，跳过电源监听启动")
            return

        try:
            self.power_monitor = PowerEventMonitor(
                on_boot_callback=self._on_boot_trigger,
                on_wake_callback=self._on_wake_trigger
            )
            self.power_monitor.start()
            logger.info("电源事件监听已启动")
        except Exception as e:
            logger.error(f"启动电源监听失败: {e}")
            self.show_notification("警告", f"启动电源监听失败: {e}\n将无法自动检测唤醒事件")

    def _stop_power_monitoring(self):
        """停止电源事件监听"""
        if self.power_monitor:
            self.power_monitor.stop()
            self.power_monitor = None
            logger.info("电源事件监听已停止")

    def _on_boot_trigger(self):
        """开机触发回调"""
        if not self.monitoring_enabled:
            logger.info("监控已禁用，跳过开机触发")
            return

        logger.info("开机事件触发")
        self._execute_monitor('boot')

    def _on_wake_trigger(self):
        """唤醒触发回调"""
        if not self.monitoring_enabled:
            logger.info("监控已禁用，跳过唤醒触发")
            return

        logger.info("唤醒事件触发")
        self._execute_monitor('wake')

    def _execute_monitor(self, trigger_type):
        """执行监控任务（在线程中）"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            logger.warning("监控任务正在执行，跳过本次触发")
            return

        self.monitor_thread = MonitorThread(trigger_type=trigger_type)
        self.monitor_thread.finished.connect(self.on_monitor_finished)
        self.monitor_thread.start()

    def toggle_autostart(self):
        """切换开机自启动"""
        if self.action_autostart.isChecked():
            if AutoStartManager.enable():
                self.show_notification("开机自启动", "已启用开机自启动")
                logger.info("开机自启动已启用")
            else:
                self.action_autostart.setChecked(False)
                self.show_notification("失败", "启用开机自启动失败")
        else:
            if AutoStartManager.disable():
                self.show_notification("开机自启动", "已禁用开机自启动")
                logger.info("开机自启动已禁用")
            else:
                self.action_autostart.setChecked(True)
                self.show_notification("失败", "禁用开机自启动失败")

    def toggle_monitoring(self):
        """切换后台监控启用/禁用状态"""
        self.monitoring_enabled = not self.monitoring_enabled

        if self.monitoring_enabled:
            self.action_toggle_monitor.setText("禁用后台监控")
            self.tray_icon.setToolTip("DonTouchMe - 后台监控运行中")
            self._start_power_monitoring()
            logger.info("后台监控已启用")
            self.show_notification("后台监控已启用", "将自动监控开机和唤醒事件")
        else:
            self.action_toggle_monitor.setText("启用后台监控")
            self.tray_icon.setToolTip("DonTouchMe - 后台监控已禁用")
            self._stop_power_monitoring()
            logger.info("后台监控已禁用")
            self.show_notification("后台监控已禁用", "手动触发仍然可用")

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

    def show_task_manager(self):
        """显示任务计划管理对话框"""
        from .task_manager_dialog import TaskManagerDialog
        dialog = TaskManagerDialog()
        dialog.exec_()

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
            '确定要退出 DonTouchMe 吗？\n\n'
            '退出后将停止后台监控功能。\n'
            '建议：您可以最小化到托盘而不是退出。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 停止电源监听
            self._stop_power_monitoring()
            logger.info("用户退出应用")
            self.tray_icon.hide()
            self.quit()


def main():
    """主函数"""
    app = DonTouchMeApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
