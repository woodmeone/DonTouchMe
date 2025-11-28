"""
卸载 Windows 任务计划脚本
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
    print("DonTouchMe - Windows 任务计划卸载")
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

    # 检查是否有任务需要卸载
    if not status['boot_task_exists'] and not status['wake_task_exists']:
        print("[提示] 没有检测到已安装的任务")
        print()
        input("按回车键退出...")
        return 0

    # 确认卸载
    print("[警告] 即将卸载所有 DonTouchMe 任务计划")
    response = input("是否继续？(y/n): ").lower()
    if response != 'y':
        print("卸载已取消")
        input("按回车键退出...")
        return 0
    print()

    # 卸载任务
    print("开始卸载任务计划...")
    print("-" * 60)

    boot_success, wake_success = scheduler.uninstall_all()

    print("\n" + "-" * 60)

    # 显示结果
    if boot_success and wake_success:
        print("\n[成功] 所有任务计划已卸载")
        print()
        print("已卸载的任务:")
        print(f"  • {scheduler.TASK_NAME_BOOT}")
        print(f"  • {scheduler.TASK_NAME_WAKE}")
        print()
        print("程序将不再自动运行，但您仍可以手动使用:")
        print("  python src/main.py trigger --type manual")

    elif boot_success or wake_success:
        print("\n[部分成功] 部分任务卸载成功")
        print()
        if boot_success:
            print(f"  [成功] {scheduler.TASK_NAME_BOOT} 已卸载")
        if wake_success:
            print(f"  [成功] {scheduler.TASK_NAME_WAKE} 已卸载")
        print()
        print("部分任务卸载失败，请查看日志了解详情")

    else:
        print("\n[失败] 任务计划卸载失败")
        print()
        print("请查看日志文件了解详情: logs/dontouchme_YYYYMMDD.log")
        print()
        print("您也可以手动卸载:")
        print(f"  schtasks /Delete /TN {scheduler.TASK_NAME_BOOT} /F")
        print(f"  schtasks /Delete /TN {scheduler.TASK_NAME_WAKE} /F")

    print()
    input("按回车键退出...")
    return 0 if (boot_success and wake_success) else 1


if __name__ == '__main__':
    sys.exit(main())
