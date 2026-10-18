# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for a standalone (one-file) filmweb executable.
#
# Build (from the repository root):
#
#     pip install -r requirements.txt pyinstaller
#     pyinstaller filmweb.spec
#
# Result: dist/filmweb (Linux) or dist/filmweb.exe (Windows).

a = Analysis(
    ["packaging/entrypoint.py"],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="filmweb",  # PyInstaller adds ".exe" on Windows
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,  # command line tool
    disable_windowed_traceback=False,
)
