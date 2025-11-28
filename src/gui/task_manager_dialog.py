"""
任务计划管理对话框
用于安装、卸载和查看任务计划状态
"""

import sys
import ctypes
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QTextEdit, QMessageBox, QProgressDialog, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from ..tasks.scheduler import WindowsScheduler
from ..utils.logger import Logger

logger = Logger()


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin(script_path):
    """以管理员权限运行脚本"""
    try:
        if sys.platform == 'win32':
            # 使用 ShellExecute 以管理员权限运行
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                f'"{script_path}"',
                None,
                1  # SW_SHOWNORMAL
            )
            return True
        return False
    except Exception as e:
        logger.error(f"以管理员权限运行失败: {e}")
        return False


class TaskInstallThread(QThread):
    """任务安装线程"""

    finished = pyqtSignal(bool, bool, str)  # boot_success, wake_success, message

    def __init__(self, action='install'):
        super().__init__()
        self.action = action  # 'install' 或 'uninstall'

    def run(self):
        """执行任务安装/卸载"""
        try:
            scheduler = WindowsScheduler()

            if self.action == 'install':
                boot_success, wake_success = scheduler.install_all()
                if boot_success and wake_success:
                    message = "所有任务计划安装成功！"
                elif boot_success:
                    message = "开机任务安装成功，唤醒任务安装失败"
                elif wake_success:
                    message = "唤醒任务安装成功，开机任务安装失败"
                else:
                    message = "任务计划安装失败"
                self.finished.emit(boot_success, wake_success, message)

            elif self.action == 'uninstall':
                boot_success = scheduler.uninstall_boot_task()
                wake_success = scheduler.uninstall_wake_task()
                if boot_success and wake_success:
                    message = "所有任务计划卸载成功！"
                elif boot_success:
                    message = "开机任务卸载成功，唤醒任务卸载失败"
                elif wake_success:
                    message = "唤醒任务卸载成功，开机任务卸载失败"
                else:
                    message = "任务计划卸载失败"
                self.finished.emit(boot_success, wake_success, message)

        except Exception as e:
            logger.error(f"任务操作异常: {e}")
            self.finished.emit(False, False, f"操作失败: {str(e)}")


