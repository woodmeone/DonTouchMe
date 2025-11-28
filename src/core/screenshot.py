"""
屏幕截图模块
使用 mss 进行高性能屏幕截图
"""

import mss
from pathlib import Path
from datetime import datetime
from typing import Optional
from PIL import Image

from ..utils.logger import Logger

logger = Logger()


class ScreenCapture:
    """屏幕截图类"""

    def __init__(self, quality: int = 85):
        """
        初始化截图器

        Args:
            quality: JPEG 质量，1-100，默认 85
        """
        self.quality = max(1, min(100, quality))

    def capture(self, save_path: Optional[Path] = None, monitor_number: int = 0) -> Optional[Path]:
        """
        截取屏幕并保存

        Args:
            save_path: 保存路径，如果为 None 则自动生成
            monitor_number: 显示器编号，0 表示所有显示器，1+ 表示具体显示器

        Returns:
            保存的文件路径，失败返回 None
        """
        try:
            logger.info("正在截取屏幕...")

            with mss.mss() as sct:
                # 获取显示器信息
                monitors = sct.monitors
                logger.debug(f"检测到 {len(monitors)-1} 个显示器")

                # 选择要截取的显示器
                if monitor_number < 0 or monitor_number >= len(monitors):
                    logger.warning(f"显示器编号 {monitor_number} 无效，使用默认（所有显示器）")
                    monitor_number = 0

                monitor = monitors[monitor_number]
                logger.debug(f"截取显示器 {monitor_number}: {monitor}")

                # 截图
                screenshot = sct.grab(monitor)

                # 转换为 PIL Image
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

                # 生成保存路径
                if save_path is None:
                    save_dir = Path(__file__).parent.parent.parent / 'data' / 'captures' / 'screen'
                    save_dir.mkdir(parents=True, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = save_dir / f"screen_{timestamp}.jpg"
                else:
                    save_path = Path(save_path)
                    save_path.parent.mkdir(parents=True, exist_ok=True)

                # 保存为 JPEG，可以压缩
                img.save(save_path, 'JPEG', quality=self.quality, optimize=True)

                logger.info(f"截图成功，保存到: {save_path}")
                logger.debug(f"截图分辨率: {img.size}, 质量: {self.quality}")

                return save_path

        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None

    def capture_all_monitors(self, save_dir: Optional[Path] = None) -> list:
        """
        分别截取所有显示器

        Args:
            save_dir: 保存目录

        Returns:
            保存的文件路径列表
        """
        screenshots = []

        try:
            with mss.mss() as sct:
                monitors = sct.monitors[1:]  # 跳过第0个（所有显示器）

                logger.info(f"检测到 {len(monitors)} 个显示器，开始分别截图...")

                for i, monitor in enumerate(monitors, start=1):
                    # 生成保存路径
                    if save_dir is None:
                        save_dir_path = Path(__file__).parent.parent.parent / 'data' / 'captures' / 'screen'
                    else:
                        save_dir_path = Path(save_dir)

                    save_dir_path.mkdir(parents=True, exist_ok=True)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = save_dir_path / f"screen_monitor{i}_{timestamp}.jpg"

                    # 截图并保存
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                    img.save(save_path, 'JPEG', quality=self.quality, optimize=True)

                    screenshots.append(save_path)
                    logger.info(f"显示器 {i} 截图成功: {save_path}")

                return screenshots

        except Exception as e:
            logger.error(f"多显示器截图失败: {e}")
            return screenshots

    def get_monitors_info(self) -> list:
        """
        获取所有显示器信息

        Returns:
            显示器信息列表
        """
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                logger.info(f"显示器信息: {monitors}")
                return monitors

        except Exception as e:
            logger.error(f"获取显示器信息失败: {e}")
            return []


if __name__ == '__main__':
    # 测试截图功能
    print("=== 屏幕截图模块测试 ===")

    screen = ScreenCapture(quality=85)

    # 获取显示器信息
    monitors = screen.get_monitors_info()
    print(f"检测到 {len(monitors)-1} 个显示器")

    # 截取所有显示器
    screenshot_path = screen.capture(monitor_number=0)
    if screenshot_path:
        print(f"截图成功: {screenshot_path}")
    else:
        print("截图失败")

    # 如果有多个显示器，测试分别截取
    if len(monitors) > 2:
        print("\n测试多显示器截图...")
        paths = screen.capture_all_monitors()
        print(f"成功截取 {len(paths)} 个显示器")
