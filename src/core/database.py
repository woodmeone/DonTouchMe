"""
数据库模块
使用 SQLite 存储历史记录
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from ..utils.logger import Logger

logger = Logger()


class Database:
    """SQLite 数据库管理器"""

    def __init__(self, db_path: Path = None):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径，默认为 data/history.db
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / 'data' / 'history.db'

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"初始化数据库: {self.db_path}")
        self._init_database()

    def _init_database(self):
        """创建数据库表（如果不存在）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 创建历史记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS capture_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_type TEXT NOT NULL,
                    trigger_time TEXT NOT NULL,
                    camera_path TEXT,
                    screenshot_path TEXT,
                    notification_sent INTEGER DEFAULT 0,
                    notification_method TEXT,
                    created_at TEXT NOT NULL
                )
            ''')

            # 创建索引以加速查询
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trigger_time
                ON capture_history(trigger_time)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trigger_type
                ON capture_history(trigger_type)
            ''')

            conn.commit()
            conn.close()
            logger.info("数据库表初始化成功")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def add_record(self,
                   trigger_type: str,
                   trigger_time: datetime,
                   camera_path: Optional[Path] = None,
                   screenshot_path: Optional[Path] = None,
                   notification_sent: bool = False,
                   notification_method: str = 'none') -> int:
        """
        添加一条历史记录

        Args:
            trigger_type: 触发类型（boot/wake/manual）
            trigger_time: 触发时间
            camera_path: 摄像头图片路径
            screenshot_path: 屏幕截图路径
            notification_sent: 是否发送通知成功
            notification_method: 通知方式（base64/text/failed/none）

        Returns:
            记录ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO capture_history
                (trigger_type, trigger_time, camera_path, screenshot_path,
                 notification_sent, notification_method, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                trigger_type,
                trigger_time.isoformat(),
                str(camera_path) if camera_path else None,
                str(screenshot_path) if screenshot_path else None,
                1 if notification_sent else 0,
                notification_method,
                datetime.now().isoformat()
            ))

            record_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"添加历史记录成功: ID={record_id}, 类型={trigger_type}")
            return record_id

        except Exception as e:
            logger.error(f"添加历史记录失败: {e}")
            return -1

    def get_all_records(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        获取所有历史记录

        Args:
            limit: 返回记录数量限制
            offset: 偏移量（用于分页）

        Returns:
            历史记录列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM capture_history
                ORDER BY trigger_time DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))

            rows = cursor.fetchall()
            conn.close()

            # 转换为字典列表
            records = [dict(row) for row in rows]
            logger.info(f"查询到 {len(records)} 条历史记录")
            return records

        except Exception as e:
            logger.error(f"查询历史记录失败: {e}")
            return []

    def get_records_by_date(self, start_date: str, end_date: str = None) -> List[Dict]:
        """
        按日期范围查询历史记录

        Args:
            start_date: 开始日期（格式：YYYY-MM-DD）
            end_date: 结束日期（可选，默认为开始日期当天）

        Returns:
            历史记录列表
        """
        try:
            if end_date is None:
                end_date = start_date

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM capture_history
                WHERE DATE(trigger_time) BETWEEN ? AND ?
                ORDER BY trigger_time DESC
            ''', (start_date, end_date))

            rows = cursor.fetchall()
            conn.close()

            records = [dict(row) for row in rows]
            logger.info(f"查询到 {len(records)} 条历史记录（{start_date} ~ {end_date}）")
            return records

        except Exception as e:
            logger.error(f"按日期查询历史记录失败: {e}")
            return []

    def get_records_by_type(self, trigger_type: str, limit: int = 100) -> List[Dict]:
        """
        按触发类型查询历史记录

        Args:
            trigger_type: 触发类型（boot/wake/manual）
            limit: 返回记录数量限制

        Returns:
            历史记录列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM capture_history
                WHERE trigger_type = ?
                ORDER BY trigger_time DESC
                LIMIT ?
            ''', (trigger_type, limit))

            rows = cursor.fetchall()
            conn.close()

            records = [dict(row) for row in rows]
            logger.info(f"查询到 {len(records)} 条 {trigger_type} 类型记录")
            return records

        except Exception as e:
            logger.error(f"按类型查询历史记录失败: {e}")
            return []

    def get_record_by_id(self, record_id: int) -> Optional[Dict]:
        """
        根据ID查询单条记录

        Args:
            record_id: 记录ID

        Returns:
            历史记录字典，不存在则返回None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM capture_history WHERE id = ?', (record_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"查询记录失败 (ID={record_id}): {e}")
            return None

    def delete_record(self, record_id: int) -> bool:
        """
        删除一条历史记录

        Args:
            record_id: 记录ID

        Returns:
            是否删除成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM capture_history WHERE id = ?', (record_id,))
            conn.commit()
            conn.close()

            logger.info(f"删除历史记录成功: ID={record_id}")
            return True

        except Exception as e:
            logger.error(f"删除历史记录失败: {e}")
            return False

    def get_statistics(self) -> Dict:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 总记录数
            cursor.execute('SELECT COUNT(*) FROM capture_history')
            total_count = cursor.fetchone()[0]

            # 各类型记录数
            cursor.execute('''
                SELECT trigger_type, COUNT(*) as count
                FROM capture_history
                GROUP BY trigger_type
            ''')
            type_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # 通知成功率
            cursor.execute('SELECT COUNT(*) FROM capture_history WHERE notification_sent = 1')
            notification_success = cursor.fetchone()[0]

            conn.close()

            stats = {
                'total_count': total_count,
                'boot_count': type_counts.get('boot', 0),
                'wake_count': type_counts.get('wake', 0),
                'manual_count': type_counts.get('manual', 0),
                'notification_success': notification_success,
                'notification_success_rate': f"{(notification_success / total_count * 100):.1f}%" if total_count > 0 else "0%"
            }

            logger.info(f"统计信息: {stats}")
            return stats

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}


if __name__ == '__main__':
    # 测试数据库功能
    print("=== 数据库模块测试 ===")

    db = Database()

    # 添加测试记录
    print("\n添加测试记录...")
    record_id = db.add_record(
        trigger_type='manual',
        trigger_time=datetime.now(),
        camera_path=Path('data/captures/camera/test.jpg'),
        screenshot_path=Path('data/captures/screen/test.jpg'),
        notification_sent=True,
        notification_method='base64'
    )
    print(f"添加成功，记录ID: {record_id}")

    # 查询所有记录
    print("\n查询所有记录...")
    records = db.get_all_records()
    for record in records:
        print(f"  ID: {record['id']}, 类型: {record['trigger_type']}, "
              f"时间: {record['trigger_time']}, 通知: {record['notification_method']}")

    # 获取统计信息
    print("\n统计信息...")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✅ 数据库测试完成")
