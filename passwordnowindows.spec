# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files

# Collect any data files if needed
datas = [('icon.ico', '.')]

# Define the main script
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'winsdk.windows.security.credentials.ui',
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'pystray',
        'win32crypt',
        'Crypto.Cipher.AES',
        'PIL.Image',
        'sqlite3',
        'asyncio',
        'ctypes',
        'winreg'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='passwxrd',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # This is the key - set to False for --noconsole behavior
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Add these to ensure Windows Hello works properly
    icon='icon.ico',
    version_file=None,
    uac_admin=False,
    uac_uiaccess=False,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    win_use_manifest=True,  # Important for Windows Hello
    manifest=None,
    # Ensure the app can show dialogs
    windowed=True,
)

# Note: Only creating the no-console version now with hidden console support
