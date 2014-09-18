# -*- mode: python -*-
from os.path import join, abspath

a = Analysis([join('..', 'root.py')],
             pathex=[abspath(join('..', 'src'))],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='SudokuBoxer.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False , 
          icon=join('..', 'img', 'sudoku.ico'))
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='SudokuBoxer')
