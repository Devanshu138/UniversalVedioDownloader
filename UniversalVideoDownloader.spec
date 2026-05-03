# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_downloader.py'],
    pathex=[],
    binaries=[],
    datas=[('README.md', '.'), ('app.ico', '.'), ('instagram_profile.png', '.'), ('app_icon.png', '.'), ('K:\\Experiment\\venv\\Lib\\site-packages\\customtkinter', 'customtkinter/')],
    hiddenimports=['yt_dlp', 'you_get', 'streamlink', 'customtkinter', 'psutil'],
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
    [],
    exclude_binaries=True,
    name='UniversalVideoDownloader',
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
    icon=['app.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='UniversalVideoDownloader',
)
