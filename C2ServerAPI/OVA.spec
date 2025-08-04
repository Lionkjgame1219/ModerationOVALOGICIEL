# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['interface.py'],
    pathex=[],
    binaries=[],
    datas=[('core', 'core')],
    hiddenimports=['PIL', 'PIL.ImageGrab', 'PIL.ImageDraw', 'PIL.ImageFont', 'pyperclip', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'PyQt5.QtCore', 'pytesseract', 'win32gui', 'win32con', 'win32process', 'win32api', 'discord'],
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
    name='OVA',
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
    icon=['ova.ico'],
)
