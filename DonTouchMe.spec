# -*- mode: python ; coding: utf-8 -*-
# DonTouchMe PyInstaller 打包配置

import sys
from pathlib import Path

block_cipher = None

# 收集 src 目录下所有 Python 模块文件
src_path = Path('src')
src_modules = []
for py_file in src_path.rglob('*.py'):
    if py_file.name != '__init__.py':
        # 转换为模块路径格式
        module_path = str(py_file.with_suffix('')).replace('\\', '.').replace('/', '.')
        src_modules.append(module_path)

a = Analysis(
    ['gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('data/config.json', 'data'),
    ],
    hiddenimports=[
        # Windows API
        'win32gui',
        'win32con',
        'win32api',
        # 图像处理
        'cv2',
        'mss',
        'mss.windows',
        'PIL',
        'PIL.Image',
        # GUI
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        # 其他
        'requests',
        'psutil',
        'numpy',
        # src 模块
        'src',
        'src.core',
        'src.core.camera',
        'src.core.screenshot',
        'src.core.notifier',
        'src.core.database',
        'src.core.monitor',
        'src.core.power_monitor',
        'src.utils',
        'src.utils.config',
        'src.utils.logger',
        'src.utils.image_helper',
        'src.utils.boot_detector',
        'src.utils.autostart',
        'src.tasks',
        'src.tasks.scheduler',
        'src.gui',
        'src.gui.app',
        'src.gui.config_window',
        'src.gui.history_window',
        'src.gui.task_manager_dialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DonTouchMe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DonTouchMe',
)
