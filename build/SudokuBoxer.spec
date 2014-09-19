# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), os.path.join('..','root.py')],
             pathex=[os.path.join('..','src')])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build', 'SudokuBoxer', 'SudokuBoxer.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon=os.path.join('..', 'img', 'sudoku.ico'))
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=os.path.join('dist', 'SudokuBoxer'))
