"""
历史记录查看窗口
显示监控历史记录和图片
"""

from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QPushButton, QComboBox, QMessageBox,
    QSplitter, QGroupBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from ..core.database import Database
from ..utils.logger import Logger

logger = Logger()


class HistoryWindow(QWidget):
    """历史记录查看窗口"""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_record = None
        self.init_ui()
        self.load_records()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("DonTouchMe - 历史记录")
        self.setGeometry(100, 100, 1000, 700)

        # 主布局
        main_layout = QVBoxLayout()

        # 1. 工具栏
        toolbar_layout = QHBoxLayout()

        # 类型筛选
        toolbar_layout.addWidget(QLabel("类型:"))
        self.filter_type = QComboBox()
        self.filter_type.addItems(["全部", "开机", "唤醒", "手动"])
        self.filter_type.currentIndexChanged.connect(self.apply_filters)
        toolbar_layout.addWidget(self.filter_type)

        toolbar_layout.addStretch()

        # 刷新按钮
        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.clicked.connect(self.load_records)
        toolbar_layout.addWidget(self.btn_refresh)

        # 删除按钮
        self.btn_delete = QPushButton("删除选中记录")
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_delete.setEnabled(False)
        toolbar_layout.addWidget(self.btn_delete)

        main_layout.addLayout(toolbar_layout)

        # 2. 分割器：左侧列表，右侧详情
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：记录列表
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "类型", "时间", "通知状态", "通知方式"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.selectionModel().selectionChanged.connect(self.on_record_selected)

        splitter.addWidget(self.table)

        # 右侧：详情区域
        detail_widget = QWidget()
        detail_layout = QVBoxLayout()

        # 详情信息
        self.detail_label = QLabel("请选择一条记录查看详情")
        self.detail_label.setAlignment(Qt.AlignCenter)
        detail_layout.addWidget(self.detail_label)

        # 图片预览区域
        images_group = QGroupBox("图片预览")
        images_layout = QVBoxLayout()

        # 摄像头图片
        self.camera_label = QLabel("摄像头照片")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("border: 1px solid gray;")
        self.camera_label.setFixedHeight(300)
        images_layout.addWidget(self.camera_label)

        # 屏幕截图
        self.screenshot_label = QLabel("屏幕截图")
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.screenshot_label.setStyleSheet("border: 1px solid gray;")
        self.screenshot_label.setFixedHeight(300)
        images_layout.addWidget(self.screenshot_label)

        images_group.setLayout(images_layout)
        detail_layout.addWidget(images_group)

        detail_widget.setLayout(detail_layout)

        # 使用滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(detail_widget)

        splitter.addWidget(scroll_area)

        # 设置分割比例
        splitter.setSizes([400, 600])

        main_layout.addWidget(splitter)

        # 3. 统计信息
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        main_layout.addWidget(self.stats_label)

        self.setLayout(main_layout)

    def load_records(self):
        """加载历史记录"""
        try:
            # 获取所有记录
            records = self.db.get_all_records(limit=1000)

            # 清空表格
            self.table.setRowCount(0)

            # 填充数据
            for row_idx, record in enumerate(records):
                self.table.insertRow(row_idx)

                # ID
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(record['id'])))

                # 类型
                type_map = {'boot': '开机', 'wake': '唤醒', 'manual': '手动'}
                type_text = type_map.get(record['trigger_type'], record['trigger_type'])
                self.table.setItem(row_idx, 1, QTableWidgetItem(type_text))

                # 时间
                trigger_time = datetime.fromisoformat(record['trigger_time'])
                time_text = trigger_time.strftime('%Y-%m-%d %H:%M:%S')
                self.table.setItem(row_idx, 2, QTableWidgetItem(time_text))

                # 通知状态
                status_text = "成功" if record['notification_sent'] else "失败"
                self.table.setItem(row_idx, 3, QTableWidgetItem(status_text))

                # 通知方式
                self.table.setItem(row_idx, 4, QTableWidgetItem(record['notification_method']))

            # 调整列宽
            self.table.resizeColumnsToContents()

            # 更新统计信息
            self.update_statistics()

            logger.info(f"加载了 {len(records)} 条历史记录")

        except Exception as e:
            logger.error(f"加载历史记录失败: {e}")
            QMessageBox.critical(self, "错误", f"加载历史记录失败: {e}")

    def apply_filters(self):
        """应用筛选条件"""
        try:
            filter_text = self.filter_type.currentText()

            if filter_text == "全部":
                self.load_records()
            else:
                # 类型映射
                type_map = {'开机': 'boot', '唤醒': 'wake', '手动': 'manual'}
                trigger_type = type_map.get(filter_text)

                if trigger_type:
                    records = self.db.get_records_by_type(trigger_type, limit=1000)
                    self._display_records(records)

        except Exception as e:
            logger.error(f"应用筛选失败: {e}")

    def _display_records(self, records):
        """显示记录列表"""
        self.table.setRowCount(0)

        for row_idx, record in enumerate(records):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(record['id'])))

            type_map = {'boot': '开机', 'wake': '唤醒', 'manual': '手动'}
            type_text = type_map.get(record['trigger_type'], record['trigger_type'])
            self.table.setItem(row_idx, 1, QTableWidgetItem(type_text))

            trigger_time = datetime.fromisoformat(record['trigger_time'])
            time_text = trigger_time.strftime('%Y-%m-%d %H:%M:%S')
            self.table.setItem(row_idx, 2, QTableWidgetItem(time_text))

            status_text = "成功" if record['notification_sent'] else "失败"
            self.table.setItem(row_idx, 3, QTableWidgetItem(status_text))

            self.table.setItem(row_idx, 4, QTableWidgetItem(record['notification_method']))

        self.table.resizeColumnsToContents()

    def on_record_selected(self):
        """记录选中事件"""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            self.btn_delete.setEnabled(False)
            return

        self.btn_delete.setEnabled(True)

        # 获取选中的记录ID
        row = selected_rows[0].row()
        record_id = int(self.table.item(row, 0).text())

        # 加载记录详情
        self.load_record_detail(record_id)

    def load_record_detail(self, record_id):
        """加载记录详情"""
        try:
            record = self.db.get_record_by_id(record_id)
            if not record:
                return

            self.current_record = record

            # 显示详情信息
            type_map = {'boot': '开机', 'wake': '唤醒', 'manual': '手动'}
            trigger_time = datetime.fromisoformat(record['trigger_time'])

            detail_text = f"""
记录ID: {record['id']}
触发类型: {type_map.get(record['trigger_type'], record['trigger_type'])}
触发时间: {trigger_time.strftime('%Y-%m-%d %H:%M:%S')}
通知状态: {'成功' if record['notification_sent'] else '失败'}
通知方式: {record['notification_method']}
            """.strip()

            self.detail_label.setText(detail_text)

            # 加载摄像头图片
            if record['camera_path']:
                camera_path = Path(record['camera_path'])
                if camera_path.exists():
                    pixmap = QPixmap(str(camera_path))
                    scaled_pixmap = pixmap.scaled(
                        self.camera_label.width(),
                        self.camera_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.camera_label.setPixmap(scaled_pixmap)
                else:
                    self.camera_label.setText("摄像头照片（文件不存在）")
                    self.camera_label.setPixmap(QPixmap())
            else:
                self.camera_label.setText("摄像头照片（无）")
                self.camera_label.setPixmap(QPixmap())

            # 加载屏幕截图
            if record['screenshot_path']:
                screenshot_path = Path(record['screenshot_path'])
                if screenshot_path.exists():
                    pixmap = QPixmap(str(screenshot_path))
                    scaled_pixmap = pixmap.scaled(
                        self.screenshot_label.width(),
                        self.screenshot_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.screenshot_label.setPixmap(scaled_pixmap)
                else:
                    self.screenshot_label.setText("屏幕截图（文件不存在）")
                    self.screenshot_label.setPixmap(QPixmap())
            else:
                self.screenshot_label.setText("屏幕截图（无）")
                self.screenshot_label.setPixmap(QPixmap())

        except Exception as e:
            logger.error(f"加载记录详情失败: {e}")

    def delete_record(self):
        """删除选中的记录"""
        if not self.current_record:
            return

        reply = QMessageBox.question(
            self,
            '删除确认',
            f"确定要删除记录 ID: {self.current_record['id']} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.db.delete_record(self.current_record['id'])
                if success:
                    QMessageBox.information(self, "成功", "记录已删除")
                    self.load_records()
                    self.current_record = None
                    self.detail_label.setText("请选择一条记录查看详情")
                    self.camera_label.clear()
                    self.screenshot_label.clear()
                else:
                    QMessageBox.warning(self, "失败", "删除记录失败")

            except Exception as e:
                logger.error(f"删除记录失败: {e}")
                QMessageBox.critical(self, "错误", f"删除记录失败: {e}")

    def update_statistics(self):
        """更新统计信息"""
        try:
            stats = self.db.get_statistics()
            stats_text = (
                f"总记录数: {stats['total_count']} | "
                f"开机: {stats['boot_count']} | "
                f"唤醒: {stats['wake_count']} | "
                f"手动: {stats['manual_count']} | "
                f"通知成功率: {stats['notification_success_rate']}"
            )
            self.stats_label.setText(stats_text)

        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = HistoryWindow()
    window.show()
    sys.exit(app.exec_())
