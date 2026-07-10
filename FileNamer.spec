# PyInstaller spec for a standalone FileNamer.exe
# Run: pyinstaller FileNamer.spec

from PyInstaller.utils.hooks import collect_all

block_cipher = None

pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all('PyQt6')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=pyqt6_binaries,
    datas=pyqt6_datas,
    hiddenimports=pyqt6_hiddenimports + [
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FileNamer',
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
)
