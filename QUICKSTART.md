# DonTouchMe 快速入门指南

## 阶段一：命令行版本（已完成）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 PushPlus Token

1. 访问 [PushPlus 官网](http://www.pushplus.plus/)
2. 微信扫码关注并获取 Token
3. 编辑 `data/config.json`，填入您的 Token：

```json
{
  "notification": {
    "token": "您的Token"
  }
}
```

### 3. 测试程序

#### 查看程序信息
```bash
python src/main.py info
```

#### 测试所有组件
```bash
python src/main.py test
```

#### 查看当前配置
```bash
python src/main.py config --show
```

#### 手动触发监控
```bash
# 手动触发（测试用）
python src/main.py trigger --type manual

# 模拟开机触发
python src/main.py trigger --type boot

# 模拟唤醒触发
python src/main.py trigger --type wake
```

## 阶段二：自动触发功能（已完成）

### 4. 安装 Windows 任务计划

#### 方法一：使用主程序命令（推荐）

以管理员身份运行命令提示符：
1. 按 `Win + X`，选择「Windows PowerShell (管理员)」或「命令提示符 (管理员)」
2. 切换到项目目录
3. 执行安装命令：

```bash
cd "D:\桌面\总\项目\计算机\DonTouchMe"
python src/main.py install
```

#### 方法二：使用安装脚本

右键点击 `scripts/install_task.py`，选择「以管理员身份运行」

### 5. 验证安装

#### 查看任务计划是否安装成功

打开「任务计划程序」（按 Win + R，输入 `taskschd.msc`），查看是否有：
- `DonTouchMe_Boot` - 开机触发任务
- `DonTouchMe_Wake` - 休眠唤醒触发任务

#### 测试自动触发

**测试开机触发：**
1. 重启电脑
2. 开机后等待约 10 秒
3. 查看日志文件：`logs/dontouchme_YYYYMMDD.log`
4. 如果配置了 Token，您将收到微信通知

**测试唤醒触发：**
1. 让电脑进入休眠（开始菜单 → 电源 → 休眠）
2. 按电源键唤醒电脑
3. 等待约 5 秒
4. 查看日志文件和微信通知

### 6. 卸载任务计划

如需卸载自动触发功能：

```bash
# 以管理员身份运行
python src/main.py uninstall
```

### 7. 可用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `info` | 显示程序信息 | `python src/main.py info` |
| `test` | 测试所有组件 | `python src/main.py test` |
| `config --show` | 查看配置 | `python src/main.py config --show` |
| `config --set` | 修改配置 | `python src/main.py config --set camera.enabled=false` |
| `trigger` | 触发监控 | `python src/main.py trigger --type boot` |
| `install` | 安装任务计划 | `python src/main.py install` (需要管理员权限) |
| `uninstall` | 卸载任务计划 | `python src/main.py uninstall` (需要管理员权限) |

### 8. 配置说明

编辑 `data/config.json` 可以修改以下配置：

#### 通知设置
```json
"notification": {
  "enabled": true,          // 是否启用通知
  "token": "您的Token",     // PushPlus Token
  "send_camera": true,      // 是否发送摄像头照片
  "send_screenshot": true   // 是否发送截图
}
```

#### 摄像头设置
```json
"camera": {
  "enabled": true,          // 是否启用摄像头
  "device_id": 0,           // 设备 ID（0 为默认）
  "resolution": [1280, 720], // 分辨率
  "save_local": true        // 是否保存到本地
}
```

#### 截图设置
```json
"screenshot": {
  "enabled": true,          // 是否启用截图
  "save_local": true,       // 是否保存到本地
  "quality": 85             // JPEG 质量（1-100）
}
```

#### 触发设置
```json
"trigger": {
  "on_boot": true,          // 是否在开机时触发
  "on_wake": true,          // 是否在唤醒时触发
  "delay_seconds": 10       // 延迟秒数（等待系统稳定）
}
```

### 9. 文件位置

- **配置文件**: `data/config.json`
- **摄像头照片**: `data/captures/camera/`
- **屏幕截图**: `data/captures/screen/`
- **日志文件**: `logs/dontouchme_YYYYMMDD.log`

### 10. 常见问题

#### Q: 安装任务计划提示「需要管理员权限」？
A: 必须以管理员身份运行命令提示符或 PowerShell。

#### Q: 安装成功但没有触发？
A: 查看日志文件确认是否有错误，检查配置文件中的延迟时间设置。

#### Q: 摄像头拍照失败？
A: 检查摄像头是否被其他程序占用，或确认摄像头权限已开启。

#### Q: 收不到微信通知？
A: 检查 Token 是否正确配置，网络是否正常。

#### Q: 如何禁用摄像头或截图？
A: 在配置文件中设置 `camera.enabled` 或 `screenshot.enabled` 为 `false`。

#### Q: 如何查看任务计划是否正在运行？
A: 打开任务计划程序（`taskschd.msc`），查找 `DonTouchMe_Boot` 和 `DonTouchMe_Wake`。

#### Q: 如何手动触发测试？
A: 使用命令 `python src/main.py trigger --type boot`

### 11. 下一步

- 查看历史记录功能（阶段三 - 开发中）
- 使用 GUI 界面管理（阶段四 - 开发中）

## 技术支持

如有问题，请查看日志文件 `logs/` 或提交 Issue。

---

**注意事项：**
- 任务计划以系统权限运行，确保有足够权限访问摄像头
- 建议先手动测试确保所有功能正常后再安装任务计划
- 休眠唤醒触发在部分 Windows 版本上可能不稳定，建议以开机触发为主
