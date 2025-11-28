@echo off
chcp 65001 >nul
echo ========================================
echo Inno Setup 安装检测工具
echo ========================================
echo.

:: 设置颜色
color 0E

:: 常见的 Inno Setup 安装路径
set "ISCC_PATH_6=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set "ISCC_PATH_5=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
set "ISCC_PATH_6_64=C:\Program Files\Inno Setup 6\ISCC.exe"

echo 正在检测 Inno Setup 安装状态...
echo.

set "FOUND=0"
set "ISCC_PATH="

:: 检测 Inno Setup 6 (x86)
if exist "%ISCC_PATH_6%" (
    echo ✅ 找到 Inno Setup 6 (x86)
    echo    路径: %ISCC_PATH_6%
    set "ISCC_PATH=%ISCC_PATH_6%"
    set "FOUND=1"
    goto :check_version
)

:: 检测 Inno Setup 6 (x64)
if exist "%ISCC_PATH_6_64%" (
    echo ✅ 找到 Inno Setup 6 (x64)
    echo    路径: %ISCC_PATH_6_64%
    set "ISCC_PATH=%ISCC_PATH_6_64%"
    set "FOUND=1"
    goto :check_version
)

:: 检测 Inno Setup 5
if exist "%ISCC_PATH_5%" (
    echo ✅ 找到 Inno Setup 5
    echo    路径: %ISCC_PATH_5%
    set "ISCC_PATH=%ISCC_PATH_5%"
    set "FOUND=1"
    goto :check_version
)

:: 未找到
:not_found
echo ❌ 未检测到 Inno Setup 安装
echo.
echo 请按照以下步骤操作：
echo 1. 阅读 Inno_Setup_安装指南.md
echo 2. 访问 https://jrsoftware.org/isdl.php
echo 3. 下载并安装 Inno Setup 6.x
echo 4. 重新运行本脚本验证
echo.
pause
exit /b 1

:check_version
echo.
echo ========================================
echo 版本信息
echo ========================================

:: 尝试获取版本信息
"%ISCC_PATH%" /? 2>&1 | findstr /i "version" >nul
if %errorlevel% == 0 (
    echo.
    "%ISCC_PATH%" /?
)

echo.
echo ========================================
echo 语言文件检测
echo ========================================

:: 检测语言文件目录
for %%P in ("%ISCC_PATH%") do set "INNO_DIR=%%~dpP"
set "LANG_DIR=%INNO_DIR%Languages\"

if exist "%LANG_DIR%" (
    echo.
    echo 可用的语言文件：
    dir /b "%LANG_DIR%*.isl" 2>nul
    echo.

    :: 检测中文语言文件
    if exist "%LANG_DIR%ChineseSimplified.isl" (
        echo ✅ 支持简体中文（ChineseSimplified.isl）
    ) else if exist "%LANG_DIR%ChineseSimp.isl" (
        echo ✅ 支持简体中文（ChineseSimp.isl）
    ) else (
        echo ⚠️  未检测到简体中文语言文件
        echo    使用英文界面（默认）
    )
)

echo.
echo ========================================
echo 检测结果
echo ========================================
echo.
echo ✅ Inno Setup 已正确安装
echo ✅ 可以开始生成安装包
echo.
echo 下一步操作：
echo 1. 双击运行 build_all.bat
echo 2. 等待生成完成
echo 3. 在 installer_output 目录找到安装包
echo.

pause
exit /b 0