class TaskManagerDialog(QDialog):
    """任务计划管理对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("任务计划管理")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        self.scheduler = None
        try:
            self.scheduler = WindowsScheduler()
        except Exception as e:
            logger.error(f"初始化调度器失败: {e}")

        self.init_ui()
        self.update_status()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()

        # 标题
        title = QLabel("Windows 任务计划管理")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 说明文本
        desc = QLabel(
            "任务计划用于在电脑开机和从睡眠唤醒时自动触发监控。\n"
            "安装任务计划需要管理员权限。"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: gray; padding: 10px;")
        layout.addWidget(desc)

        # 管理员权限状态
        self.admin_status_label = QLabel()
        if is_admin():
            self.admin_status_label.setText("✓ 当前以管理员权限运行")
            self.admin_status_label.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
        else:
            self.admin_status_label.setText("✗ 当前未以管理员权限运行（某些操作需要管理员权限）")
            self.admin_status_label.setStyleSheet("color: orange; font-weight: bold; padding: 5px;")
        layout.addWidget(self.admin_status_label)

        # 状态显示区域
        status_group = QGroupBox("任务计划状态")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("正在检查状态...")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # 操作按钮
        button_layout = QHBoxLayout()

        self.install_button = QPushButton("安装任务计划")
        self.install_button.clicked.connect(self.install_tasks)
        button_layout.addWidget(self.install_button)

        self.uninstall_button = QPushButton("卸载任务计划")
        self.uninstall_button.clicked.connect(self.uninstall_tasks)
        button_layout.addWidget(self.uninstall_button)

        self.refresh_button = QPushButton("刷新状态")
        self.refresh_button.clicked.connect(self.update_status)
        button_layout.addWidget(self.refresh_button)

        layout.addLayout(button_layout)

        # 详细信息
        info_group = QGroupBox("详细信息")
        info_layout = QVBoxLayout()

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        info_layout.addWidget(self.info_text)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def update_status(self):
        """更新任务计划状态"""
        if not self.scheduler:
            self.status_label.setText("⚠ 初始化调度器失败，无法查看状态")
            self.status_label.setStyleSheet("color: red;")
            self.install_button.setEnabled(False)
            self.uninstall_button.setEnabled(False)
            return

        try:
            status = self.scheduler.check_status()
            boot_exists = status.get('boot_task_exists', False)
            wake_exists = status.get('wake_task_exists', False)

            # 更新状态显示
            status_text = ""
            if boot_exists and wake_exists:
                status_text = "✓ 所有任务计划已安装\n"
                status_text += f"  • {self.scheduler.TASK_NAME_BOOT} - 开机时自动运行\n"
                status_text += f"  • {self.scheduler.TASK_NAME_WAKE} - 从睡眠唤醒时自动运行"
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.install_button.setText("重新安装任务计划")
            elif boot_exists:
                status_text = "⚠ 部分任务计划已安装\n"
                status_text += f"  • {self.scheduler.TASK_NAME_BOOT} - 已安装\n"
                status_text += f"  • {self.scheduler.TASK_NAME_WAKE} - 未安装"
                self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                self.install_button.setText("安装缺失的任务")
            elif wake_exists:
                status_text = "⚠ 部分任务计划已安装\n"
                status_text += f"  • {self.scheduler.TASK_NAME_BOOT} - 未安装\n"
                status_text += f"  • {self.scheduler.TASK_NAME_WAKE} - 已安装"
                self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                self.install_button.setText("安装缺失的任务")
            else:
                status_text = "✗ 未安装任何任务计划\n"
                status_text += "  需要安装任务计划才能自动监控开机和唤醒事件"
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
                self.install_button.setText("安装任务计划")

            self.status_label.setText(status_text)

            # 更新详细信息
            info_text = "任务计划详情:\n"
            info_text += f"Python 解释器: {self.scheduler.python_exe}\n"
            info_text += f"主程序路径: {self.scheduler.main_script}\n"
            info_text += f"\n开机任务: {self.scheduler.TASK_NAME_BOOT}\n"
            info_text += f"  状态: {'已安装' if boot_exists else '未安装'}\n"
            info_text += f"  触发器: 系统启动时\n"
            info_text += f"  延迟: 10秒\n"
            info_text += f"\n唤醒任务: {self.scheduler.TASK_NAME_WAKE}\n"
            info_text += f"  状态: {'已安装' if wake_exists else '未安装'}\n"
            info_text += f"  触发器: Kernel-Power 事件 107 (睡眠/休眠恢复)\n"
            info_text += f"  延迟: 5秒\n"
            self.info_text.setText(info_text)

            # 更新按钮状态
            self.uninstall_button.setEnabled(boot_exists or wake_exists)

        except Exception as e:
            logger.error(f"更新状态失败: {e}")
            self.status_label.setText(f"⚠ 检查状态失败: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def install_tasks(self):
        """安装任务计划"""
        if not is_admin():
            reply = QMessageBox.question(
                self,
                '需要管理员权限',
                '安装任务计划需要管理员权限。\n\n'
                '是否要以管理员身份重新启动 GUI 应用？\n'
                '（当前窗口将会关闭）',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                # 获取 gui.py 的路径
                gui_script = Path(__file__).parent.parent.parent / 'gui.py'
                if run_as_admin(str(gui_script)):
                    QMessageBox.information(
                        self,
                        '提示',
                        '正在以管理员权限重新启动应用...\n'
                        '请在新窗口中再次打开"任务计划管理"'
                    )
                    # 关闭当前应用
                    self.close()
                    QApplication.instance().quit()
                else:
                    QMessageBox.critical(
                        self,
                        '错误',
                        '无法以管理员权限启动应用'
                    )
            return

        # 确认安装
        status = self.scheduler.check_status()
        if status.get('boot_task_exists') or status.get('wake_task_exists'):
            reply = QMessageBox.question(
                self,
                '确认安装',
                '检测到已安装的任务计划，将会被覆盖。\n\n'
                '注意：新版本使用 Kernel-Power 事件 107 检测唤醒，\n'
                '比旧版本更可靠。建议重新安装以更新唤醒检测机制。\n\n'
                '是否继续？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply != QMessageBox.Yes:
                return

        # 显示进度对话框
        progress = QProgressDialog("正在安装任务计划...", "取消", 0, 0, self)
        progress.setWindowTitle("安装中")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()

        # 在线程中执行安装
        self.install_thread = TaskInstallThread(action='install')
        self.install_thread.finished.connect(lambda boot, wake, msg: self.on_task_operation_finished(progress, boot, wake, msg))
        self.install_thread.start()

    def uninstall_tasks(self):
        """卸载任务计划"""
        if not is_admin():
            reply = QMessageBox.question(
                self,
                '需要管理员权限',
                '卸载任务计划需要管理员权限。\n\n'
                '是否要以管理员身份重新启动 GUI 应用？\n'
                '（当前窗口将会关闭）',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                gui_script = Path(__file__).parent.parent.parent / 'gui.py'
                if run_as_admin(str(gui_script)):
                    QMessageBox.information(
                        self,
                        '提示',
                        '正在以管理员权限重新启动应用...\n'
                        '请在新窗口中再次打开"任务计划管理"'
                    )
                    self.close()
                    QApplication.instance().quit()
                else:
                    QMessageBox.critical(self, '错误', '无法以管理员权限启动应用')
            return

        # 确认卸载
        reply = QMessageBox.question(
            self,
            '确认卸载',
            '确定要卸载所有任务计划吗？\n\n卸载后将无法自动监控开机和唤醒事件。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # 显示进度对话框
        progress = QProgressDialog("正在卸载任务计划...", "取消", 0, 0, self)
        progress.setWindowTitle("卸载中")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()

        # 在线程中执行卸载
        self.uninstall_thread = TaskInstallThread(action='uninstall')
        self.uninstall_thread.finished.connect(lambda boot, wake, msg: self.on_task_operation_finished(progress, boot, wake, msg))
        self.uninstall_thread.start()

    def on_task_operation_finished(self, progress, boot_success, wake_success, message):
        """任务操作完成回调"""
        progress.close()

        if boot_success and wake_success:
            QMessageBox.information(self, '成功', message)
        elif boot_success or wake_success:
            QMessageBox.warning(self, '部分成功', message)
        else:
            QMessageBox.critical(self, '失败', message)

        # 刷新状态
        self.update_status()
