@echo off
:: 切换到脚本所在目录
cd /d "%~dp0"

echo ========================================
echo DonTouchMe 安装包生成工具
echo ========================================
echo.

:: 设置颜色（可选）
color 0A

echo [步骤 1/4] 检�?Inno Setup 是否安装...

:: 尝试多个可能的安装路�?set "ISCC_PATH="
set "ISCC_PATH_6=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set "ISCC_PATH_5=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
set "ISCC_PATH_6_64=C:\Program Files\Inno Setup 6\ISCC.exe"

if exist "%ISCC_PATH_6%" (
    set "ISCC_PATH=%ISCC_PATH_6%"
) else if exist "%ISCC_PATH_6_64%" (
    set "ISCC_PATH=%ISCC_PATH_6_64%"
) else if exist "%ISCC_PATH_5%" (
    set "ISCC_PATH=%ISCC_PATH_5%"
)

if "%ISCC_PATH%"=="" (
    echo.
    echo �?错误: 未找�?Inno Setup!
    echo.
    echo 请按照以下步骤操作：
    echo 1. 阅读 Inno_Setup_安装指南.md
    echo 2. 或运�?check_innosetup.bat 检�?    echo 3. 访问 https://jrsoftware.org/isdl.php 下载安装
    echo.
    pause
    exit /b 1
)
echo �?Inno Setup 已安�?echo    路径: %ISCC_PATH%
echo.

echo [步骤 2/4] 检查可执行文件...
if not exist "dist\DonTouchMe\DonTouchMe.exe" (
    echo.
    echo �?错误: 未找到可执行文件!
    echo.
    echo 请先打包程序�?    echo    python -m PyInstaller DonTouchMe.spec --clean
    echo.
    pause
    exit /b 1
)
echo �?找到可执行文�?echo.

echo [步骤 3/4] 检查依赖文�?..
if not exist "dist\DonTouchMe\_internal" (
    echo.
    echo �?警告: _internal 文件夹不存在
    echo 可能导致安装包不完整
    echo.
    pause
)
echo �?依赖文件完整
echo.

echo [步骤 4/4] 生成安装程序...
echo 正在编译 installer.iss...
echo.

"%ISCC_PATH%" installer.iss

echo.
if %errorlevel% == 0 (
    echo ========================================
    echo �?安装包生成成功！
    echo ========================================
    echo.
    echo 输出位置:
    for %%F in (installer_output\*.exe) do (
        echo    %%F
        echo    大小: %%~zF 字节
    )
    echo.
    echo 接下来您可以�?    echo 1. 双击安装包测试安装流�?    echo 2. 分享给其他用�?    echo 3. 上传�?GitHub Releases
    echo.

    :: 询问是否打开输出目录
    set /p OPEN_FOLDER="是否打开输出文件�? (Y/N): "
    if /i "%OPEN_FOLDER%"=="Y" (
        start explorer installer_output
    )
) else (
    echo ========================================
    echo �?生成失败
    echo ========================================
    echo.
    echo 请检查上方错误信�?    echo.
)

echo.
pause
