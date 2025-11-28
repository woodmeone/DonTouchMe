# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

DonTouchMe 是一个 Windows 电脑守护助手，用于监控电脑访问情况。当电脑开机或从休眠状态唤醒时，自动拍摄摄像头照片和屏幕截图，并通过 PushPlus 服务推送微信通知，帮助用户了解谁在什么时候访问了电脑。

**核心功能**：摄像头拍照、屏幕截图、微信推送通知、历史记录管理、Windows 任务计划自动触发

## 常用命令

### 开发和测试
```bash
# 安装依赖
pip install -r requirements.txt

# 测试所有组件（验证摄像头、截图、通知功能）
python src/main.py test

# 手动触发一次监控（用于测试完整流程）
python src/main.py trigger --type manual

# 模拟开机触发（带延迟）
python src/main.py trigger --type boot --delay 10
```

### 配置管理
```bash
# 查看当前配置
python src/main.py config --show

# 修改配置项
python src/main.py config --set notification.token=你的PushPlus_Token
python src/main.py config --set camera.enabled=true
python src/main.py config --set screenshot.quality=85
```

### Windows 任务计划（自动触发）
```bash
# 安装任务计划（需要管理员权限）
# 创建两个任务：开机触发和休眠唤醒触发
python src/main.py install

# 卸载任务计划
python src/main.py uninstall

# 手动检查任务计划状态
powershell -Command "Get-ScheduledTask | Where-Object {$_.TaskName -like '*DonTouchMe*'} | Select-Object TaskName, State, LastRunTime | Format-Table"
```

### GUI 界面
```bash
# 启动系统托盘 GUI 应用
python gui.py
```

### 数据库操作
```bash
# 查看历史记录数据库
python -m src.core.database

# 使用检查脚本查看历史
python check_history.py
```

## 项目架构

### 目录结构
```
DonTouchMe/
├── src/
│   ├── core/              # 核心功能模块
│   │   ├── camera.py      # 摄像头拍照 (OpenCV)
│   │   ├── screenshot.py  # 屏幕截图 (mss)
│   │   ├── notifier.py    # 微信推送 (PushPlus API)
│   │   ├── database.py    # 历史记录 (SQLite)
│   │   └── monitor.py     # 中央协调器
│   ├── tasks/
│   │   └── scheduler.py   # Windows Task Scheduler 集成
│   ├── utils/             # 工具模块
│   │   ├── config.py      # 配置管理 (JSON)
│   │   ├── logger.py      # 日志系统（每日轮转）
│   │   └── image_helper.py # 图像处理
│   ├── gui/               # PyQt5 GUI 组件
│   │   ├── app.py         # 系统托盘应用
│   │   ├── config_window.py
│   │   ├── history_window.py
│   │   └── task_manager_dialog.py
│   └── main.py            # CLI 主入口
├── data/                  # 数据目录
│   ├── config.json        # 配置文件
│   ├── history.db         # SQLite 数据库
│   └── *.jpg / *.png      # 捕获的图像和截图
└── logs/                  # 日志文件（每日轮转）
```

### 核心工作流程

1. **触发方式**：
   - Windows 任务计划自动触发（开机/唤醒）
   - 命令行手动触发
   - GUI 界面触发

2. **执行流程**（Monitor 类协调）：
   ```
   触发 → Monitor.execute()
        ├── Camera.capture()      # 拍摄摄像头
        ├── Screenshot.capture()  # 截取屏幕
        ├── Notifier.send()       # 推送微信通知
        └── Database.save()       # 保存历史记录
   ```

3. **配置驱动**：所有功能通过 `data/config.json` 配置，支持运行时修改

### 关键设计模式

- **模块化分离**：每个核心功能（摄像头、截图、通知）独立为单独模块
- **中央协调**：`Monitor` 类负责协调所有组件，处理执行逻辑
- **配置管理**：`Config` 类提供点式路径访问（如 `config.get('notification.token')`）
- **双接口设计**：CLI 和 GUI 共享相同的核心逻辑

## 重要技术细节

### Windows 平台特性
- 使用 Windows Task Scheduler（`schtasks` 命令）实现自动触发
- 任务名称：`DonTouchMe_Boot` 和 `DonTouchMe_Wake`
- 需要管理员权限安装任务计划
- 使用 `ctypes.windll.shell32.IsUserAnAdmin()` 检查权限
- **唤醒检测机制**：监听 `Microsoft-Windows-Kernel-Power` Event ID 107（系统从睡眠/休眠恢复）

### UTF-8 编码处理
项目支持中文，所有入口文件（`src/main.py`, `gui.py`）都包含 UTF-8 配置：
```python
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
```

### PushPlus 集成
- 需要在 `data/config.json` 中配置 token
- 支持发送文本、图片或两者
- API 端点：`http://www.pushplus.plus/send`

### 日志系统
- 位置：`logs/` 目录
- 格式：`dontouchme_YYYYMMDD.log`（每日一个文件）
- 级别：DEBUG、INFO、WARNING、ERROR

### 数据库
- SQLite 数据库位于 `data/history.db`
- 主表：`history`（trigger_type, timestamp, camera_path, screenshot_path, notification_status）
- 支持历史查询和自动清理

## 开发注意事项

1. **测试流程**：修改代码后务必运行 `python src/main.py test` 验证所有组件

2. **配置优先**：不要硬编码路径或参数，使用配置文件

3. **异常处理**：所有组件都有独立的异常处理，部分失败不影响其他功能

4. **摄像头预热**：Camera 类会捕获并丢弃前几帧（warm-up），确保图像质量

5. **多显示器支持**：Screenshot 模块支持捕获所有显示器（通过 mss 库）

6. **GUI 线程安全**：GUI 使用独立线程执行监控任务，避免阻塞界面

## 技术栈

- **Python**: 3.8+
- **图像处理**: opencv-python (摄像头), mss (截图), Pillow (图片处理)
- **GUI**: PyQt5
- **HTTP**: requests
- **数据库**: SQLite3 (内置)
- **任务调度**: Windows Task Scheduler (通过 subprocess 调用 schtasks)
- **其他**: numpy (数值处理)

## 配置文件示例

`data/config.json` 关键配置项：
```json
{
  "notification": {
    "enabled": true,
    "provider": "pushplus",
    "token": "你的PushPlus_Token",
    "send_camera": true,
    "send_screenshot": false
  },
  "camera": {
    "enabled": true,
    "device_id": 0,
    "resolution": [640, 480]
  },
  "screenshot": {
    "enabled": true,
    "quality": 85
  },
  "trigger": {
    "on_boot": true,
    "on_wake": true,
    "delay_seconds": 10
  },
  "history": {
    "max_records": 1000,
    "auto_cleanup_days": 30
  }
}
```

## 项目阶段

- ✅ **阶段一**：核心功能（命令行版本）
- ✅ **阶段二**：自动触发功能（Windows 任务计划）
- ⏳ **阶段三**：数据持久化和历史管理
- ⏳ **阶段四**：GUI 界面增强
