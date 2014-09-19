SudokuBoxer
=======
Cross platform Sudoku GUI game & solver. Develop by wxPython. Help you solve the Sudoku puzzle step by step

--------------

Version
--------------
0.7.x Alpha

Requirement
--------------
* [Python 2.7](https://www.python.org/download/releases/2.7)
* Windows
  * [wxPython 2.8 for Python 2.7](http://www.wxpython.org/download.php)
  * PyWin32 
* Ubuntu 12.04+
  * `sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n`
* [Tips] Please download both 32bit or 64bit


IDE
--------------
**PyCharm** Community Edition(Free) [Download Link](http://www.jetbrains.com/pycharm/download/)


Development
--------------
* `git clone <SudokuBoxer repo> <SudokuBoxerDir>`
* install requirement
* open `<SudokuBoxerDir>` by PyCharm
* configure Python Interpreter in PyCharm
* execute `root.py`


Build Package
--------------
* Windows & Linux
  * execute `python <SudokuBoxerDir>/build/build.py`
* Mac
  * execute `python <SudokuBoxerDir>/build/build.py` (not verified)


Language (i18n)
--------------
* Chinese
* English

##### Build & update language translating file (.PO)
 execute `python <SudokuBoxerDir>/build/build.py --update-po`


GUI Screenshots
--------------
* ![Alt text](https://raw.githubusercontent.com/Falldog/SudokuBoxer/master/.imgres/Screenshots_UI.png "Play UI") Play UI
* ![Alt text](https://raw.githubusercontent.com/Falldog/SudokuBoxer/master/.imgres/Screenshots_Solve1.png "Solve next step") Solve next step 1
* ![Alt text](https://raw.githubusercontent.com/Falldog/SudokuBoxer/master/.imgres/Screenshots_Solve2.png "Solve next step") Solve next step 2
* ![Alt text](https://raw.githubusercontent.com/Falldog/SudokuBoxer/master/.imgres/Screenshots_Solve3.png "Solve next step") Solve next step 3
* ![Alt text](https://raw.githubusercontent.com/Falldog/SudokuBoxer/master/.imgres/Screenshots_i18n.png "MultiLanguage") MultiLanguage (i18n)
