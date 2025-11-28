"""
DonTouchMe 主程序
电脑守护助手 - 当电脑开机或从休眠状态唤醒时，自动拍照、截图并发送微信通知
"""

import sys
import os
import argparse
import time
from pathlib import Path

# 设置 Windows 控制台输出为 UTF-8
if sys.platform == 'win32':
    import locale
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        # 如果 reconfigure 不可用，使用其他方法
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.monitor import Monitor
from src.utils.logger import Logger
from src.utils.config import get_config

logger = Logger()


def print_banner():
    """打印程序标题"""
    banner = """
╔══════════════════════════════════════╗
║        DonTouchMe - 电脑守护助手      ║
║    Don't Touch My Computer Monitor   ║
╚══════════════════════════════════════╝
"""
    print(banner)


def command_trigger(args):
    """
    触发监控任务

    Args:
        args: 命令行参数
    """
    trigger_type = args.type
    delay = args.delay

    logger.info(f"收到触发命令: 类型={trigger_type}, 延迟={delay}秒")

    # 如果配置了延迟，等待一段时间
    if delay > 0:
        logger.info(f"延迟 {delay} 秒后开始执行...")
        time.sleep(delay)

    # 执行监控
    monitor = Monitor()
    result = monitor.execute(trigger_type=trigger_type)

    # 显示结果
    if result['success']:
        print(f"\n[成功] 监控任务执行成功")
        print(f"  触发类型: {trigger_type}")
        print(f"  执行时间: {result['timestamp']}")

        if result['camera_path']:
            print(f"  摄像头照片: {result['camera_path']}")
        if result['screenshot_path']:
            print(f"  屏幕截图: {result['screenshot_path']}")
        if result['notification_sent']:
            print(f"  [成功] 微信通知已发送")
        else:
            print(f"  [失败] 微信通知发送失败或已禁用")

    else:
        print(f"\n[失败] 监控任务执行失败")
        if result['errors']:
            print("  错误信息:")
            for error in result['errors']:
                print(f"    - {error}")

    return 0 if result['success'] else 1


def command_test(args):
    """
    测试所有组件

    Args:
        args: 命令行参数
    """
    logger.info("开始测试所有组件...")

    print("\n正在测试所有组件...")
    print("=" * 50)

    monitor = Monitor()
    test_results = monitor.test_all_components()

    print("\n测试结果:")
    print("-" * 50)

    all_passed = True
    for component, result in test_results.items():
        status = "[成功]" if result else "[失败]"
        print(f"  {component.ljust(20)}: {status}")
        if not result:
            all_passed = False

    print("-" * 50)

    if all_passed:
        print("\n[成功] 所有组件测试通过")
        return 0
    else:
        print("\n[失败] 部分组件测试失败，请检查配置和日志")
        return 1


def command_config(args):
    """
    查看或修改配置

    Args:
        args: 命令行参数
    """
    config = get_config()

    if args.show:
        # 显示配置
        print("\n当前配置:")
        print("=" * 50)

        # 基本信息
        print(f"版本: {config.get('version', '未知')}")

        # 通知配置
        print("\n[通知]")
        print(f"  启用: {config.get('notification.enabled', False)}")
        print(f"  服务商: {config.get('notification.provider', 'pushplus')}")
        token = config.get('notification.token', '')
        if token and token != "请在此处填写您的 PushPlus Token":
            print(f"  Token: {'*' * 20}{token[-4:]}")
        else:
            print(f"  Token: 未配置")

        # 摄像头配置
        print("\n[摄像头]")
        print(f"  启用: {config.get('camera.enabled', True)}")
        print(f"  设备 ID: {config.get('camera.device_id', 0)}")
        print(f"  分辨率: {config.get('camera.resolution', [1280, 720])}")

        # 截图配置
        print("\n[截图]")
        print(f"  启用: {config.get('screenshot.enabled', True)}")
        print(f"  质量: {config.get('screenshot.quality', 85)}")

        # 触发配置
        print("\n[触发]")
        print(f"  开机触发: {config.get('trigger.on_boot', True)}")
        print(f"  唤醒触发: {config.get('trigger.on_wake', True)}")
        print(f"  延迟秒数: {config.get('trigger.delay_seconds', 10)}")

        print("=" * 50)

    elif args.set:
        # 修改配置
        key, value = args.set.split('=', 1)

        # 尝试转换值类型
        try:
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                value = float(value)
        except:
            pass  # 保持字符串

        # 设置配置
        if config.set(key, value):
            print(f"\n[成功] 配置已更新: {key} = {value}")
            print("配置文件已保存")
            return 0
        else:
            print(f"\n[失败] 配置更新失败: {key}")
            return 1

    return 0


def command_info(args):
    """
    显示程序信息

    Args:
        args: 命令行参数
    """
    from src import __version__, __author__

    print_banner()

    print(f"版本: {__version__}")
    print(f"作者: {__author__}")
    print()
    print("功能:")
    print("  - 自动监控电脑开机和休眠唤醒")
    print("  - 摄像头自动拍照")
    print("  - 屏幕自动截图")
    print("  - 微信通知推送")
    print()
    print("使用方法:")
    print("  python src/main.py --help")
    print()
    print("配置文件:")
    config = get_config()
    print(f"  {config.config_path}")
    print()
    print("更多信息请访问: https://github.com/yourusername/DonTouchMe")

    return 0


