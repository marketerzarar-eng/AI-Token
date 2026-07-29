# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller build spec for AI Token Auditor.
#
# Build (from the project root, one level above this file):
#     pyinstaller build/token_auditor.spec --noconfirm
#
# Produces dist/AI Token Auditor/AI Token Auditor.exe (onedir build).
# Onedir is used instead of onefile because:
#   - startup is faster (no self-extraction to a temp folder)
#   - Windows SmartScreen / AV heuristics are generally friendlier to
#     a normal folder + exe than a self-extracting single binary
#   - it's the layout expected by a signtool / installer step
#
# See build/PACKAGING.md for code-signing and "unknown publisher" guidance.

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all('PyQt6')

block_cipher = None

PROJECT_ROOT = Path(SPECPATH).parent

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=repo_dlls + pyqt6_binaries,
    datas=pyqt6_datas,
    hiddenimports=["tiktoken_ext.openai_public", "tiktoken_ext"] + pyqt6_hiddenimports
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
    name="AI Token Auditor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                 # UPX-packed exes trip AV heuristics more often
    console=False,              # no terminal window for a polished app feel
    icon=str(PROJECT_ROOT / "build" / "app_icon.ico"),
    version=str(PROJECT_ROOT / "build" / "version_info.txt"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="AI Token Auditor",
)
