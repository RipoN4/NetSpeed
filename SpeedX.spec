# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Specification File for NETSpeed (by RipoN)
Builds a standalone executable on Windows (.exe)
or an application bundle on macOS (.app).
"""

import sys

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('NetSpeed.png', '.'),
        ('NetSpeed.ico', '.'),
    ],
    hiddenimports=[
        'psutil',
        'icons',
        'config',
        'autostart',
        'monitor',
        'overlay_widget',
        'settings_dialog',
        'win_taskbar',
        'mac_menubar',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSvg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'torch',
        'IPython',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if sys.platform == 'darwin':
    # macOS Bundle
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='NETSpeed',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='NETSpeed'
    )
    app = BUNDLE(
        coll,
        name='NETSpeed.app',
        icon=None,
        bundle_identifier='com.ripon.netspeed',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSUIElement': 'True',  # Runs as Menu Bar background utility on macOS
        },
    )
else:
    # Windows Standalone One-File .exe
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='NETSpeed',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='NetSpeed.ico',
    )
