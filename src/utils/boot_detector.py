"""
开机检测模块
判断程序是否在系统启动时启动
"""

import os
import psutil
from typing import Tuple

from .logger import Logger

logger = Logger()


def get_system_boot_time() -> float:
    """
    获取系统启动时间（时间戳）

    Returns:
        系统启动时间戳（秒）
    """
    try:
        boot_time = psutil.boot_time()
        return boot_time
    except Exception as e:
        logger.error(f"获取系统启动时间失败: {e}")
        return 0.0


def get_program_start_time() -> float:
    """
    获取当前程序启动时间（时间戳）

    Returns:
        程序启动时间戳（秒）
    """
    try:
        process = psutil.Process(os.getpid())
        create_time = process.create_time()
        return create_time
    except Exception as e:
        logger.error(f"获取程序启动时间失败: {e}")
        return 0.0


def is_boot_start(threshold_seconds: int = 120) -> bool:
    """
    判断程序是否在系统开机时启动

    如果程序启动时间距离系统启动时间在阈值内，判定为开机启动

    Args:
        threshold_seconds: 阈值（秒），默认 120 秒

    Returns:
        如果是开机启动返回 True，否则返回 False
    """
    boot_time = get_system_boot_time()
    program_time = get_program_start_time()

    if boot_time == 0.0 or program_time == 0.0:
        logger.warning("无法获取启动时间，假定不是开机启动")
        return False

    time_diff = program_time - boot_time

    logger.debug(
        f"开机检测: 系统启动时间={boot_time:.2f}, "
        f"程序启动时间={program_time:.2f}, "
        f"时间差={time_diff:.2f}秒, "
        f"阈值={threshold_seconds}秒"
    )

    is_boot = time_diff <= threshold_seconds

    if is_boot:
        logger.info(f"检测到开机启动（时间差 {time_diff:.2f} 秒 <= {threshold_seconds} 秒）")
    else:
        logger.debug(f"非开机启动（时间差 {time_diff:.2f} 秒 > {threshold_seconds} 秒）")

    return is_boot


def get_boot_info() -> Tuple[float, float, float]:
    """
    获取完整的开机信息

    Returns:
        (系统启动时间, 程序启动时间, 时间差)
    """
    boot_time = get_system_boot_time()
    program_time = get_program_start_time()
    time_diff = program_time - boot_time if (boot_time and program_time) else 0.0

    return boot_time, program_time, time_diff


if __name__ == '__main__':
    # 测试
    print("=== 开机检测模块测试 ===\n")

    boot_time, program_time, time_diff = get_boot_info()

    print(f"系统启动时间: {boot_time:.2f} ({psutil.datetime.datetime.fromtimestamp(boot_time)})")
    print(f"程序启动时间: {program_time:.2f} ({psutil.datetime.datetime.fromtimestamp(program_time)})")
    print(f"时间差: {time_diff:.2f} 秒\n")

    is_boot = is_boot_start(threshold_seconds=120)
    print(f"是否开机启动: {'是' if is_boot else '否'}")

    # 测试不同阈值
    print("\n测试不同阈值:")
    for threshold in [30, 60, 120, 180, 300]:
        result = is_boot_start(threshold_seconds=threshold)
        print(f"  阈值 {threshold:3d} 秒: {'开机启动' if result else '非开机启动'}")
