# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('core', 'core'),
        ('ui', 'ui'),
        ('models', 'models'),
        ('utils', 'utils'),   # Aseguramos que utils (rutas.py) esté incluido
        ('themes', 'themes'),
        ('assets', 'assets'), # Vital para los iconos
        ('data', 'data')      # Vital para los JSON iniciales
    ],
    hiddenimports=[
        'pandas', 
        'openpyxl', 
        'PySide6.QtCharts', 
        'PySide6.QtPrintSupport',
        'requests',
        'packaging',
        'packaging.version'
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
    [],
    exclude_binaries=True,
    name='SHILLONG_v3_PRO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Ponlo en True si quieres ver errores en una ventanita negra al probar
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/shillong_logov3.ico' # Asegúrate de que este archivo exista
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SHILLONG_v3_PRO',
)