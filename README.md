# DonTouchMe - 电脑守护助手

当电脑开机或从休眠状态唤醒时，自动拍摄摄像头照片和屏幕截图，并通过微信推送通知您。

## 功能特性

- 🚀 **自动触发**：Windows 开机和休眠唤醒时自动运行
- 📷 **摄像头拍照**：自动拍摄电脑摄像头照片
- 🖥️ **屏幕截图**：捕获当前屏幕画面
- 💬 **微信通知**：通过 PushPlus 服务推送到微信
- ⚙️ **灵活配置**：支持 JSON 配置文件和 GUI 界面（开发中）
- 📝 **历史记录**：保存所有拍照和截图的历史记录

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/DonTouchMe.git
cd DonTouchMe
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 PushPlus Token

1. 访问 [PushPlus 官网](http://www.pushplus.plus/) 注册并获取 Token
2. 编辑 `data/config.json` 文件
3. 将您的 Token 填入配置文件

## 使用方法

### 命令行模式

```bash
# 手动触发拍照和通知（测试）
python src/main.py trigger --type manual

# 测试所有组件
python src/main.py test

# 查看配置
python src/main.py config --show
```

### 配置 Windows 任务计划（自动触发）

#### 方法一：使用主程序（推荐）

```bash
# 以管理员身份运行命令提示符，然后执行：
python src/main.py install

# 卸载任务计划
python src/main.py uninstall
```

#### 方法二：使用安装脚本

右键点击 `scripts/install_task.py`，选择「以管理员身份运行」

或在管理员命令提示符中运行：

```bash
python scripts/install_task.py
```

安装成功后，程序将在以下情况自动运行：
- 电脑开机时
- 电脑从休眠/睡眠状态唤醒时

## 配置文件

配置文件位于 `data/config.json`，主要配置项：

```json
{
  "notification": {
    "enabled": true,
    "provider": "pushplus",
    "token_encrypted": "您的Token"
  },
  "camera": {
    "enabled": true,
    "device_id": 0
  },
  "screenshot": {
    "enabled": true,
    "quality": 85
  }
}
```

## 开发状态

- ✅ 阶段一：核心功能（命令行版本）- 已完成
- ✅ 阶段二：自动触发功能 - 已完成
- ⏳ 阶段三：数据持久化 - 计划中
- ⏳ 阶段四：GUI 界面 - 计划中

## 技术栈

- Python 3.8+
- opencv-python - 摄像头拍照
- mss - 屏幕截图
- Pillow - 图片处理
- requests - HTTP 请求
- PushPlus - 微信推送服务

## 许可证

MIT License

## 隐私声明

本程序所有数据仅保存在本地，不会上传到除 PushPlus 之外的任何第三方服务器。
拍摄的照片和截图仅用于通知您电脑的使用状态。
