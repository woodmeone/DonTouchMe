"""
配置管理窗口
可视化编辑配置文件
"""

import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QCheckBox,
    QPushButton, QGroupBox, QMessageBox, QComboBox
)
from PyQt5.QtCore import pyqtSignal

from ..utils.config import get_config
from ..utils.logger import Logger

logger = Logger()


class ConfigWindow(QWidget):
    """配置管理窗口"""

    config_saved = pyqtSignal()  # 配置保存信号

    def __init__(self):
        super().__init__()
        self.config_path = Path(__file__).parent.parent.parent / 'data' / 'config.json'
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("DonTouchMe - 配置设置")
        self.setFixedSize(500, 600)

        # 主布局
        main_layout = QVBoxLayout()

        # 1. 通知设置分组
        notification_group = QGroupBox("微信通知设置")
        notification_layout = QFormLayout()

        self.notification_enabled = QCheckBox()
        self.notification_enabled.setChecked(True)
        notification_layout.addRow("启用通知:", self.notification_enabled)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("请输入 PushPlus Token")
        notification_layout.addRow("PushPlus Token:", self.token_input)

        notification_group.setLayout(notification_layout)
        main_layout.addWidget(notification_group)

        # 2. 摄像头设置分组
        camera_group = QGroupBox("摄像头设置")
        camera_layout = QFormLayout()

        self.camera_enabled = QCheckBox()
        self.camera_enabled.setChecked(True)
        camera_layout.addRow("启用摄像头:", self.camera_enabled)

        self.camera_device = QSpinBox()
        self.camera_device.setRange(0, 10)
        self.camera_device.setValue(0)
        camera_layout.addRow("设备ID:", self.camera_device)

        # 分辨率选择
        resolution_h_layout = QHBoxLayout()
        self.camera_width = QComboBox()
        self.camera_width.addItems(["640", "1280", "1920"])
        self.camera_width.setCurrentText("640")
        resolution_h_layout.addWidget(self.camera_width)

        resolution_h_layout.addWidget(QLabel("x"))

        self.camera_height = QComboBox()
        self.camera_height.addItems(["480", "720", "1080"])
        self.camera_height.setCurrentText("480")
        resolution_h_layout.addWidget(self.camera_height)

        resolution_widget = QWidget()
        resolution_widget.setLayout(resolution_h_layout)
        camera_layout.addRow("分辨率:", resolution_widget)

        camera_group.setLayout(camera_layout)
        main_layout.addWidget(camera_group)

        # 3. 截图设置分组
        screenshot_group = QGroupBox("屏幕截图设置")
        screenshot_layout = QFormLayout()

        self.screenshot_enabled = QCheckBox()
        self.screenshot_enabled.setChecked(True)
        screenshot_layout.addRow("启用截图:", self.screenshot_enabled)

        self.screenshot_quality = QSpinBox()
        self.screenshot_quality.setRange(1, 100)
        self.screenshot_quality.setValue(85)
        screenshot_layout.addRow("图片质量 (1-100):", self.screenshot_quality)

        screenshot_group.setLayout(screenshot_layout)
        main_layout.addWidget(screenshot_group)

        # 4. 按钮区域
        button_layout = QHBoxLayout()

        self.btn_save = QPushButton("保存配置")
        self.btn_save.clicked.connect(self.save_config)
        button_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.close)
        button_layout.addWidget(self.btn_cancel)

        main_layout.addLayout(button_layout)

        # 5. 提示信息
        info_label = QLabel(
            "提示：修改配置后需要保存才能生效。\n"
            "PushPlus Token 可在 http://www.pushplus.plus/ 获取。"
        )
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        main_layout.addWidget(info_label)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def load_config(self):
        """加载配置到界面"""
        try:
            config = get_config()

            # 加载通知配置
            notification = config.get('notification', {})
            self.notification_enabled.setChecked(notification.get('enabled', True))
            token = notification.get('token', '')
            if token != "请在此处填写您的 PushPlus Token":
                self.token_input.setText(token)

            # 加载摄像头配置
            camera = config.get('camera', {})
            self.camera_enabled.setChecked(camera.get('enabled', True))
            self.camera_device.setValue(camera.get('device_id', 0))

            resolution = camera.get('resolution', [640, 480])
            self.camera_width.setCurrentText(str(resolution[0]))
            self.camera_height.setCurrentText(str(resolution[1]))

            # 加载截图配置
            screenshot = config.get('screenshot', {})
            self.screenshot_enabled.setChecked(screenshot.get('enabled', True))
            self.screenshot_quality.setValue(screenshot.get('quality', 85))

            logger.info("配置加载成功")

        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            QMessageBox.warning(self, "错误", f"加载配置失败: {e}")

    def save_config(self):
        """保存配置到文件"""
        try:
            # 验证 Token
            token = self.token_input.text().strip()
            if self.notification_enabled.isChecked() and not token:
                QMessageBox.warning(self, "警告", "请输入 PushPlus Token 或禁用通知功能")
                return

            # 构建配置字典
            config = {
                "notification": {
                    "enabled": self.notification_enabled.isChecked(),
                    "token": token if token else "请在此处填写您的 PushPlus Token",
                    "send_camera": True,
                    "send_screenshot": False
                },
                "camera": {
                    "enabled": self.camera_enabled.isChecked(),
                    "device_id": self.camera_device.value(),
                    "resolution": [
                        int(self.camera_width.currentText()),
                        int(self.camera_height.currentText())
                    ]
                },
                "screenshot": {
                    "enabled": self.screenshot_enabled.isChecked(),
                    "quality": self.screenshot_quality.value()
                },
                "history": {
                    "max_records": 1000,
                    "auto_cleanup_days": 30
                }
            }

            # 保存到文件
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info("配置保存成功")
            QMessageBox.information(self, "成功", "配置已保存！")

            # 发送信号
            self.config_saved.emit()
            self.close()

        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存配置失败: {e}")


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())
