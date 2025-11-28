"""
微信通知模块
使用 PushPlus 服务发送微信通知
支持混合图片发送方案
"""

import requests
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..utils.logger import Logger
from ..utils.image_helper import ImageHelper

logger = Logger()


class PushPlusNotifier:
    """PushPlus 微信通知器"""

    API_URL = "http://www.pushplus.plus/send"

    def __init__(self, token: str):
        """
        初始化通知器

        Args:
            token: PushPlus Token
        """
        self.token = token

    def send_text(self, title: str, content: str) -> bool:
        """
        发送纯文字通知

        Args:
            title: 标题
            content: 内容

        Returns:
            是否发送成功
        """
        try:
            logger.info(f"发送文字通知: {title}")

            data = {
                'token': self.token,
                'title': title,
                'content': content,
                'template': 'txt'
            }

            response = requests.post(self.API_URL, data=data, timeout=30)
            result = response.json()

            if result.get('code') == 200:
                logger.info("文字通知发送成功")
                return True
            else:
                error_msg = result.get('msg', '未知错误')
                logger.error(f"文字通知发送失败: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"发送文字通知异常: {e}")
            return False

    def send_with_base64(self, title: str, content: str, base64_list: List[str]) -> bool:
        """
        发送包含 Base64 图片的通知

        Args:
            title: 标题
            content: 内容
            base64_list: Base64 编码的图片列表

        Returns:
            是否发送成功
        """
        try:
            logger.info(f"发送 Base64 图片通知: {title} ({len(base64_list)} 张图片)")

            # 构建 HTML 内容
            html_content = f"<p>{content}</p>"
            for i, base64_str in enumerate(base64_list, 1):
                html_content += f'<p>图片 {i}:</p>'
                html_content += f'<img src="data:image/jpeg;base64,{base64_str}" style="max-width:100%;"/><br>'

            data = {
                'token': self.token,
                'title': title,
                'content': html_content,
                'template': 'html'
            }

            response = requests.post(self.API_URL, data=data, timeout=30)
            result = response.json()

            if result.get('code') == 200:
                logger.info("Base64 图片通知发送成功")
                return True
            else:
                error_msg = result.get('msg', '未知错误')
                logger.error(f"Base64 图片通知发送失败: {error_msg}")
                logger.error(f"完整响应: {result}")
                return False

        except Exception as e:
            logger.error(f"发送 Base64 图片通知异常: {e}")
            return False

    def send_with_urls(self, title: str, content: str, image_urls: List[str]) -> bool:
        """
        发送包含图片 URL 的通知

        Args:
            title: 标题
            content: 内容
            image_urls: 图片 URL 列表

        Returns:
            是否发送成功
        """
        try:
            logger.info(f"发送图片 URL 通知: {title} ({len(image_urls)} 张图片)")

            # 构建 HTML 内容
            html_content = f"<p>{content}</p>"
            for i, url in enumerate(image_urls, 1):
                html_content += f'<p>图片 {i}:</p>'
                html_content += f'<img src="{url}" style="max-width:100%;"/><br>'

            data = {
                'token': self.token,
                'title': title,
                'content': html_content,
                'template': 'html'
            }

            response = requests.post(self.API_URL, data=data, timeout=30)
            result = response.json()

            if result.get('code') == 200:
                logger.info("图片 URL 通知发送成功")
                return True
            else:
                error_msg = result.get('msg', '未知错误')
                logger.error(f"图片 URL 通知发送失败: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"发送图片 URL 通知异常: {e}")
            return False

    def send_with_images(self, title: str, content: str, image_paths: List[Path]) -> bool:
        """
        发送包含图片的通知（简化降级方案）

        方案优先级：
        1. Base64 编码（小于 100KB）
        2. 仅文字通知（Base64失败时降级）

        Args:
            title: 标题
            content: 内容
            image_paths: 图片路径列表

        Returns:
            是否发送成功
        """
        if not image_paths:
            return self.send_text(title, content)

        logger.info(f"准备发送图片通知 ({len(image_paths)} 张图片)...")

        # 使用混合智能降级方案准备图片
        # PushPlus限制消息内容不超过2万字，Base64编码后约15KB可满足要求
        method, data = ImageHelper.prepare_images_for_notification(image_paths, max_size_kb=15)

        if method == 'base64':
            # 尝试方案1: Base64 编码
            logger.info("尝试使用Base64方案发送图片...")
            if self.send_with_base64(title, content, data):
                return True

            # Base64失败，降级到纯文字
            logger.warning("Base64发送失败，降级到纯文字方案...")
            fallback_content = f"{content}\n\n注意：图片发送失败，请在程序中查看历史记录。"
            return self.send_text(title, fallback_content)

        else:
            # 图片过大，直接使用纯文字
            logger.info("图片过大，使用纯文字方案...")
            fallback_content = f"{content}\n\n注意：图片过大无法发送，请在程序中查看历史记录。"
            return self.send_text(title, fallback_content)

    def send_boot_notification(self, camera_path: Optional[Path] = None, screenshot_path: Optional[Path] = None) -> bool:
        """
        发送开机通知

        Args:
            camera_path: 摄像头照片路径
            screenshot_path: 屏幕截图路径

        Returns:
            是否发送成功
        """
        title = "电脑已开机"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"您的电脑已于 {current_time} 开机。"

        images = []
        if camera_path and camera_path.exists():
            images.append(camera_path)
        # 只发送摄像头照片，不发送屏幕截图（避免Base64过大）

        return self.send_with_images(title, content, images)

    def send_wake_notification(self, camera_path: Optional[Path] = None, screenshot_path: Optional[Path] = None) -> bool:
        """
        发送唤醒通知

        Args:
            camera_path: 摄像头照片路径
            screenshot_path: 屏幕截图路径

        Returns:
            是否发送成功
        """
        title = "电脑已从休眠唤醒"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"您的电脑已于 {current_time} 从休眠状态唤醒。"

        images = []
        if camera_path and camera_path.exists():
            images.append(camera_path)
        # 只发送摄像头照片，不发送屏幕截图（避免Base64过大）

        return self.send_with_images(title, content, images)

    def send_manual_notification(self, camera_path: Optional[Path] = None, screenshot_path: Optional[Path] = None) -> bool:
        """
        发送手动触发通知

        Args:
            camera_path: 摄像头照片路径
            screenshot_path: 屏幕截图路径

        Returns:
            是否发送成功
        """
        title = "DonTouchMe 手动触发"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"手动触发时间: {current_time}"

        images = []
        if camera_path and camera_path.exists():
            images.append(camera_path)
        # 只发送摄像头照片，不发送屏幕截图（避免Base64过大）

        return self.send_with_images(title, content, images)

    def test_connection(self) -> bool:
        """
        测试 PushPlus 连接

        Returns:
            连接是否正常
        """
        return self.send_text("DonTouchMe 测试", "这是一条测试消息，如果您收到这条消息，说明配置正确。")


if __name__ == '__main__':
    # 测试通知功能
    print("=== 微信通知模块测试 ===")
    print("请在 data/config.json 中配置您的 PushPlus Token")

    # 读取配置
    from ..utils.config import get_config
    config = get_config()
    token = config.get('notification.token', '')

    if not token or token == "请在此处填写您的 PushPlus Token":
        print("错误：未配置 PushPlus Token")
        print("请访问 http://www.pushplus.plus/ 获取 Token")
    else:
        notifier = PushPlusNotifier(token)

        # 测试连接
        print("测试连接...")
        if notifier.test_connection():
            print("测试成功！请查看您的微信")
        else:
            print("测试失败，请检查 Token 是否正确")
