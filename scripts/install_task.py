"""
安装 Windows 任务计划脚本
需要管理员权限运行
"""

import sys
import ctypes
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tasks.scheduler import WindowsScheduler
from src.utils.logger import Logger

logger = Logger()


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("DonTouchMe - Windows 任务计划安装")
    print("=" * 60)
    print()

    # 检查管理员权限
    if not is_admin():
        print("[错误] 需要管理员权限")
        print()
        print("请右键点击此脚本，选择「以管理员身份运行」")
        print("或在管理员命令提示符中运行：")
        print(f"  python {Path(__file__).name}")
        print()
        input("按回车键退出...")
        return 1

    print("[提示] 已获取管理员权限")
    print()

    # 创建调度器
    try:
        scheduler = WindowsScheduler()
    except Exception as e:
        print(f"[错误] 初始化调度器失败: {e}")
        input("按回车键退出...")
        return 1

    # 显示当前状态
    print("检查当前状态...")
    status = scheduler.check_status()
    print(f"  开机触发任务: {'已安装' if status['boot_task_exists'] else '未安装'}")
    print(f"  唤醒触发任务: {'已安装' if status['wake_task_exists'] else '未安装'}")
    print()

    # 确认安装
    if status['boot_task_exists'] or status['wake_task_exists']:
        print("[警告] 检测到已安装的任务，将会被覆盖")
        response = input("是否继续安装？(y/n): ").lower()
        if response != 'y':
            print("安装已取消")
            input("按回车键退出...")
            return 0
        print()

    # 安装任务
    print("开始安装任务计划...")
    print("-" * 60)

    print("\n1. 安装开机触发任务...")
    boot_success, wake_success = scheduler.install_all()

    print("\n" + "-" * 60)

    # 显示结果
    if boot_success and wake_success:
        print("\n[成功] 所有任务计划安装成功！")
        print()
        print("已安装的任务:")
        print(f"  • {scheduler.TASK_NAME_BOOT} - 开机时自动运行")
        print(f"  • {scheduler.TASK_NAME_WAKE} - 从休眠唤醒时自动运行")
        print()
        print("您现在可以：")
        print("  1. 重启电脑测试开机触发")
        print("  2. 让电脑进入休眠，然后唤醒测试唤醒触发")
        print("  3. 查看日志文件: logs/dontouchme_YYYYMMDD.log")
        print()
        print("卸载方法:")
        print(f"  python scripts/uninstall_task.py")

    elif boot_success:
        print("\n[部分成功] 开机任务安装成功，但唤醒任务安装失败")
        print()
        print("开机任务已安装，重启电脑后将自动运行")
        print("唤醒任务安装失败，请查看日志了解详情")

    elif wake_success:
        print("\n[部分成功] 唤醒任务安装成功，但开机任务安装失败")
        print()
        print("唤醒任务已安装，从休眠唤醒后将自动运行")
        print("开机任务安装失败，请查看日志了解详情")

    else:
        print("\n[失败] 任务计划安装失败")
        print()
        print("可能的原因:")
        print("  1. 权限不足")
        print("  2. 系统配置问题")
        print("  3. Python 路径包含特殊字符")
        print()
        print("请查看日志文件了解详情: logs/dontouchme_YYYYMMDD.log")

    print()
    input("按回车键退出...")
    return 0 if (boot_success and wake_success) else 1


if __name__ == '__main__':
    sys.exit(main())
