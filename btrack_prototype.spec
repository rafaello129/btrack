# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

mediapipe_datas = collect_data_files("mediapipe")
mediapipe_hiddenimports = collect_submodules("mediapipe.python.solutions")


a = Analysis(
    ["src/main.py"],
    pathex=["."],
    binaries=[],
    datas=[("assets", "assets"), *mediapipe_datas],
    hiddenimports=[*mediapipe_hiddenimports],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BTrackPrototype",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="BTrackPrototype",
)
