# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['magyka.py', 'magyka.spec'],
             pathex=['C:\\Users\\notmu\\Desktop\\Code\\Python\\Magyka'],
             binaries=[],
             datas=[],
             hiddenimports=["pywintypes"],
             hookspath=[],
             runtime_hooks=[],
             excludes=["_bz2", "_hashlib", "_lzma", "_ssl", "_asyncio", "_decimal", "_elementtree", "_overlapped", "_queue", "_tkinter", "_testcapi", "_multiprocessing", "pyexpat", "unicodedata"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='magyka',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='magyka')
