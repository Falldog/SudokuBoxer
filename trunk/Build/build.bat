SET PYINSTALLER=.\pyinstaller\Build.py
SET ROOT_DIR=..
SET DIST_DIR=.\distSudokuBoxer
SET PUZZLE_DIR=.\puzzle
SET VERSION=%ROOT_DIR%\version

:: Process Multi-language
call MUI.bat

:: Make Pyinstaller spec
call makespec.bat

del %DIST_DIR% /q /f
python  -O %PYINSTALLER%  .\SudokuBoxer.spec
python  .\build_util.py generate_version %VERSION%

md  %DIST_DIR%\img
md  %DIST_DIR%\lang
md  %DIST_DIR%\puzzle
xcopy  ..\img     %DIST_DIR%\img /e /y
xcopy  ..\lang    %DIST_DIR%\lang /e /y
copy  %PUZZLE_DIR%\PuzzleDB-1000  %DIST_DIR%\puzzle\PuzzleDB

del %DIST_DIR%\lang\*.po
del %DIST_DIR%\lang\*.po~

copy %VERSION% %DIST_DIR%\

pause