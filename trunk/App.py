#
#    SudokuBoxer is a Sudoku GUI game & solver
#
#    Copyright (C) 2010  Falldog
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import wx
import util
from PuzzleLoader import PuzzleLoaderDB

#--------------------------- Get Version ------------------------------#
try:
    f = open('version', 'r')
    lines = f.readlines()
    v  = lines[0].strip()
    vd = lines[1].strip()
except:
    v  = '0.7'
    vd = '0101'
VERSION = v
VERSION_DATE = vd
#-----------------------------------------------------------------------#

nLINE = 9
nGRID = 3
rgLINE = range(nLINE)
rgGRID = range(nGRID)

locale = wx.Locale()
puzzleLoader = PuzzleLoaderDB()

bShowAutoTip      = eval(util.config.get('APP', 'ShowAutoTip', 'False'))
bRecordLastPuzzle = eval(util.config.get('APP', 'RecordLastPuzzle', 'False'))
lastPuzzle        = eval(util.config.get('APP', 'LastPuzzle', '{}'))

def SetConfig():
    util.config.set('APP', 'RecordLastPuzzle', bRecordLastPuzzle)
    util.config.set('APP', 'LastPuzzle',       str(lastPuzzle))
    util.config.set('APP', 'ShowAutoTip',      bShowAutoTip)
    