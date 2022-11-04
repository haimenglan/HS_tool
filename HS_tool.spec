# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

search_path = ['C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1', 'C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1\\HS_GUI',
'C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1\\HS_client','C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1\\HS_tool_tool',
'C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1\\HS_universal',
]



a = Analysis(
    ['C:\\Users\\蓝海梦\\Desktop\\py_envir\\HS_4.1\\HS_tool.py'],
    pathex=search_path,
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name='HS_tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HS_tool',
)
