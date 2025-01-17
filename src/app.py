import wx
import sys
import util
from os.path import join, abspath, dirname
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

ROOT_PATH = util.to_unicode(abspath(dirname(sys.argv[0])))
XRC_PATH = join(ROOT_PATH, 'resource', 'xrc')
LANG_PATH = join(ROOT_PATH, 'lang')
PUZZLE_PATH = join(ROOT_PATH, 'puzzle')

nCellSize = eval(util.config.get('APP', 'CellSize', '50'))
nAnswerCellSize = nCellSize*0.6
nLINE = 9
nGRID = 3
rgLINE = range(nLINE)
rgGRID = range(nGRID)

clBgFocus = '#C1DEA3'
clBgOver  = '#8FD6FF'
clBgNormal = '#EEEEEE'
clBgDefault = '#E3EDFF'
clTextNormal = '#000000'
clTextDefault = '#000000'

locale = wx.Locale()

bShowAutoTip      = eval(util.config.get('APP', 'ShowAutoTip', 'False'))
bRecordLastPuzzle = eval(util.config.get('APP', 'RecordLastPuzzle', 'False'))
lastPuzzle        = eval(util.config.get('APP', 'LastPuzzle', '{}'))

def SetConfig():
    util.config.set('APP', 'RecordLastPuzzle', bRecordLastPuzzle)
    util.config.set('APP', 'LastPuzzle',       str(lastPuzzle))
    util.config.set('APP', 'ShowAutoTip',      bShowAutoTip)
    util.config.set('APP', 'CellSize',         str(nCellSize))

