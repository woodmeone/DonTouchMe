"""
Windows 任务计划管理模块
使用 schtasks 命令行工具创建和管理定时任务
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from ..utils.logger import Logger

logger = Logger()


class WindowsScheduler:
    """Windows 任务计划管理器"""

    TASK_NAME_BOOT = "DonTouchMe_Boot"
    TASK_NAME_WAKE = "DonTouchMe_Wake"

    def __init__(self):
        """初始化调度器"""
        if sys.platform != 'win32':
            raise RuntimeError("此模块仅支持 Windows 系统")

        # 获取 Python 解释器路径和主程序路径
        self.python_exe = sys.executable
        self.main_script = Path(__file__).parent.parent / 'main.py'

        logger.info(f"Python 路径: {self.python_exe}")
        logger.info(f"主程序路径: {self.main_script}")

    def _run_command(self, command: list) -> Tuple[bool, str]:
        """
        运行命令

        Args:
            command: 命令列表

        Returns:
            (是否成功, 输出信息)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                logger.debug(f"命令执行成功: {' '.join(command)}")
                return True, output
            else:
                logger.error(f"命令执行失败: {' '.join(command)}")
                logger.error(f"输出: {output}")
                return False, output

        except Exception as e:
            error_msg = f"执行命令异常: {e}"
            logger.error(error_msg)
            return False, error_msg

    def task_exists(self, task_name: str) -> bool:
        """
        检查任务是否存在

        Args:
            task_name: 任务名称

        Returns:
            任务是否存在
        """
        command = ['schtasks', '/Query', '/TN', task_name]
        success, output = self._run_command(command)
        return success

    def create_boot_task(self, delay_seconds: int = 10) -> bool:
        """
        创建开机触发任务

        Args:
            delay_seconds: 延迟秒数

        Returns:
            是否创建成功
        """
        logger.info(f"创建开机触发任务: {self.TASK_NAME_BOOT}")

        # 检查任务是否已存在
        if self.task_exists(self.TASK_NAME_BOOT):
            logger.warning(f"任务已存在: {self.TASK_NAME_BOOT}，将先删除")
            self.delete_task(self.TASK_NAME_BOOT)

        # 构建命令
        # 使用 pythonw.exe 避免弹出控制台窗口
        pythonw_exe = self.python_exe.replace('python.exe', 'pythonw.exe')
        if not Path(pythonw_exe).exists():
            pythonw_exe = self.python_exe

        action = f'"{pythonw_exe}" "{self.main_script}" trigger --type boot --delay {delay_seconds}'

        command = [
            'schtasks',
            '/Create',
            '/TN', self.TASK_NAME_BOOT,
            '/TR', action,
            '/SC', 'ONSTART',  # 开机时触发
            '/RU', 'SYSTEM',  # 以系统权限运行
            '/RL', 'HIGHEST',  # 最高权限
            '/F'  # 强制创建（覆盖已存在的任务）
        ]

        success, output = self._run_command(command)

        if success:
            logger.info(f"开机触发任务创建成功: {self.TASK_NAME_BOOT}")
            return True
        else:
            logger.error(f"开机触发任务创建失败: {output}")
            return False

    def create_wake_task(self, delay_seconds: int = 5) -> bool:
        """
        创建休眠唤醒触发任务

        注意：Windows 任务计划对休眠唤醒的支持有限
        此方法使用事件触发器监听 Power-Troubleshooter 事件

        Args:
            delay_seconds: 延迟秒数

        Returns:
            是否创建成功
        """
        logger.info(f"创建休眠唤醒触发任务: {self.TASK_NAME_WAKE}")

        # 检查任务是否已存在
        if self.task_exists(self.TASK_NAME_WAKE):
            logger.warning(f"任务已存在: {self.TASK_NAME_WAKE}，将先删除")
            self.delete_task(self.TASK_NAME_WAKE)

        # 使用 pythonw.exe
        pythonw_exe = self.python_exe.replace('python.exe', 'pythonw.exe')
        if not Path(pythonw_exe).exists():
            pythonw_exe = self.python_exe

        action = f'"{pythonw_exe}" "{self.main_script}" trigger --type wake --delay {delay_seconds}'

        # 创建 XML 配置文件（用于事件触发）
        xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <EventTrigger>
      <Enabled>true</Enabled>
      <Subscription>&lt;QueryList&gt;&lt;Query Id="0" Path="System"&gt;&lt;Select Path="System"&gt;*[System[Provider[@Name='Microsoft-Windows-Power-Troubleshooter'] and EventID=1]]&lt;/Select&gt;&lt;/Query&gt;&lt;/QueryList&gt;</Subscription>
    </EventTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{pythonw_exe}</Command>
      <Arguments>"{self.main_script}" trigger --type wake --delay {delay_seconds}</Arguments>
    </Exec>
  </Actions>