def command_install(args):
    """
    安装 Windows 任务计划

    Args:
        args: 命令行参数
    """
    import ctypes

    # 检查是否为 Windows 系统
    if sys.platform != 'win32':
        print("[错误] 此功能仅支持 Windows 系统")
        return 1

    # 检查管理员权限
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        print("[错误] 需要管理员权限")
        print()
        print("请以管理员身份运行命令提示符，然后再次执行此命令")
        print("或者直接运行安装脚本：")
        print("  scripts/install_task.py (右键 -> 以管理员身份运行)")
        return 1

    # 导入调度器
    from src.tasks.scheduler import WindowsScheduler

    print("\n=== 安装 Windows 任务计划 ===\n")

    try:
        scheduler = WindowsScheduler()

        # 显示当前状态
        status = scheduler.check_status()
        print("当前状态:")
        print(f"  开机触发任务: {'已安装' if status['boot_task_exists'] else '未安装'}")
        print(f"  唤醒触发任务: {'已安装' if status['wake_task_exists'] else '未安装'}")
        print()

        # 安装任务
        print("正在安装任务计划...")
        boot_success, wake_success = scheduler.install_all()

        print()
        if boot_success and wake_success:
            print("[成功] 所有任务计划安装成功")
            print()
            print("已安装任务:")
            print(f"  - {scheduler.TASK_NAME_BOOT} (开机触发)")
            print(f"  - {scheduler.TASK_NAME_WAKE} (唤醒触发)")
            return 0
        elif boot_success or wake_success:
            print("[部分成功] 部分任务安装成功")
            return 1
        else:
            print("[失败] 任务计划安装失败，请查看日志")
            return 1

    except Exception as e:
        print(f"[错误] {e}")
        return 1


def command_uninstall(args):
    """
    卸载 Windows 任务计划

    Args:
        args: 命令行参数
    """
    import ctypes

    # 检查是否为 Windows 系统
    if sys.platform != 'win32':
        print("[错误] 此功能仅支持 Windows 系统")
        return 1

    # 检查管理员权限
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        print("[错误] 需要管理员权限")
        print()
        print("请以管理员身份运行命令提示符，然后再次执行此命令")
        print("或者直接运行卸载脚本：")
        print("  scripts/uninstall_task.py (右键 -> 以管理员身份运行)")
        return 1

    # 导入调度器
    from src.tasks.scheduler import WindowsScheduler

    print("\n=== 卸载 Windows 任务计划 ===\n")

    try:
        scheduler = WindowsScheduler()

        # 显示当前状态
        status = scheduler.check_status()
        print("当前状态:")
        print(f"  开机触发任务: {'已安装' if status['boot_task_exists'] else '未安装'}")
        print(f"  唤醒触发任务: {'已安装' if status['wake_task_exists'] else '未安装'}")
        print()

        if not status['boot_task_exists'] and not status['wake_task_exists']:
            print("[提示] 没有检测到已安装的任务")
            return 0

        # 卸载任务
        print("正在卸载任务计划...")
        boot_success, wake_success = scheduler.uninstall_all()

        print()
        if boot_success and wake_success:
            print("[成功] 所有任务计划已卸载")
            return 0
        elif boot_success or wake_success:
            print("[部分成功] 部分任务卸载成功")
            return 1
        else:
            print("[失败] 任务计划卸载失败，请查看日志")
            return 1

    except Exception as e:
        print(f"[错误] {e}")
        return 1


def main():
    """主函数"""
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description='DonTouchMe - 电脑守护助手',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # trigger 命令：触发监控
    trigger_parser = subparsers.add_parser('trigger', help='触发监控任务')
    trigger_parser.add_argument(
        '--type', '-t',
        choices=['boot', 'wake', 'manual'],
        default='manual',
        help='触发类型 (默认: manual)'
    )
    trigger_parser.add_argument(
        '--delay', '-d',
        type=int,
        default=0,
        help='延迟秒数 (默认: 0)'
    )
    trigger_parser.set_defaults(func=command_trigger)

    # test 命令：测试组件
    test_parser = subparsers.add_parser('test', help='测试所有组件')
    test_parser.set_defaults(func=command_test)

    # config 命令：配置管理
    config_parser = subparsers.add_parser('config', help='查看或修改配置')
    config_group = config_parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument('--show', '-s', action='store_true', help='显示当前配置')
    config_group.add_argument('--set', metavar='KEY=VALUE', help='设置配置项，如: notification.token=abc123')
    config_parser.set_defaults(func=command_config)

    # info 命令：显示信息
    info_parser = subparsers.add_parser('info', help='显示程序信息')
    info_parser.set_defaults(func=command_info)

    # install 命令：安装任务计划
    install_parser = subparsers.add_parser('install', help='安装 Windows 任务计划（需要管理员权限）')
    install_parser.set_defaults(func=command_install)

    # uninstall 命令：卸载任务计划
    uninstall_parser = subparsers.add_parser('uninstall', help='卸载 Windows 任务计划（需要管理员权限）')
    uninstall_parser.set_defaults(func=command_uninstall)

    # 解析参数
    args = parser.parse_args()

    # 如果没有指定命令，显示帮助
    if not args.command:
        print_banner()
        parser.print_help()
        return 0

    # 执行对应的命令
    try:
        return args.func(args)
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        print(f"\n[错误] {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
