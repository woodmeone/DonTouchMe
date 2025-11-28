@echo off
chcp 65001 >nul
echo ========================================
echo DonTouchMe 一键打包 + 安装包生成
echo ========================================
echo.

color 0B

echo 此脚本将执行以下操作：
echo 1. 使用 PyInstaller 打包程序
echo 2. 使用 Inno Setup 生成安装包
echo.
echo 预计耗时: 2-5 分钟
echo.

set /p CONFIRM="确认开始? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo 已取消
    pause
    exit /b 0
)

echo.
echo ========================================
echo 阶段 1: PyInstaller 打包程序
echo ========================================
echo.

echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python
    pause
    exit /b 1
)
echo ✅ Python 环境正常
echo.

echo [2/3] 检查 PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未安装 PyInstaller
    echo 正在安装...
    pip install pyinstaller
)
echo ✅ PyInstaller 已安装
echo.

echo [3/3] 打包程序...
echo 请稍候，这可能需要 1-2 分钟...
echo.

python -m PyInstaller DonTouchMe.spec --clean

if %errorlevel% neq 0 (
    echo.
    echo ❌ 打包失败
    pause
    exit /b 1
)

echo.
echo ✅ 程序打包完成
echo.

echo ========================================
echo 阶段 2: Inno Setup 生成安装包
echo ========================================
echo.

:: 调用安装包构建脚本
call build_installer.bat

echo.
echo ========================================
echo 🎉 全部完成！
echo ========================================
echo.

echo 生成的文件：
echo 1. 可执行程序: dist\DonTouchMe\DonTouchMe.exe
echo 2. 安装包: installer_output\DonTouchMe_Setup_v1.0.0.exe
echo.

echo 下一步建议：
echo 1. 测试安装包
echo 2. 测试程序功能
echo 3. 上传到 GitHub
echo.

pause
