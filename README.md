# DonTouchMe - 电脑守护助手

当电脑开机或从休眠状态唤醒时，自动拍摄摄像头照片和屏幕截图，并通过微信推送通知您。

## 功能特性

- 🚀 **自动触发**：Windows 开机和休眠唤醒时自动运行
- 📷 **摄像头拍照**：自动拍摄电脑摄像头照片
- 🖥️ **屏幕截图**：捕获当前屏幕画面（支持多显示器）
- 💬 **微信通知**：通过 PushPlus 服务推送到微信
- 🎨 **图形界面**：系统托盘应用，方便快捷的操作
- ⚙️ **灵活配置**：支持 JSON 配置文件和 GUI 配置界面
- 📝 **历史记录**：保存所有拍照和截图的历史记录，支持查看和管理

## 快速开始

### 安装方式

#### 方式一：使用安装包（推荐，适合普通用户）

1. 下载最新版本的安装包 `DonTouchMe_Setup_v1.0.0.exe`
2. 双击运行安装程序，按照向导完成安装
3. 安装完成后，程序会自动启动系统托盘应用
4. 右键点击托盘图标，选择"配置"，设置您的 PushPlus Token

#### 方式二：从源码安装（适合开发者）

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/DonTouchMe.git
   cd DonTouchMe
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置 PushPlus Token**
   - 访问 [PushPlus 官网](http://www.pushplus.plus/) 注册并获取 Token
   - 编辑 `data/config.json` 文件，将 Token 填入 `notification.token` 字段

4. **启动程序**
   ```bash
   # 启动 GUI 应用
   python gui.py

   # 或使用命令行模式
   python src/main.py test
   ```

## 使用方法

### GUI 界面（推荐）

程序启动后会在系统托盘显示图标，右键点击可以：

- **立即触发**：手动执行一次拍照和通知
- **配置**：打开配置窗口，修改 Token、摄像头、截图等设置
- **历史记录**：查看所有拍照和截图的历史记录
- **任务管理**：管理 Windows 任务计划（开机和唤醒自动触发）
- **关于**：查看程序版本和信息
- **退出**：关闭程序

### 设置自动触发

在系统托盘右键菜单中选择"任务管理"，可以：

1. **安装任务计划**（需要管理员权限）
   - 开机触发：电脑启动后延迟 10 秒自动拍照
   - 唤醒触发：从睡眠/休眠状态恢复后自动拍照

2. **查看任务状态**：检查任务计划是否正常运行

3. **卸载任务计划**：移除自动触发功能

### 命令行模式（高级用户）

```bash
# 测试所有组件（摄像头、截图、通知）
python src/main.py test

# 手动触发一次监控
python src/main.py trigger --type manual

# 查看配置
python src/main.py config --show

# 修改配置
python src/main.py config --set notification.token=你的Token

# 安装/卸载任务计划
python src/main.py install
python src/main.py uninstall
```

## 配置说明

### 通过 GUI 配置（推荐）

在系统托盘图标右键菜单选择"配置"，可以方便地修改所有设置：

- **通知设置**：启用/禁用通知、配置 PushPlus Token、选择推送内容
- **摄像头设置**：启用/禁用摄像头、选择摄像头设备、设置分辨率
- **截图设置**：启用/禁用截图、设置图片质量
- **触发设置**：配置延迟时间、开机和唤醒触发开关
- **历史记录**：设置最大记录数、自动清理时间

### 配置文件

配置文件位于 `data/config.json`，高级用户可以直接编辑：

```json
{
  "notification": {
    "enabled": true,
    "provider": "pushplus",
    "token": "您的PushPlus_Token",
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
  }
}
```

## 系统要求

- **操作系统**：Windows 10 或更高版本
- **Python 版本**：3.8 或更高（仅源码运行需要）
- **硬件要求**：
  - 摄像头（用于拍照功能）
  - 至少 100MB 可用磁盘空间
  - 网络连接（用于微信推送）

## 常见问题

### 如何获取 PushPlus Token？

1. 访问 [PushPlus 官网](http://www.pushplus.plus/)
2. 使用微信扫码登录
3. 在控制台复制您的 Token
4. 将 Token 填入程序配置中

### 程序可以开机自启动吗？

可以！在系统托盘右键菜单选择"任务管理"，点击"安装任务计划"即可设置开机和唤醒自动拍照。

### 为什么需要管理员权限？

仅在安装/卸载 Windows 任务计划时需要管理员权限。日常使用不需要管理员权限。

### 摄像头拍照失败怎么办？

1. 检查摄像头是否被其他程序占用
2. 尝试更改配置中的 `camera.device_id`（0, 1, 2...）
3. 在配置中禁用摄像头功能，只使用截图功能

### 如何查看历史记录？

在系统托盘右键菜单选择"历史记录"，可以查看所有拍照和截图的历史，包括图片预览和通知状态。

## 技术栈

- **Python 3.8+**
- **图像处理**：opencv-python (摄像头)、mss (截图)、Pillow (图片处理)
- **GUI 框架**：PyQt5
- **Windows 集成**：pywin32、psutil
- **HTTP 请求**：requests
- **推送服务**：PushPlus

## 开发状态

- ✅ 核心功能（摄像头、截图、通知）
- ✅ Windows 任务计划自动触发
- ✅ SQLite 数据库历史记录
- ✅ PyQt5 系统托盘 GUI
- ✅ 打包和发布

## 许可证

MIT License

## 隐私声明

本程序所有数据仅保存在本地，不会上传到除 PushPlus 之外的任何第三方服务器。拍摄的照片和截图仅用于通知您电脑的使用状态，您可以随时查看或删除历史记录。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请在 GitHub 上提交 Issue。
