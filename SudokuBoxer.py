import wx
import wx.lib.newevent
from copy import deepcopy
import os
import sqlite3
import anim
import util
import App
from PuzzleLoader import PuzzleLoaderDB
from boxer import SudokuBoxer, Step
from user import GetUserInfo
_ = wx.GetTranslation

LICENSE = '''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

class Number:
    def __init__(self, val=0):
        self.val = val
        self.isDefault = False
        self.valid = True
        self.autoTipList = []
        
    def __str__(self):
        return str(self.val)
    def __int__(self):
        return int(self.val)
    def __lt__(self, v):
        return self.val < v
    def __le__(self, v):
        return self.val <= v
    def __gt__(self, v):
        return self.val > v
    def __ge__(self, v):
        return self.val >= v
    def __eq__(self, v):
        return self.val == v
    def __ne__(self, v):
        return self.val != v
    def __sub__(self, v):
        return self.val-v
    def __add__(self, v):
        return self.val+v
        

class NumberBoard(wx.Panel, SudokuBoxer): 
    def __init__(self, parent, *argv, **argd):
        wx.Panel.__init__(self, parent, *argv, **argd)
        SudokuBoxer.__init__(self)
        #self.SetBackgroundColour('WHITE')
        
        self.BG_CL         = '#EEEEEE'
        self.BG_CL_DEFAULT = '#E3EDFF'
        self.BG_CL_OVER    = '#8FD6FF'
        self.BG_CL_FOCUS   = '#C1DEA3'
        self.CL_LINE_DOT   = '#777777'
        self.CL_LINE_SOLID = '#333333'
        self.CL_TEXT_VALID = '#000000'
        self.CL_TEXT_INVALID='#DD0000'
        self.CL_TEXT_AUTOTIP='#AAAAAA'
        self.CL_TEXT_HIGHLIGHT='#AA2222'
        
        self.NUM_SIZE = 50
        
        self.num = [ [] for n in App.rgLINE ]
        for i in App.rgLINE:
            self.num[i] = [ Number() for n in App.rgLINE ]
        self.default = deepcopy(self.num)
        self.answer = None
        
        self.steps = [] #record change history
        self.cur_step = -1
        
        self.highlightNum = 0
        self.focusPos     = (-1,-1)
        self.mouseOverPos = (-1,-1)
        
        self.testAnim = anim.AnimBase(self)
        
        self.font    = wx.Font( 20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Comic Sans MS' )
        self.fontTip = wx.Font( 10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Comic Sans MS' )
        self.brush_bg        = wx.Brush(self.BG_CL)
        self.brush_bg_defalt = wx.Brush(self.BG_CL_DEFAULT)
        self.brush_bg_over   = wx.Brush(self.BG_CL_OVER)
        self.brush_bg_focus  = wx.Brush(self.BG_CL_FOCUS)
        
        self.penTrans = wx.Pen('#000000', 1, wx.TRANSPARENT)
        
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.bmpBorder = None
        self.bmpNum = []
        self.bmpNumInvalid = []
        self.bmpNumAutoTip = []
        
        self.setDefault( [ [8,0,0, 0,0,5, 6,0,7] ,
                           [3,4,6, 7,0,0, 0,8,0] ,
                           [0,0,9, 0,0,0, 3,2,4] ,
                           [4,0,0, 0,0,0, 0,0,0] ,
                           [5,0,7, 8,3,4, 9,0,2] ,
                           [0,0,0, 0,0,0, 0,0,8] ,
                           [6,1,5, 0,0,0, 8,0,0] ,
                           [0,3,0, 0,0,6, 2,7,5] ,
                           [2,0,4, 9,0,0, 0,0,6] ] )
        self.bindEvent()
    
    def grid(self, x, y, num=None):
        if not num:
            num = self.num
        g = []
        for i in App.rgGRID:
            g.append( [0 for j in App.rgGRID] )
        
        for i in App.rgGRID:
            for j in App.rgGRID:
                g[i][j] = num[x*App.nGRID+i][y*App.nGRID+j]
        return g
        
    def bindEvent(self):
        self.Bind(wx.EVT_PAINT,        self.onDraw)
        self.Bind(wx.EVT_MOTION,       self.onMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN,    self.onMouseDown)
        self.Bind(wx.EVT_KEY_DOWN,     self.onKeyDown)
        self.Bind(wx.EVT_KEY_UP,       self.onKeyUp)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
    
    def unbindEvent(self, skipPaint=True):
        if not skipPaint:
            self.Unbind(wx.EVT_PAINT)
        self.Unbind(wx.EVT_MOTION)
        self.Unbind(wx.EVT_LEFT_DOWN)
        self.Unbind(wx.EVT_KEY_DOWN)
        self.Unbind(wx.EVT_KEY_UP)
        self.Unbind(wx.EVT_LEAVE_WINDOW)
        
    def setDefault(self, d, cur_d=[]):
        assert len(d)==len(self.default)
        #Default
        for i in App.rgLINE:
            for j in App.rgLINE:
                self.default[i][j].val = d[i][j]
                self.default[i][j].isDefault  =  d[i][j]!=0
                    
        #Current Number of puzzle
        if cur_d:
            for i in App.rgLINE:
                for j in App.rgLINE:
                    self.num[i][j].val = cur_d[i][j]
                    self.num[i][j].isDefault = self.default[i][j].isDefault
        else:
            self.num = deepcopy(self.default)
        self._updateAutoTip()
        self._initToDefault()
        self.Refresh()
    
    def _initToDefault(self):
        self.clearStepInfo()
        self.answer = None
        
    def clearToNull(self):
        num = []
        for i in App.rgLINE:
            num.append( [0 for j in App.rgLINE] )
        self.setDefault(num)
        
    def clearToDefault(self):
        self.num = deepcopy(self.default)
        self._updateAutoTip()
        self.clearStepInfo()
        self.Refresh()
        
    def clearStepInfo(self):
        self.steps = []
        self.cur_step = -1
    
    def queryAnswer(self):
        ori_num = deepcopy(self.num)
        
        while True:
            gotOne = False
            while True:
                if self.guessNext(mode='easy', silentFill=True):
                    gotOne = True
                else:
                    break
            
            if self.guessNext(mode='medium', silentFill=True):
                gotOne = True
            
            if not gotOne:
                break
        
        #[TODO] Fix, should finish and don't use brute method.
        if not self.checkFinish():
            self.boxerBrute( bCheckFromDefault=False )
            
        self.answer = self.num
        self.num = ori_num
        
    def guessNext(self, autoFill=True, silentFill=False, mode='easy'):
        ret = self.boxerNext(mode)
        if ret:
            self.dirtyCell(*self.focusPos) #dirty original focus cell
            pos, v = ret
            self.focusPos = pos
            if autoFill:
                if silentFill:
                    self._setVal(pos[0],pos[1],v)
                else:
                    self.setVal(pos[0],pos[1],v)
        return ret
    
    def getNum(self, i, j):
        return self.num[i][j]
    
    def _setVal(self, i, j, v):
        self.num[i][j].val = v
        self.num[i][j].valid = self.checkValidInput(v, i, j)
        
        #refresh
        if App.bShowAutoTip:
            self._updateAutoTip(i,j)
            self.Refresh()
        else:
            self.dirtyCell(i,j)
            
    def setVal(self, i, j, v):
        '''
        @(i,j) coordinate
        @v value
        '''
        assert 0 <= i < App.nLINE
        assert 0 <= j < App.nLINE
        
        if len(self.steps)-1 > self.cur_step:
            self.steps = self.steps[:self.cur_step+1]
        
        ori_v = self.num[i][j].val
        if ori_v == v:
            return
            
        self.steps.append( Step(i,j,ori_v,v) )
        self.cur_step = len(self.steps)-1
        self._setVal(i,j,v)
        
        #check finish
        if self.checkFinish():
            #wx.PostEvent(self, EVT_FINISH)
            evt = FunFinishEvent()
            wx.PostEvent(self, evt)
            
    def _updateAutoTip(self, i=-1, j=-1):
        if not App.bShowAutoTip:
            return
        if i==-1 or j==-1:
            #Update all
            for x in App.rgLINE:
                for y in App.rgLINE:
                    if self.num[x][y] == 0:
                        self.num[x][y].autoTipList = self.getValidNum(x,y)
        else:
            #Update grid & line base on (i,j)
            for x in App.rgGRID:
                for y in App.rgGRID:
                    posX, posY = int(i/3)*3 + x, int(j/3*3) + y
                    if self.num[posX][posY] == 0:
                        self.num[posX][posY].autoTipList = self.getValidNum(posX, posY)
            #Update vertical line
            for n in App.rgLINE:
                if self.num[i][n] == 0:
                    self.num[i][n].autoTipList = self.getValidNum(i,n)
            #Update horizantol line
            for n in App.rgLINE:
                if self.num[n][j] == 0:
                    self.num[n][j].autoTipList = self.getValidNum(n,j)
        pass
    
    def getDefaultPuzzle(self, bString=False):
        if not bString:
            return deepcopy(self.default)
        else:
            return util.Puzzle2Str(self.default)
            
    def getCurrentPuzzle(self, bString=False):
        if not bString:
            return deepcopy(self.num)
        else:
            return util.Puzzle2Str(self.num)
        
    def canUndo(self):
        return self.cur_step >= 0
        
    def canRedo(self):
        return self.cur_step < len(self.steps)-1
        
    def redo(self):
        if not self.canRedo():
            return
        self.cur_step+=1
        s = self.steps[self.cur_step]
        self._setVal(*s.infoRedo())
        
    def undo(self):
        if not self.canUndo():
            return
        s = self.steps[self.cur_step]
        self._setVal(*s.infoUndo())
        self.cur_step-=1
    
    def checkValid(self):
        '''
        Check the board is valid or not.
        Check is the line/grid is any number duplicate.
        Ex: 123456788 -> False, 8 duplicate
            123456789 -> True
        '''
        boolNumFalse = [False for i in App.rgLINE]
        #Check vertical & horizontal
        query_hor = lambda x,y: self.num[x][y]
        query_ver = lambda y,x: self.num[x][y]
        for query in [query_hor, query_ver]:
            for x in App.rgLINE:
                boolNum = deepcopy(boolNumFalse)
                for y in App.rgLINE:
                    n = query(x,y)
                    if n == 0: continue
                    if boolNum[n-1]:#duplicate
                        return False
                    boolNum[n-1] = True
        #Check grid
        for i in App.rgGRID:
            for j in App.rgGRID:
                boolNum = deepcopy(boolNumFalse)
                g = self.grid(i,j)
                for x in App.rgGRID:
                    for y in App.rgGRID:
                        n = g[x][y]
                        if n == 0: continue
                        if boolNum[n-1]:#duplicate
                            return False
                        boolNum[n-1] = True
        return True
        
    def checkFinish(self):
        boolNumFalse = [False for i in App.rgLINE]
        for i in App.rgLINE:
            for j in App.rgLINE:
                if self.num[i][j]==0:
                    return False
        return True
        
    def pt2pos(self, x, y):
        _x, _y = int(x / self.NUM_SIZE), int(y / self.NUM_SIZE)
        if 0 <= _x < App.nLINE or 0 <= _y < App.nLINE:
            return _x, _y
        else:
            return -1, -1
            
    def onKeyUp(self, evt):
        #print 'KeyUp', evt.GetKeyCode()
        key = evt.GetKeyCode()
        if key in [wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN]:
            x, y = 0, 0
            if   key==wx.WXK_LEFT:  x-=1
            elif key==wx.WXK_RIGHT: x+=1
            elif key==wx.WXK_UP:    y-=1
            elif key==wx.WXK_DOWN:  y+=1
            self.doMoveFocus(x,y)
            
            evt.Skip()
        pass
        
    def onKeyDown(self, evt):
        if self.focusPos != (-1,-1) and self.num[self.focusPos[0]][self.focusPos[1]].isDefault:
            return
        
        dirty = True
        num_idx = -1
        key = evt.GetKeyCode()
        if key < 256 and \
           key not in [wx.WXK_BACK, wx.WXK_RETURN, wx.WXK_ESCAPE, wx.WXK_SPACE, wx.WXK_DELETE]:
            key = chr(key)
        #print 'KeyDown', evt.GetKeyCode(), key
        
        try:
            num_list = [wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3, wx.WXK_NUMPAD4, 
                        wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, wx.WXK_NUMPAD8, wx.WXK_NUMPAD9]
            num_idx = num_list.index(key) + 1
        except ValueError:
            pass
            
        if num_idx > -1:
            self.setVal(self.focusPos[0], self.focusPos[1], num_idx)
            
        elif key in [ str(i) for i in range(1, 10) ]:
            self.setVal(self.focusPos[0], self.focusPos[1], int(key))
            
        elif key in [wx.WXK_DELETE, wx.WXK_BACK, wx.WXK_SPACE]:
            self.setVal(self.focusPos[0], self.focusPos[1], 0)
                
        else:
            dirty = False
        
        if dirty :
            evt.Skip()
    
    def doMoveFocus(self, x, y):
        if self.focusPos == (-1,-1):
            return
        curX, curY = self.focusPos
        newX, newY = curX, curY
        if x > 0:
            r = range(curX+1, App.nLINE)
        elif x < 0:
            r = range(curX-1, -1, -1)
        else:
            r = []
        for i in r:
            if self.default[i][curY] == 0:
                newX = i
                break
        
        if y > 0:
            r = range(curY+1, App.nLINE)
        elif y < 0:
            r = range(curY-1, -1, -1)
        else:
            r = []
        for i in r:
            if self.default[curX][i] == 0:
                newY = i
                break
        
        if self.focusPos != (newX, newY):
            self.dirtyCell(newX, newY)
            self.dirtyCell(*self.focusPos)
            self.focusPos = (newX, newY)
        
    def onMouseDown(self, evt):
        x,y = evt.GetPosition()
        pos = self.pt2pos(x,y)
        if self.focusPos != pos:
            self.dirtyCell(*pos)
            self.dirtyCell(*self.focusPos)
            self.focusPos = pos
        
        #Set highlight for one number
        num = self.getNum(*self.focusPos)
        if num != 0:
            if self.highlightNum == 0 or num != self.highlightNum:
                self.highlightNum = num.val
            else:
                self.highlightNum = 0
            self.Refresh()
            
        #self.testAnim.setType(anim.AnimBase.DECAY)
        #self.testAnim.assign(0)
        #self.testAnim.reset(1, 100)
        
    def onMouseMove(self, evt):
        x,y = evt.GetPosition()
        pos = self.pt2pos(x,y)
        if self.mouseOverPos != pos:
            self.dirtyCell(*self.mouseOverPos)
            self.dirtyCell(*pos)
            self.mouseOverPos = pos
            
    def onMouseLeave(self, evt):
        self.dirtyCell(*self.mouseOverPos)
        self.mouseOverPos = (-1, -1)
    
    def dirtyCell(self, i, j):
        if i == -1 or j == -1:
            return
        self.RefreshRect((i*self.NUM_SIZE, j*self.NUM_SIZE, self.NUM_SIZE, self.NUM_SIZE))
    
    def initBmpBorder(self):
        bmp = wx.EmptyBitmap(App.nLINE*self.NUM_SIZE, App.nLINE*self.NUM_SIZE)
        mdc = wx.MemoryDC()
        mdc.SelectObject(bmp)
        mdc.SetBackground(wx.BLACK_BRUSH) #set black for mask
        mdc.Clear()
        
        self.onDrawBorder(mdc)
        
        mdc.SelectObject(wx.NullBitmap) #release bmp
        bmp.SetMask(wx.Mask(bmp, wx.BLACK)) #Color mask
        self.bmpBorder = bmp
    
    def initBmpNum(self):
        size = self.NUM_SIZE
        content_list = [ {'bmp':self.bmpNum,        'font':self.font,    'textColor':self.CL_TEXT_VALID,   'size': size },
                         {'bmp':self.bmpNumInvalid, 'font':self.font,    'textColor':self.CL_TEXT_INVALID, 'size': size },
                         {'bmp':self.bmpNumAutoTip, 'font':self.fontTip, 'textColor':self.CL_TEXT_AUTOTIP, 'size': size/3 } ]
        
        for content in content_list:
            for i in range(1, 10):
                bmp = wx.EmptyBitmap(content['size'], content['size'])
                mdc = wx.MemoryDC()
                mdc.SelectObject(bmp)
                mdc.SetBackground(wx.WHITE_BRUSH) #set white for mask
                mdc.Clear()
                
                mdc.SetPen(wx.Pen('#000000', 1, wx.TRANSPARENT)) #Don't draw the border on BG rect
                mdc.SetFont( content['font'] )
                mdc.SetTextForeground( content['textColor'] )
                mdc.DrawLabel(str(i), (0,0,content['size'],content['size']), wx.ALIGN_CENTER)
                
                mdc.SelectObject(wx.NullBitmap) #release bmp
                bmp.SetMask(wx.Mask(bmp, wx.WHITE)) #Color mask
                content['bmp'].append(bmp)
        
    def onDraw(self, event):
        bpdc = wx.BufferedPaintDC(self)
        dc = wx.GCDC(bpdc)#for alpha effect
        
        #No use temp bitmap number, because the quality is sucks!
        #Replace by RefreshRect mechanism
        #if not self.bmpNum:
        #    self.initBmpNum()
        
        if not self.bmpBorder:
            self.initBmpBorder()
        
        self.onDrawText(dc)
        
        #draw border
        dc.DrawBitmap(self.bmpBorder, 0, 0, True)
        
    def onDrawText(self, dc):
        '''
        Paint text and background color
        '''
        r = self.GetUpdateRegion()
        dirtyR = r.GetBox()
        
        dc.SetFont(self.font)
        dc.SetPen(self.penTrans) #Don't draw the border on BG rect
        for i in App.rgLINE:
            for j in App.rgLINE:
                _r = (i*self.NUM_SIZE, j*self.NUM_SIZE, self.NUM_SIZE, self.NUM_SIZE)
                
                #skip the cell doesn't in dirty region
                if not( dirtyR[0] <= _r[0] and dirtyR[1] <= _r[1] and dirtyR[2] >= _r[2] and dirtyR[3] >= _r[3] ):
                    continue
                    
                if self.default[i][j] != 0:
                    dc.SetBrush(self.brush_bg_defalt)
                elif (i,j) == self.focusPos:
                    dc.SetBrush(self.brush_bg_focus)
                elif (i,j) == self.mouseOverPos:
                    dc.SetBrush(self.brush_bg_over)
                else:
                    dc.SetBrush(self.brush_bg)
                
                dc.DrawRectangle(*_r)
                dc.SetBrush(wx.NullBrush)
                
                if self.num[i][j] == 0:
                    if App.bShowAutoTip: self.onDrawAutoTip(dc,i,j)
                    continue
                
                dc.SetFont( self.font )
                if self.num[i][j] == self.highlightNum:
                    dc.SetTextForeground( self.CL_TEXT_HIGHLIGHT )
                elif self.num[i][j].valid:
                    dc.SetTextForeground( self.CL_TEXT_VALID )
                else:
                    dc.SetTextForeground( self.CL_TEXT_INVALID )
                dc.DrawLabel( str(self.num[i][j]), _r, wx.ALIGN_CENTER )
                
        dc.SetPen(wx.NullPen)
        pass
    
    def onDrawAutoTip(self, dc, i, j):
        l, t = i*self.NUM_SIZE, j*self.NUM_SIZE
        size = self.NUM_SIZE/3
        dc.SetFont( self.fontTip )
        dc.SetTextForeground( self.CL_TEXT_AUTOTIP )
        for n in self.num[i][j].autoTipList:
            r = (l + int((n-1)%3)*size, t + int((n-1)/3)*size,size,size)
            dc.DrawLabel(str(n), r, wx.ALIGN_CENTER)
        
    def onDrawBorder(self, dc):
        dc.SetBrush(wx.NullBrush)
        
        s  = self.NUM_SIZE
        sl = s * App.nLINE
        
        #Draw Dot Line
        dc.SetPen(wx.Pen(self.CL_LINE_DOT, 1, wx.DOT))
        for i in App.rgGRID:
            _x = i*s*App.nGRID
            dc.DrawLine( _x+s,   0, _x+s,   sl )
            dc.DrawLine( _x+s*2, 0, _x+s*2, sl )
            
            _y = i*s*App.nGRID
            dc.DrawLine( 0, _y+s,   sl, _y+s   )
            dc.DrawLine( 0, _y+s*2, sl, _y+s*2 )
        dc.SetPen(wx.NullPen)
        
        #Draw Solid Line
        w = 2 #line width
        dc.SetPen(wx.Pen(self.CL_LINE_SOLID, w, wx.SOLID))
        for i in range(App.nGRID+1):
            _pos = i*s*App.nGRID
            dc.DrawLine( _pos, 0, _pos, sl )
            dc.DrawLine( 0, _pos, sl, _pos )
        dc.SetPen(wx.NullPen)
        pass


class AnswerBoard(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE,
            useMetal=False,
            ):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        
        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)
        
        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle(wx.DIALOG_EX_METAL)
        
        
        self.board = NumberBoard(self, -1, pos=(0,0), size=(30*App.nLINE,30*App.nLINE))
        self.board.NUM_SIZE= 30
        self.board.font    = wx.Font( 12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Comic Sans MS' )
        self.board.fontTip = wx.Font( 6, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Comic Sans MS' )
        self.board.unbindEvent()
        #self.board.SetEvtHandlerEnabled(False)
    
    def setPuzzle(self, default, answer):
        self.board.setDefault(default, answer)
        

#Event
FunFinishEvent, EVT_FINISH = wx.lib.newevent.NewEvent()

#Menubar
ID_MENU_MODE_EASY    = wx.NewId()
ID_MENU_MODE_MEDIUM  = wx.NewId()
ID_MENU_MODE_HARD    = wx.NewId()
ID_MENU_MODE_EVIL    = wx.NewId()
ID_MENU_LANG_ENU     = wx.NewId()
ID_MENU_LANG_CHT     = wx.NewId()
ID_MENU_HELP_ABOUT   = wx.NewId()
ID_MENU_HELP_LINKPROJECT       = wx.NewId()
ID_MENU_OPT_RECORD_LAST_PUZZLE = wx.NewId()
ID_MENU_OPT_SHOW_AUTOTIP       = wx.NewId()

MODE_STR_MAP = { ID_MENU_MODE_EASY:   'easy',
                 ID_MENU_MODE_MEDIUM: 'medium',
                 ID_MENU_MODE_HARD:   'hard',
                 ID_MENU_MODE_EVIL:   'evil' }
MODE_ID_MAP  = { 'easy':   ID_MENU_MODE_EASY,
                 'medium': ID_MENU_MODE_MEDIUM,
                 'hard':   ID_MENU_MODE_HARD,
                 'evil':   ID_MENU_MODE_EVIL   }
LANG_STR_MAP = { ID_MENU_LANG_ENU:'ENU',
                 ID_MENU_LANG_CHT:'CHT' }
LANG_ID_MAP  = { 'ENU': ID_MENU_LANG_ENU,
                 'CHT': ID_MENU_LANG_CHT }

#Toolbar
ID_TOOLBAR_NEW       = wx.NewId()
ID_TOOLBAR_NEW_NULL  = wx.NewId()
ID_TOOLBAR_CHECK     = wx.NewId()
ID_TOOLBAR_GUESS     = wx.NewId()
ID_TOOLBAR_ANSWER    = wx.NewId()
ID_TOOLBAR_CHECKVALID= wx.NewId()
ID_TOOLBAR_CLEARALL  = wx.NewId()
ID_TOOLBAR_SELECT    = wx.NewId()
ID_TOOLBAR_SETUSER   = wx.NewId()
ID_TOOLBAR_RECORDTIME= wx.NewId()

class MainFrame(wx.Frame):
    """ MainFrame """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, 
                          title=title, 
                          size=(500,600), 
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX) )
        #set icon
        self.SetIcon( wx.Icon(u'./img/sudoku.ico', wx.BITMAP_TYPE_ICO) )
        
        self.board = NumberBoard(self, -1, pos=(10,80), size=(450,450))
        
        self.btn = wx.Button(self, -1, size=(10,10))
        self.btn.Show(False)
        
        #self.setDefault = self.board.setDefault
        mode = util.config.get('APP',  'level', 'easy')
        lang = util.config.get('LANG', 'language')
        self.curLangID = LANG_ID_MAP[lang]
        self.curModeID = MODE_ID_MAP[mode]
        self.puzzleID = 0
        
        self.initMenubar()
        self.initToolbar()
        self.initLayout()
        
        self.changeMode(self.curModeID)
        self.changeLang(self.curLangID, bInit=True)
        
        self.bindEvent()
        
        self.Centre()
        self.Show(True)
    
    def bindEvent(self):
        self.board.Bind(EVT_FINISH,          self.finish)
        self.board.Bind(wx.EVT_ENTER_WINDOW, self.onEnterBoard)
        self.Bind(wx.EVT_TIMER, self.onSpendTimer)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
    def initMenubar(self):
        self.menubar = wx.MenuBar()
        
        #Mode
        self.menuMode = wx.Menu()
        self.menuMode.Append(ID_MENU_MODE_EASY,   _('Easy'),  kind=wx.ITEM_RADIO)
        self.menuMode.Append(ID_MENU_MODE_MEDIUM, _('Medium'),kind=wx.ITEM_RADIO)
        self.menuMode.Append(ID_MENU_MODE_HARD,   _('Hard'),  kind=wx.ITEM_RADIO)
        self.menuMode.Append(ID_MENU_MODE_EVIL,   _('Evil'),  kind=wx.ITEM_RADIO)
        #Language
        self.menuLang = wx.Menu()
        self.menuLang.Append(ID_MENU_LANG_ENU, _('ENU'),            kind=wx.ITEM_RADIO)
        self.menuLang.Append(ID_MENU_LANG_CHT, _('CHT'), kind=wx.ITEM_RADIO)
        #Options
        self.menuOpt = wx.Menu()
        self.menuOpt.Append(ID_MENU_OPT_RECORD_LAST_PUZZLE, _('Record Last Puzzle'), kind=wx.ITEM_CHECK)
        self.menuOpt.Append(ID_MENU_OPT_SHOW_AUTOTIP,       _('Show AutoTip'),       kind=wx.ITEM_CHECK)
        #About
        _help = wx.Menu()
        _help.Append(ID_MENU_HELP_ABOUT, _('About'))
        _help.Append(ID_MENU_HELP_LINKPROJECT, _('Check New Version'))
        
        self.menubar.Append(self.menuMode,  _('Mode'))
        self.menubar.Append(self.menuLang,  _('Language'))
        self.menubar.Append(self.menuOpt,   _('Options'))
        self.menubar.Append(_help,          _('Help'))
        
        self.SetMenuBar(self.menubar)
        
        #Bind Event
        _clickLang = lambda evt: self.changeLang(evt.GetId())
        self.Bind(wx.EVT_MENU, _clickLang, id=ID_MENU_LANG_ENU)
        self.Bind(wx.EVT_MENU, _clickLang, id=ID_MENU_LANG_CHT)
        
        _clickMode = lambda evt: self.changeMode(evt.GetId())
        self.Bind(wx.EVT_MENU, _clickMode, id=ID_MENU_MODE_EASY)
        self.Bind(wx.EVT_MENU, _clickMode, id=ID_MENU_MODE_MEDIUM)
        self.Bind(wx.EVT_MENU, _clickMode, id=ID_MENU_MODE_HARD)
        self.Bind(wx.EVT_MENU, _clickMode, id=ID_MENU_MODE_EVIL)
        
        self.Bind(wx.EVT_MENU, self.about, id=ID_MENU_HELP_ABOUT)
        self.Bind(wx.EVT_MENU, self.linkProject, id=ID_MENU_HELP_LINKPROJECT)
        self.Bind(wx.EVT_MENU, self.onRecordLastPuzzle, id=ID_MENU_OPT_RECORD_LAST_PUZZLE)
        self.Bind(wx.EVT_MENU, self.onShowAutoTip, id=ID_MENU_OPT_SHOW_AUTOTIP)
        
        #Set default
        self.menuOpt.Check(ID_MENU_OPT_RECORD_LAST_PUZZLE, App.bRecordLastPuzzle)
        self.menuOpt.Check(ID_MENU_OPT_SHOW_AUTOTIP, App.bShowAutoTip)
        
        pass
        
    def initToolbar(self):
        self.toolbar = self.CreateToolBar()
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(ID_TOOLBAR_NEW,        wx.Bitmap('./img/new puzzle.png'),      shortHelpString=_('New Puzzle'))
        self.toolbar.AddTool(ID_TOOLBAR_NEW_NULL,   wx.Bitmap('./img/new puzzle null.png'), shortHelpString=_('New Null Puzzle'))
        self.toolbar.AddTool(ID_TOOLBAR_SELECT,     wx.Bitmap('./img/select.png'),          shortHelpString=_('Select Puzzle By ID'))
        self.toolbar.AddSeparator()
        
        self.toolbar.AddTool(wx.ID_UNDO,            wx.Bitmap('./img/undo.png'),             shortHelpString=_('Undo'))
        self.toolbar.AddTool(wx.ID_REDO,            wx.Bitmap('./img/redo.png'),             shortHelpString=_('Redo'))
        self.toolbar.AddTool(ID_TOOLBAR_CLEARALL,   wx.Bitmap('./img/clear all.png'),        shortHelpString=_('Clear All'))
        self.toolbar.AddSeparator()
        
        self.toolbar.AddTool(ID_TOOLBAR_GUESS,      wx.Bitmap('./img/guess.png'),            shortHelpString=_('Guess Next'))
        self.toolbar.AddTool(ID_TOOLBAR_ANSWER,   wx.Bitmap('./img/guess all.png'),        shortHelpString=_('Show Answer'))
        self.toolbar.AddTool(ID_TOOLBAR_CHECKVALID, wx.Bitmap('./img/check valid.png'),      shortHelpString=_('Check Valid'))
        self.toolbar.AddSeparator()
        
        self.toolbar.AddTool(ID_TOOLBAR_SETUSER,    wx.Bitmap('./img/user.png'),             shortHelpString=_('Choice User'))
        self.toolbar.AddTool(ID_TOOLBAR_RECORDTIME, wx.Bitmap('./img/time.png'),             shortHelpString=_('Record Time'))
        self.toolbar.AddSeparator()
        
        self.toolbar.Realize()
        
        self.Bind(wx.EVT_TOOL, self.new,        id=ID_TOOLBAR_NEW)
        self.Bind(wx.EVT_TOOL, self.newNull,    id=ID_TOOLBAR_NEW_NULL)
        self.Bind(wx.EVT_TOOL, self.select,     id=ID_TOOLBAR_SELECT)
        
        self.Bind(wx.EVT_TOOL, self.undo,       id=wx.ID_UNDO)
        self.Bind(wx.EVT_TOOL, self.redo,       id=wx.ID_REDO)
        self.Bind(wx.EVT_TOOL, self.guess,      id=ID_TOOLBAR_GUESS)
        self.Bind(wx.EVT_TOOL, self.showAnswer,   id=ID_TOOLBAR_ANSWER)
        self.Bind(wx.EVT_TOOL, self.checkValid, id=ID_TOOLBAR_CHECKVALID)
        self.Bind(wx.EVT_TOOL, self.clearAll,   id=ID_TOOLBAR_CLEARALL)
        
        self.Bind(wx.EVT_TOOL, self.setUser,    id=ID_TOOLBAR_SETUSER)
        self.Bind(wx.EVT_TOOL, self.showRecord, id=ID_TOOLBAR_RECORDTIME)
    
    def initLayout(self):
        self.spendTime = 0
        self.spendTimer = wx.Timer(self)
        self.seendTimerInterval = 1000
        
        wx.StaticText(self, -1, _('User Name :'),               pos=(10, 10),  size=(70, 20),  style=wx.ALIGN_RIGHT)
        self.textUser = wx.StaticText(self, -1, "",             pos=(90, 10),  size=(90, 20))
        
        wx.StaticText(self, -1, _('Best Time:'),                pos=(150, 10), size=(100,20))
        self.textBestTime = wx.StaticText(self, -1, "0:00:00",  pos=(200, 10), size=(100,20))
        
        wx.StaticText(self, -1, _('Puzzle ID :'),               pos=(250, 10), size=(70,20))
        self.textPuzzleID = wx.StaticText(self, -1, "0",        pos=(310, 10), size=(30,20))
        
        wx.StaticText(self, -1, _('Spend Time :'),              pos=(350, 10), size=(100,20))
        self.textSpendTime = wx.StaticText(self, -1, "0:00:00", pos=(420, 10), size=(100,20))
        
    def cleanSpendTime(self):
        self.setSpendTime(0)
        
    def setSpendTime(self, t):
        self.spendTime = t
        self.onSpendTimer(None)
        
    def onSpendTimer(self, evt):
        self.spendTime += 1
        t = self.spendTime
#        h = t/(60*60)
#        m = t/(60) % 60
#        s = t % 60
        #self.textSpendTime.SetLabel('%d:%02d:%02d' % (h,m,s))
        self.textSpendTime.SetLabel(util.Sec2TimeFormat(t))
        
    
    def changeLang(self, lang_id, bInit=False):
        self.curLangID = lang_id
        self.menuLang.Check(self.curLangID, True)
        
        util.config.set('LANG', 'language', LANG_STR_MAP[lang_id])
        
        if not bInit:
            dlg = wx.MessageDialog(None, _('Please relaunch SudokuBoxer to load correctly Language'), _('Information'), style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        pass
        
    def changeMode(self, mode_id):
        self.curModeID = mode_id
        self.menuMode.Check(self.curModeID, True)
        
        util.config.set('APP', 'level', MODE_STR_MAP[mode_id])
        pass
    
    def onRecordLastPuzzle(self, evt):
        App.bRecordLastPuzzle = not App.bRecordLastPuzzle
        self.menuOpt.Check(ID_MENU_OPT_RECORD_LAST_PUZZLE, App.bRecordLastPuzzle)
    
    def onShowAutoTip(self, evt):
        App.bShowAutoTip = not App.bShowAutoTip
        self.menuOpt.Check(ID_MENU_OPT_SHOW_AUTOTIP, App.bShowAutoTip)
        if App.bShowAutoTip:
            self.board._updateAutoTip()
        self.board.Refresh()
        
    def onClose(self, evt):
        if App.bRecordLastPuzzle:
            App.lastPuzzle = { 'id': self.puzzleID, 
                               'time': self.spendTime,
                               'puzzleDefault' : self.board.getDefaultPuzzle(bString=True), 
                               'puzzleCurrent' : self.board.getCurrentPuzzle(bString=True) }
        self.Destroy()
    
    def onEnterBoard(self, evt):
        if not self.spendTimer.IsRunning():
            self.spendTimer.Start(self.seendTimerInterval)
    
    def setDefault(self, _id, num, current=[]):
        self.board.setDefault(num, current)
        self.cleanSpendTime()
        
        self.puzzleID = _id
        self.textPuzzleID.SetLabel(unicode(_id))
        
    def new(self, evt):
        _id, puzzle = App.puzzleLoader.pick(MODE_STR_MAP[self.curModeID])
        self.setDefault(_id, puzzle)
        
    def newNull(self, evt):
        self.board.clearToNull()
    
    def select(self, evt):
        count = App.puzzleLoader.getCount( MODE_STR_MAP[self.curModeID] )
        dlg = wx.TextEntryDialog( self, message=_('Please input a ID number : (1~%d)' % count), 
                                        caption='Select ID' )
        
        if dlg.ShowModal() == wx.ID_OK:
            v = dlg.GetValue()
            try:
                v = int(v)
                if 0 < v <= count:
                    self.selectId(v)
                else:
                    raise 'Number Error!'
            except:
                msg = wx.MessageDialog(None, _('Please input a correctly number!'), _('Information'), style=wx.OK)
                msg.ShowModal()
                msg.Destroy()
        dlg.Destroy()
    
    def selectId(self, _id):
        self.setDefault( *App.puzzleLoader.pick(MODE_STR_MAP[self.curModeID], _id) )
        
    def clearAll(self, evt):
        self.board.clearToDefault()
        
    def showAnswer(self, evt):
        '''
        Do 'easy' first, then 'medium' and try 'easy' again!
        '''
        
        if not self.board.answer:
            self.board.queryAnswer()
        
        dlg = AnswerBoard(self, -1, _("Answer"), size=(30*App.nLINE, 30*App.nLINE+30), style=wx.DEFAULT_DIALOG_STYLE, useMetal=False )
        
        #put answerBoard to right side of MainFrom
        pos  = self.GetPosition()
        size = self.GetSize()
        mw, mh = size.GetWidth(), size.GetHeight() #main frame width, height
        d_size = dlg.GetSize()
        dw, dh = d_size.GetWidth(), d_size.GetHeight() #dlg width, height
        
        dlg.SetPosition( (pos.x+mw, pos.y+(mh-dh)/2.0) )
        dlg.setPuzzle( self.board.default, self.board.answer )
        
        dlg.ShowModal()
        dlg.Destroy()
        
    def guess(self, evt):
        guessModeList = ['easy', 'medium']
        for mode in guessModeList:
            if self.board.guessNext(mode=mode):
                break
        
    def checkValid(self, evt):
        res = self.board.checkValid()
        if res:
            msg = _('Check Valid : Correctly!')
        else:
            msg = _('Check Valid : Wrong!')
        dlg = wx.MessageDialog(None, msg, _('Information'), style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def check(self, evt):
        print 'Check Finish', self.board.checkFinish()
    
    def finish(self, evt):
        res = self.board.checkValid()
        if res:
            msg = _('Congratulations! You had finish this Sudoku!')
            self.spendTimer.Stop()
            
            g_userInfo = GetUserInfo()
            g_userInfo.setRecord(self.puzzleID, self.spendTime)
        else:
            msg = _('Hey man! Your answer is wrong... try again!')
        #print msg
        #print '123'
        #print u'123'
        #print msg
        dlg = wx.MessageDialog(None, msg, _('Information'), style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    
    def undo(self, evt):
        self.board.undo()
        
    def redo(self, evt):
        self.board.redo()
        
    def setUser(self, evt):
        from user import UserDialog
        dlg = UserDialog(self, -1, _("Select User"), size=(350, 200),
                         #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
                         style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
                         useMetal=False,
                         )
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            name = dlg.GetName()
            self._setUser(name)
            pass
        dlg.Destroy()
    
    def _setUser(self, name):
        from user import UserDialog
        g_userInfo = GetUserInfo()
        g_userInfo.setUser(name)
        self.textUser.SetLabel(name)
        
        util.config.set('APP', 'user', name)
        
    def showRecord(self,evt):
        from user import GetUserInfo, RecordListDialog
        userInfo = GetUserInfo()
        if not userInfo.getCurUser():
            return
        dlg = RecordListDialog(self, -1, _("Record List"), size=(350, 200))
        dlg.CenterOnScreen()
        dlg.ShowModal()
        dlg.Destroy()
        
    def about(self, evt):
        from wx.lib.wordwrap import wordwrap
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = "Sudoku Boxer"
        info.Version = App.VERSION + '.' + App.VERSION_DATE
        info.Copyright = "(C) 2010 Falldog (falldog7@gmail.com)"
        info.Description = wordwrap(
            "Sudoku Boxer, play and solve with sudoku software. Enjoy it!",
            350, wx.ClientDC(self))
        info.WebSite = ("http://falldog7.blogspot.com", "Falldog's blog")
        info.Developers = ["Falldog"]
        
        info.License = wordwrap(LICENSE, 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)
    
    def linkProject(self, evt):
        import webbrowser
        webbrowser.open('http://sourceforge.net/projects/sudokuboxer/')
        