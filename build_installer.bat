@echo off
chcp 65001 >nul
echo ========================================
echo DonTouchMe 安装包生成工具
echo ========================================
echo.

:: 设置颜色（可选）
color 0A

echo [步骤 1/4] 检查 Inno Setup 是否安装...
set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_PATH%" (
    echo.
    echo ❌ 错误: 未找到 Inno Setup!
    echo.
    echo 请按照以下步骤操作：
    echo 1. 访问 https://jrsoftware.org/isdl.php
    echo 2. 下载 Inno Setup 6.x
    echo 3. 安装到默认路径
    echo 4. 重新运行本脚本
    echo.
    pause
    exit /b 1
)
echo ✅ Inno Setup 已安装
echo.

echo [步骤 2/4] 检查可执行文件...
if not exist "dist\DonTouchMe\DonTouchMe.exe" (
    echo.
    echo ❌ 错误: 未找到可执行文件!
    echo.
    echo 请先打包程序：
    echo    python -m PyInstaller DonTouchMe.spec --clean
    echo.
    pause
    exit /b 1
)
echo ✅ 找到可执行文件
echo.

echo [步骤 3/4] 检查依赖文件...
if not exist "dist\DonTouchMe\_internal" (
    echo.
    echo ❌ 警告: _internal 文件夹不存在
    echo 可能导致安装包不完整
    echo.
    pause
)
echo ✅ 依赖文件完整
echo.

echo [步骤 4/4] 生成安装程序...
echo 正在编译 installer.iss...
echo.

"%ISCC_PATH%" installer.iss

echo.
if %errorlevel% == 0 (
    echo ========================================
    echo ✅ 安装包生成成功！
    echo ========================================
    echo.
    echo 输出位置:
    for %%F in (installer_output\*.exe) do (
        echo    %%F
        echo    大小: %%~zF 字节
    )
    echo.
    echo 接下来您可以：
    echo 1. 双击安装包测试安装流程
    echo 2. 分享给其他用户
    echo 3. 上传到 GitHub Releases
    echo.

    :: 询问是否打开输出目录
    set /p OPEN_FOLDER="是否打开输出文件夹? (Y/N): "
    if /i "%OPEN_FOLDER%"=="Y" (
        start explorer installer_output
    )
) else (
    echo ========================================
    echo ❌ 生成失败
    echo ========================================
    echo.
    echo 请检查上方错误信息
    echo.
)

echo.
pause
