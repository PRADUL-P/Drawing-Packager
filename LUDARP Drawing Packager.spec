# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas_ctk, binaries_ctk, hidden_ctk = collect_all('customtkinter')
datas_dnd, binaries_dnd, hidden_dnd = collect_all('tkinterdnd2')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries_ctk + binaries_dnd,
    datas=[('zip-folder.ico', '.')] + datas_ctk + datas_dnd,
    hiddenimports=['tkinterdnd2', 'tkcalendar', 'babel.numbers', 'customtkinter', 'darkdetect', 'PIL'] + hidden_ctk + hidden_dnd,
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
    name='LUDARP Drawing Packager',
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
    icon=['zip-folder.ico'],
)
