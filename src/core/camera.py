"""
摄像头拍照模块
使用 opencv-python 进行摄像头操作
"""

import cv2
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

from ..utils.logger import Logger

logger = Logger()


class CameraCapture:
    """摄像头拍照类"""

    def __init__(self, device_id: int = 0, resolution: Tuple[int, int] = (1280, 720)):
        """
        初始化摄像头

        Args:
            device_id: 摄像头设备ID，默认0（内置摄像头）
            resolution: 分辨率，默认 (1280, 720)
        """
        self.device_id = device_id
        self.resolution = resolution

    def capture(self, save_path: Optional[Path] = None, warmup_frames: int = 5) -> Optional[Path]:
        """
        拍照并保存

        Args:
            save_path: 保存路径，如果为 None 则自动生成
            warmup_frames: 预热帧数，让摄像头稳定后再拍照

        Returns:
            保存的文件路径，失败返回 None
        """
        cap = None

        try:
            logger.info(f"正在打开摄像头 (设备 ID: {self.device_id})...")

            # 打开摄像头
            cap = cv2.VideoCapture(self.device_id)

            if not cap.isOpened():
                logger.error("无法打开摄像头，请检查设备是否可用")
                return None

            # 设置分辨率
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

            logger.debug(f"摄像头分辨率设置为: {self.resolution}")

            # 预热摄像头，让其自动调整曝光和白平衡
            logger.debug(f"预热摄像头 ({warmup_frames} 帧)...")
            for i in range(warmup_frames):
                ret = cap.read()
                if not ret[0]:
                    logger.warning(f"预热第 {i+1} 帧读取失败")
                time.sleep(0.1)  # 每帧间隔100ms

            # 拍照
            logger.info("正在拍照...")
            ret, frame = cap.read()

            if not ret or frame is None:
                logger.error("拍照失败，未能读取图像帧")
                return None

            # 生成保存路径
            if save_path is None:
                save_dir = Path(__file__).parent.parent.parent / 'data' / 'captures' / 'camera'
                save_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = save_dir / f"camera_{timestamp}.jpg"
            else:
                save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存图片（使用 imencode 支持中文路径）
            try:
                # 编码为 JPEG 格式
                success, encoded_img = cv2.imencode('.jpg', frame)

                if success:
                    # 写入文件（支持中文路径）
                    with open(save_path, 'wb') as f:
                        f.write(encoded_img.tobytes())
                    logger.info(f"拍照成功，保存到: {save_path}")
                    return save_path
                else:
                    logger.error(f"图像编码失败")
                    return None
            except Exception as ex:
                logger.error(f"保存图片失败: {save_path}, 错误: {ex}")
                return None

        except Exception as e:
            logger.error(f"摄像头拍照出错: {e}")
            return None

        finally:
            # 确保释放摄像头
            if cap is not None:
                cap.release()
                logger.debug("摄像头已释放")

    def test_camera(self) -> bool:
        """
        测试摄像头是否可用

        Returns:
            摄像头是否可用
        """
        try:
            cap = cv2.VideoCapture(self.device_id)
            is_opened = cap.isOpened()
            cap.release()

            if is_opened:
                logger.info(f"摄像头 {self.device_id} 可用")
            else:
                logger.warning(f"摄像头 {self.device_id} 不可用")

            return is_opened

        except Exception as e:
            logger.error(f"测试摄像头失败: {e}")
            return False

    @staticmethod
    def list_cameras(max_test: int = 5) -> list:
        """
        列出可用的摄像头设备

        Args:
            max_test: 最多测试的设备数量

        Returns:
            可用的设备ID列表
        """
        available_cameras = []

        for i in range(max_test):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    available_cameras.append(i)
                    cap.release()
            except:
                pass

        logger.info(f"找到 {len(available_cameras)} 个可用摄像头: {available_cameras}")
        return available_cameras


if __name__ == '__main__':
    # 测试摄像头功能
    print("=== 摄像头模块测试 ===")

    # 列出可用摄像头
    cameras = CameraCapture.list_cameras()
    print(f"可用摄像头: {cameras}")

    if cameras:
        # 测试拍照
        camera = CameraCapture(device_id=0)

        # 测试摄像头
        if camera.test_camera():
            # 拍照
            photo_path = camera.capture()
            if photo_path:
                print(f"拍照成功: {photo_path}")
            else:
                print("拍照失败")
        else:
            print("摄像头不可用")
    else:
        print("未找到可用摄像头")
