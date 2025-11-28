"""
监控主逻辑模块
整合摄像头、截图和通知功能
"""

import time
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

from .camera import CameraCapture
from .screenshot import ScreenCapture
from .notifier import PushPlusNotifier
from .database import Database
from ..utils.config import get_config
from ..utils.logger import Logger

logger = Logger()


class Monitor:
    """监控管理器"""

    def __init__(self):
        """初始化监控器"""
        # 加载配置
        self.config = get_config()

        # 初始化数据库
        self.db = Database()

        # 初始化各个模块
        self._init_components()

    def _init_components(self):
        """初始化各个组件"""
        # 摄像头
        camera_config = self.config.get('camera', {})
        self.camera_enabled = camera_config.get('enabled', True)
        if self.camera_enabled:
            device_id = camera_config.get('device_id', 0)
            resolution = tuple(camera_config.get('resolution', [1280, 720]))
            self.camera = CameraCapture(device_id=device_id, resolution=resolution)
            logger.info(f"摄像头已初始化: 设备 {device_id}, 分辨率 {resolution}")
        else:
            self.camera = None
            logger.info("摄像头已禁用")

        # 截图
        screenshot_config = self.config.get('screenshot', {})
        self.screenshot_enabled = screenshot_config.get('enabled', True)
        if self.screenshot_enabled:
            quality = screenshot_config.get('quality', 85)
            self.screenshot = ScreenCapture(quality=quality)
            logger.info(f"截图已初始化: 质量 {quality}")
        else:
            self.screenshot = None
            logger.info("截图已禁用")

        # 通知
        notification_config = self.config.get('notification', {})
        self.notification_enabled = notification_config.get('enabled', True)
        if self.notification_enabled:
            token = notification_config.get('token', '')
            if token and token != "请在此处填写您的 PushPlus Token":
                self.notifier = PushPlusNotifier(token)
                self.send_camera_image = notification_config.get('send_camera', True)
                self.send_screenshot_image = notification_config.get('send_screenshot', True)
                logger.info("通知已初始化")
            else:
                self.notifier = None
                logger.warning("未配置 PushPlus Token，通知功能已禁用")
        else:
            self.notifier = None
            logger.info("通知已禁用")

    def execute(self, trigger_type: str = 'manual') -> Dict:
        """
        执行监控任务

        Args:
            trigger_type: 触发类型，可选 'boot', 'wake', 'manual'

        Returns:
            执行结果字典
        """
        result = {
            'success': False,
            'trigger_type': trigger_type,
            'timestamp': datetime.now().isoformat(),
            'camera_path': None,
            'screenshot_path': None,
            'notification_sent': False,
            'errors': []
        }

        logger.info(f"=== 开始执行监控任务 (触发类型: {trigger_type}) ===")

        # 1. 摄像头拍照
        camera_path = None
        if self.camera_enabled and self.camera:
            try:
                logger.info("正在拍照...")
                camera_path = self.camera.capture()
                if camera_path:
                    result['camera_path'] = str(camera_path)
                    logger.info(f"拍照成功: {camera_path}")
                else:
                    error_msg = "拍照失败"
                    result['errors'].append(error_msg)
                    logger.error(error_msg)
            except Exception as e:
                error_msg = f"拍照异常: {e}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
        else:
            logger.info("摄像头已禁用，跳过拍照")

        # 2. 屏幕截图
        screenshot_path = None
        if self.screenshot_enabled and self.screenshot:
            try:
                logger.info("正在截图...")
                screenshot_path = self.screenshot.capture()
                if screenshot_path:
                    result['screenshot_path'] = str(screenshot_path)
                    logger.info(f"截图成功: {screenshot_path}")
                else:
                    error_msg = "截图失败"
                    result['errors'].append(error_msg)
                    logger.error(error_msg)
            except Exception as e:
                error_msg = f"截图异常: {e}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
        else:
            logger.info("截图已禁用，跳过截图")

        # 3. 发送通知
        if self.notification_enabled and self.notifier:
            try:
                logger.info("正在发送通知...")

                # 准备要发送的图片
                images_to_send = []
                if self.send_camera_image and camera_path:
                    images_to_send.append(Path(camera_path))
                if self.send_screenshot_image and screenshot_path:
                    images_to_send.append(Path(screenshot_path))

                # 根据触发类型发送不同的通知
                if trigger_type == 'boot':
                    notification_sent = self.notifier.send_boot_notification(
                        camera_path=camera_path,
                        screenshot_path=screenshot_path
                    )
                elif trigger_type == 'wake':
                    notification_sent = self.notifier.send_wake_notification(
                        camera_path=camera_path,
                        screenshot_path=screenshot_path
                    )
                else:  # manual
                    notification_sent = self.notifier.send_manual_notification(
                        camera_path=camera_path,
                        screenshot_path=screenshot_path
                    )

                result['notification_sent'] = notification_sent
                if notification_sent:
                    logger.info("通知发送成功")
                else:
                    error_msg = "通知发送失败"
                    result['errors'].append(error_msg)
                    logger.error(error_msg)

            except Exception as e:
                error_msg = f"发送通知异常: {e}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
        else:
            logger.info("通知已禁用，跳过发送")

        # 4. 保存到数据库
        try:
            logger.info("保存历史记录到数据库...")
            # 确定通知方式
            notification_method = 'none'
            if result['notification_sent']:
                # 假设使用了 base64 方式（简化处理，后续可以从 notifier 获取实际方式）
                notification_method = 'base64'
            elif self.notification_enabled and self.notifier:
                notification_method = 'failed'

            record_id = self.db.add_record(
                trigger_type=trigger_type,
                trigger_time=datetime.now(),
                camera_path=Path(camera_path) if camera_path else None,
                screenshot_path=Path(screenshot_path) if screenshot_path else None,
                notification_sent=result['notification_sent'],
                notification_method=notification_method
            )

            if record_id > 0:
                logger.info(f"历史记录已保存 (ID: {record_id})")
                result['record_id'] = record_id
            else:
                logger.error("保存历史记录失败")

        except Exception as e:
            error_msg = f"保存历史记录异常: {e}"
            result['errors'].append(error_msg)
            logger.error(error_msg)

        # 5. 判断整体是否成功
        # 至少完成了拍照或截图，且没有严重错误
        has_capture = bool(camera_path or screenshot_path)
        result['success'] = has_capture

        logger.info(f"=== 监控任务执行完成 (成功: {result['success']}) ===")

        return result

    def test_all_components(self) -> Dict:
        """
        测试所有组件

        Returns:
            测试结果字典
        """
        test_result = {
            'camera': False,
            'screenshot': False,
            'notification': False
        }

        logger.info("=== 开始测试所有组件 ===")

        # 测试摄像头
        if self.camera:
            logger.info("测试摄像头...")
            test_result['camera'] = self.camera.test_camera()
            logger.info(f"摄像头测试: {'成功' if test_result['camera'] else '失败'}")
        else:
            logger.info("摄像头已禁用")

        # 测试截图
        if self.screenshot:
            logger.info("测试截图...")
            test_path = self.screenshot.capture()
            test_result['screenshot'] = bool(test_path)
            logger.info(f"截图测试: {'成功' if test_result['screenshot'] else '失败'}")
            if test_path:
                # 删除测试截图
                try:
                    Path(test_path).unlink()
                except:
                    pass
        else:
            logger.info("截图已禁用")

        # 测试通知
        if self.notifier:
            logger.info("测试通知...")
            test_result['notification'] = self.notifier.test_connection()
            logger.info(f"通知测试: {'成功' if test_result['notification'] else '失败'}")
        else:
            logger.info("通知已禁用")

        logger.info("=== 组件测试完成 ===")
        return test_result


if __name__ == '__main__':
    # 测试监控模块
    print("=== 监控模块测试 ===")

    monitor = Monitor()

    # 测试所有组件
    print("\n1. 测试所有组件...")
    test_results = monitor.test_all_components()
    for component, result in test_results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {component}: {'成功' if result else '失败'}")

    # 执行一次手动监控
    print("\n2. 执行手动监控...")
    result = monitor.execute(trigger_type='manual')
    print(f"  执行结果: {'成功' if result['success'] else '失败'}")
    if result['camera_path']:
        print(f"  摄像头照片: {result['camera_path']}")
    if result['screenshot_path']:
        print(f"  屏幕截图: {result['screenshot_path']}")
    if result['notification_sent']:
        print("  通知已发送")
    if result['errors']:
        print(f"  错误: {', '.join(result['errors'])}")
