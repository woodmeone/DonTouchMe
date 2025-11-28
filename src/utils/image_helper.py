"""
图片处理工具模块
提供图片压缩、Base64编码、图床上传等功能
支持混合智能降级方案
"""

import base64
import requests
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image
from io import BytesIO

from .logger import Logger

logger = Logger()


class ImageHelper:
    """图片处理助手"""

    # 支持的图床服务
    IMGBED_SERVICES = {
        'sm.ms': {
            'url': 'https://sm.ms/api/v2/upload',
            'method': 'POST',
            'file_field': 'smfile',
            'need_auth': False  # 免费使用不需要认证
        },
        'imgbb': {
            'url': 'https://api.imgbb.com/1/upload',
            'method': 'POST',
            'file_field': 'image',
            'need_auth': True  # 需要 API Key
        }
    }

    @staticmethod
    def compress_image(image_path: Path, max_size_kb: int = 100, quality: int = 85) -> Optional[Path]:
        """
        压缩图片到指定大小以下

        Args:
            image_path: 原图路径
            max_size_kb: 最大文件大小（KB）
            quality: 初始质量（1-100）

        Returns:
            压缩后的图片路径，如果已经满足要求则返回原路径
        """
        try:
            image_path = Path(image_path)

            # 检查文件大小
            current_size_kb = image_path.stat().st_size / 1024

            if current_size_kb <= max_size_kb:
                logger.debug(f"图片已满足大小要求: {current_size_kb:.2f}KB <= {max_size_kb}KB")
                return image_path

            logger.info(f"开始压缩图片: {current_size_kb:.2f}KB -> {max_size_kb}KB")

            # 打开图片
            img = Image.open(image_path)

            # 创建临时文件
            compressed_path = image_path.parent / f"{image_path.stem}_compressed{image_path.suffix}"

            # 尝试不同质量级别进行压缩
            for q in range(quality, 10, -5):
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=q, optimize=True)

                size_kb = len(buffer.getvalue()) / 1024

                if size_kb <= max_size_kb:
                    # 保存压缩后的图片
                    with open(compressed_path, 'wb') as f:
                        f.write(buffer.getvalue())

                    logger.info(f"压缩成功: 质量 {q}, 大小 {size_kb:.2f}KB")
                    return compressed_path

            # 如果压缩到质量10还是太大，尝试缩小分辨率
            logger.warning("降低质量无法达到目标大小，开始缩小分辨率")

            for scale in [0.8, 0.6, 0.4, 0.2]:
                new_size = (int(img.width * scale), int(img.height * scale))
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

                buffer = BytesIO()
                resized_img.save(buffer, format='JPEG', quality=70, optimize=True)

                size_kb = len(buffer.getvalue()) / 1024

                if size_kb <= max_size_kb:
                    with open(compressed_path, 'wb') as f:
                        f.write(buffer.getvalue())

                    logger.info(f"缩放压缩成功: 比例 {scale}, 大小 {size_kb:.2f}KB")
                    return compressed_path

            logger.error(f"无法将图片压缩到 {max_size_kb}KB 以下")
            return None

        except Exception as e:
            logger.error(f"压缩图片失败: {e}")
            return None

    @staticmethod
    def image_to_base64(image_path: Path) -> Optional[str]:
        """
        将图片转换为 Base64 编码

        Args:
            image_path: 图片路径

        Returns:
            Base64 编码字符串
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_str = base64.b64encode(image_data).decode('utf-8')

            logger.debug(f"图片转 Base64 成功，长度: {len(base64_str)}")
            return base64_str

        except Exception as e:
            logger.error(f"图片转 Base64 失败: {e}")
            return None

    @staticmethod
    def upload_to_smms(image_path: Path) -> Optional[str]:
        """
        上传图片到 SM.MS 图床

        Args:
            image_path: 图片路径

        Returns:
            图片 URL
        """
        try:
            logger.info(f"正在上传图片到 SM.MS: {image_path.name}")

            with open(image_path, 'rb') as f:
                files = {'smfile': f}
                response = requests.post(
                    'https://sm.ms/api/v2/upload',
                    files=files,
                    timeout=30
                )

            result = response.json()

            if result.get('success'):
                url = result['data']['url']
                logger.info(f"上传成功: {url}")
                return url
            else:
                error_msg = result.get('message', '未知错误')
                # 如果是已存在的图片，返回已有的URL
                if result.get('code') == 'image_repeated':
                    url = result['images']
                    logger.info(f"图片已存在，使用已有URL: {url}")
                    return url
                else:
                    logger.error(f"上传失败: {error_msg}")
                    return None

        except Exception as e:
            logger.error(f"上传到 SM.MS 失败: {e}")
            return None

    @staticmethod
    def prepare_images_for_notification(image_paths: List[Path], max_size_kb: int = 100) -> Tuple[str, List[str]]:
        """
        准备图片用于通知（混合智能降级方案）

        方案优先级：
        1. Base64 编码（小于 max_size_kb）
        2. 上传图床获取 URL
        3. 仅文字通知

        Args:
            image_paths: 图片路径列表
            max_size_kb: Base64 编码的最大图片大小（KB）

        Returns:
            (方式, 数据列表) - 方式可以是 'base64', 'url', 'text'
        """
        if not image_paths:
            return ('text', [])

        # 方案1：尝试 Base64（适合小图片）
        logger.info("尝试方案1: Base64 编码...")
        base64_list = []
        all_small_enough = True

        for img_path in image_paths:
            # 尝试压缩
            compressed_path = ImageHelper.compress_image(img_path, max_size_kb=max_size_kb)

            if compressed_path:
                base64_str = ImageHelper.image_to_base64(compressed_path)
                if base64_str:
                    base64_list.append(base64_str)
                else:
                    all_small_enough = False
                    break

                # 删除临时压缩文件
                if compressed_path != img_path:
                    try:
                        compressed_path.unlink()
                    except:
                        pass
            else:
                all_small_enough = False
                break

        if all_small_enough and base64_list:
            logger.info(f"方案1成功: 使用 Base64 编码 ({len(base64_list)} 张图片)")
            return ('base64', base64_list)

        # 方案2：尝试上传图床
        logger.info("方案1失败，尝试方案2: 上传图床...")
        url_list = []

        for img_path in image_paths:
            url = ImageHelper.upload_to_smms(img_path)
            if url:
                url_list.append(url)
            else:
                # 上传失败，降级到方案3
                logger.warning(f"图片上传失败: {img_path.name}")
                break

        if len(url_list) == len(image_paths):
            logger.info(f"方案2成功: 使用图床 URL ({len(url_list)} 张图片)")
            return ('url', url_list)

        # 方案3：仅文字通知
        logger.warning("方案2失败，降级到方案3: 仅文字通知")
        return ('text', [])

    @staticmethod
    def get_image_size_kb(image_path: Path) -> float:
        """获取图片文件大小（KB）"""
        try:
            return Path(image_path).stat().st_size / 1024
        except:
            return 0.0


if __name__ == '__main__':
    # 测试图片处理功能
    print("=== 图片处理工具测试 ===")

    # 需要有一个测试图片
    test_image = Path(__file__).parent.parent.parent / 'data' / 'captures' / 'camera'
    test_images = list(test_image.glob('*.jpg'))

    if test_images:
        test_img = test_images[0]
        print(f"测试图片: {test_img}")
        print(f"原始大小: {ImageHelper.get_image_size_kb(test_img):.2f}KB")

        # 测试压缩
        compressed = ImageHelper.compress_image(test_img, max_size_kb=100)
        if compressed:
            print(f"压缩后: {ImageHelper.get_image_size_kb(compressed):.2f}KB")

        # 测试 Base64
        base64_str = ImageHelper.image_to_base64(test_img)
        if base64_str:
            print(f"Base64 长度: {len(base64_str)}")

        # 测试混合方案
        method, data = ImageHelper.prepare_images_for_notification([test_img])
        print(f"推荐方案: {method}, 数据数量: {len(data)}")
    else:
        print("未找到测试图片，请先运行摄像头或截图模块生成测试图片")
