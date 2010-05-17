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

nCellSize = eval(util.config.get('APP', 'CellSize', '50'))
nAnswerCellSize = nCellSize*0.6
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
    util.config.set('APP', 'CellSize',         str(nCellSize))