</Task>'''

        # 保存 XML 到临时文件
        temp_xml = Path(__file__).parent.parent.parent / 'data' / 'wake_task.xml'
        temp_xml.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(temp_xml, 'w', encoding='utf-16') as f:
                f.write(xml_content)

            # 使用 XML 文件创建任务
            command = [
                'schtasks',
                '/Create',
                '/TN', self.TASK_NAME_WAKE,
                '/XML', str(temp_xml),
                '/F'
            ]

            success, output = self._run_command(command)

            if success:
                logger.info(f"休眠唤醒触发任务创建成功: {self.TASK_NAME_WAKE}")
                return True
            else:
                logger.error(f"休眠唤醒触发任务创建失败: {output}")
                return False

        except Exception as e:
            logger.error(f"创建唤醒任务异常: {e}")
            return False

        finally:
            # 删除临时 XML 文件
            try:
                if temp_xml.exists():
                    temp_xml.unlink()
            except:
                pass

    def delete_task(self, task_name: str) -> bool:
        """
        删除任务

        Args:
            task_name: 任务名称

        Returns:
            是否删除成功
        """
        logger.info(f"删除任务: {task_name}")

        if not self.task_exists(task_name):
            logger.warning(f"任务不存在: {task_name}")
            return True

        command = [
            'schtasks',
            '/Delete',
            '/TN', task_name,
            '/F'  # 强制删除，不提示确认
        ]

        success, output = self._run_command(command)

        if success:
            logger.info(f"任务删除成功: {task_name}")
            return True
        else:
            logger.error(f"任务删除失败: {output}")
            return False

    def install_all(self) -> Tuple[bool, bool]:
        """
        安装所有任务

        Returns:
            (开机任务是否成功, 唤醒任务是否成功)
        """
        logger.info("开始安装所有任务计划...")

        boot_success = self.create_boot_task()
        wake_success = self.create_wake_task()

        if boot_success and wake_success:
            logger.info("所有任务计划安装成功")
        elif boot_success:
            logger.warning("开机任务安装成功，但唤醒任务安装失败")
        elif wake_success:
            logger.warning("唤醒任务安装成功，但开机任务安装失败")
        else:
            logger.error("所有任务计划安装失败")

        return boot_success, wake_success

    def uninstall_all(self) -> Tuple[bool, bool]:
        """
        卸载所有任务

        Returns:
            (开机任务是否成功, 唤醒任务是否成功)
        """
        logger.info("开始卸载所有任务计划...")

        boot_success = self.delete_task(self.TASK_NAME_BOOT)
        wake_success = self.delete_task(self.TASK_NAME_WAKE)

        if boot_success and wake_success:
            logger.info("所有任务计划卸载成功")
        else:
            logger.warning("部分任务计划卸载失败")

        return boot_success, wake_success

    def check_status(self) -> dict:
        """
        检查任务状态

        Returns:
            状态字典
        """
        return {
            'boot_task_exists': self.task_exists(self.TASK_NAME_BOOT),
            'wake_task_exists': self.task_exists(self.TASK_NAME_WAKE),
        }


if __name__ == '__main__':
    # 测试任务计划管理
    print("=== Windows 任务计划管理测试 ===")

    scheduler = WindowsScheduler()

    # 检查状态
    print("\n1. 检查当前状态...")
    status = scheduler.check_status()
    print(f"  开机任务: {'已安装' if status['boot_task_exists'] else '未安装'}")
    print(f"  唤醒任务: {'已安装' if status['wake_task_exists'] else '未安装'}")

    # 测试创建任务（需要管理员权限）
    print("\n2. 测试创建任务（需要管理员权限）...")
    print("  提示：如果失败，请以管理员身份运行")
