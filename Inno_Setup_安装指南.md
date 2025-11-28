# Inno Setup 安装指南

## 什么是 Inno Setup？

Inno Setup 是一个**免费**的 Windows 安装包制作工具，用于创建专业的软件安装程序。

**重要说明**：
- Inno Setup 是**开发工具**，只有您（开发者）需要安装
- 安装后，您可以生成 `DonTouchMe_Setup.exe` 安装包
- **最终用户不需要安装 Inno Setup**，只需双击您生成的安装包即可

---

## 下载 Inno Setup

### 官方下载地址
👉 https://jrsoftware.org/isdl.php

### 推荐版本
选择 **Inno Setup 6.x**（最新稳定版）

具体文件名类似：`innosetup-6.3.3.exe`（约 2-3 MB）

---

## 安装步骤

### 步骤 1：下载安装程序
1. 访问 https://jrsoftware.org/isdl.php
2. 找到 **"Inno Setup"** 下载链接
3. 点击下载 `innosetup-6.x.x.exe`

### 步骤 2：运行安装程序
1. 双击下载的 `innosetup-6.x.x.exe`
2. 如果出现 Windows 安全提示，点击"运行"

### 步骤 3：安装向导
1. **欢迎界面**
   - 点击 `Next >` 继续

2. **许可协议**
   - 选择 `I accept the agreement`
   - 点击 `Next >`

3. **选择安装位置**
   - 默认路径：`C:\Program Files (x86)\Inno Setup 6`
   - **建议使用默认路径**（我们的脚本会自动检测）
   - 点击 `Next >`

4. **选择组件**
   - 保持默认选择即可
   - 点击 `Next >`

5. **开始菜单文件夹**
   - 保持默认 `Inno Setup 6`
   - 点击 `Next >`

6. **准备安装**
   - 点击 `Install` 开始安装

7. **安装完成**
   - **不需要**勾选 `Launch Inno Setup` 查看帮助
   - 点击 `Finish` 完成

---

## 验证安装

### 方法 1：使用我们的验证脚本（推荐）
回到 DonTouchMe 项目目录，双击运行：
```
check_innosetup.bat
```

如果显示 `✅ Inno Setup 已正确安装`，说明安装成功！

### 方法 2：手动验证
1. 打开文件资源管理器
2. 导航到：`C:\Program Files (x86)\Inno Setup 6\`
3. 检查是否存在 `ISCC.exe` 文件

或者：
1. 按 `Win + R` 打开运行
2. 输入：`C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
3. 按回车，如果打开了命令行窗口，说明安装成功

---

## 下一步：生成安装包

安装完成后，返回 DonTouchMe 项目，双击运行：
```
build_all.bat
```

脚本会自动：
1. 使用 PyInstaller 打包程序
2. 使用 Inno Setup 生成安装包
3. 输出到 `installer_output/` 目录

生成的安装包：`DonTouchMe_Setup_v1.0.0.exe`

---

## 常见问题

### Q1: 安装时提示需要管理员权限？
**A**: 这是正常的，Inno Setup 会安装到 Program Files 目录。点击"是"授权即可。

### Q2: 安装完成后在哪里找到 Inno Setup？
**A**:
- 开始菜单：所有程序 → Inno Setup 6
- 安装目录：`C:\Program Files (x86)\Inno Setup 6\`

### Q3: 我需要学习如何使用 Inno Setup吗？
**A**: **不需要！** 我们已经创建好了配置文件 (`installer.iss`) 和自动化脚本。您只需运行 `build_all.bat` 即可。

### Q4: 卸载 Inno Setup 会影响已生成的安装包吗？
**A**: **不会！** 生成的安装包是独立的，可以自由分发。但如果您还需要更新程序并重新生成安装包，建议保留 Inno Setup。

### Q5: 安装包显示英文界面？
**A**: 这是正常的。为了最大兼容性，我们默认使用英文界面。如果需要中文界面，请参考 `installer.iss` 文件中的注释说明。

---

## 总结

✅ 安装 Inno Setup（一次性，约 2 分钟）
✅ 运行 `build_all.bat` 生成安装包
✅ 分发 `DonTouchMe_Setup_v1.0.0.exe` 给用户
✅ 用户双击安装，无需任何准备！

就是这么简单！🎉
