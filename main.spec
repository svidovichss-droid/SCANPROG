# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Определяем архитектуру
is_64bits = sys.maxsize > 2**32
arch = 'x64' if is_64bits else 'x86'

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[
        (f'dlls/{arch}/libdmtx.dll', '.'),
    ],
    datas=[
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'cv2',
        'PIL',
        'numpy',
        'pylibdmtx',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DataMatrix-Quality-Scanner',
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
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)