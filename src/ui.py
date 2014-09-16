import wx
from wx import xrc
import logging

import app
from main_frame import Number

logger = logging.getLogger(__name__)


class XrcBase:
    def __init__(self):
        self.Bind( wx.EVT_WINDOW_CREATE , self.OnCreate)
        
    def OnCreate(self, evt):
        self.Unbind ( wx.EVT_WINDOW_CREATE )
        wx.CallAfter( self.PostInit )
        evt.Skip()
        return True
        
    def PostInit(self):
        raise NotImplementedError
    
    def __getattr__(self, name):
        if not self.__dict__.has_key(name):
            obj = xrc.XRCCTRL(self, name) #Try to query XRC obj
            if not obj:
                raise AttributeError
            self.__dict__[name] = obj
        return self.__dict__[name]
        
class XrcFrame(wx.Frame, XrcBase):
    def __init__(self):
        f = wx.PreFrame()
        self.PostCreate(f)
        XrcBase.__init__(self)

class XrcPanel(wx.Panel, XrcBase):
    def __init__(self):
        p = wx.PrePanel()
        self.PostCreate(p)
        XrcBase.__init__(self)

class XrcDialog(wx.Dialog, XrcBase):
    def __init__(self):
        d = wx.PreDialog()
        self.PostCreate(d)
        XrcBase.__init__(self)

class PreferenceDialog(XrcDialog):
    def __init__(self):
        XrcDialog.__init__(self)
    
    def PostInit(self):
        wx.CallAfter(self.initNumberPanel)
        self.initColorText()
        self.updateColor()
        
    def initNumberPanel(self):
        self.numberPanel.setDefault( [[0,2,3],
                                      [0,5,0],
                                      [7,0,9]] )
        pass
        
    def initColorText(self):
        self.cpBgFocus.SetColour(app.clBgFocus)
        self.cpBgOver.SetColour(app.clBgOver)
        self.cpBgNormal.SetColour(app.clBgNormal)
        self.cpBgDefault.SetColour(app.clBgDefault)
        self.cpTextNormal.SetColour(app.clTextNormal)
        self.cpTextDefault.SetColour(app.clTextDefault)
        self.colorPickerList = [self.cpBgFocus, self.cpBgOver, self.cpBgNormal, self.cpBgDefault, self.cpTextDefault, self.cpTextNormal]
        for c in self.colorPickerList:
            self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onColorChanged, c)
    
    def updateColor(self):
        self.numberPanel.BG_CL       = app.clBgNormal
        self.numberPanel.BG_CL_FOCUS = app.clBgFocus
        self.numberPanel.BG_CL_OVER  = app.clBgOver
        self.numberPanel.BG_CL_DEFAULT= app.clBgDefault
        self.numberPanel.updateBrush()
        
    def onColorChanged(self, evt):
        _id = evt.GetId()
        for idx, c in enumerate(self.colorPickerList):
            if _id == c.GetId():
                if c is self.cpBgFocus:
                    app.clBgFocus = c.GetColour()
                if c is self.cpBgOver:
                    app.clBgOver = c.GetColour()
                if c is self.cpBgNormal:
                    app.clBgNormal = c.GetColour()
                if c is self.cpBgDefault:
                    app.clBgDefault = c.GetColour()
                self.updateColor()
                    
class NumberPanel(XrcPanel):
    def __init__(self):
        XrcPanel.__init__(self)
    
    def PostInit(self):
        #wx.Panel.__init__(self, parent, *argv, **argd)
        from copy import deepcopy
        self.mouseOverPos = (-1,-1)
        self.BG_CL         = '#EEEEEE'
        self.BG_CL_DEFAULT = '#E3EDFF'
        self.BG_CL_OVER    = '#8FD6FF'
        self.BG_CL_FOCUS   = '#C1DEA3'
        self.CL_TEXT       = '#000000'
        self.CL_LINE_DOT   = '#777777'
        self.CL_LINE_SOLID = '#333333'
        self.penTrans = wx.Pen('#000000', 1, wx.TRANSPARENT)
        self.updateBrush()
        
        #self.cellPos = (-1,-1)
        self.num = [ [] for n in app.rgGRID ]
        for i in app.rgGRID:
            self.num[i] = [ Number() for n in app.rgGRID ]
        self.default = deepcopy(self.num)
        
        self.focusPos = (-1,-1)
        self.focusNums = []
        self.bindEvent()
        self.setCellSize(30)
        
    def bindEvent(self):
        self.Bind(wx.EVT_PAINT,        self.onDraw)
        self.Bind(wx.EVT_MOTION,       self.onMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN,    self.onMouseDown)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        self.Bind(wx.EVT_KEY_DOWN,     self.onKeyDown)
    
    def updateBrush(self):
        self.brush_bg        = wx.Brush(self.BG_CL)
        self.brush_bg_over   = wx.Brush(self.BG_CL_OVER)
        self.brush_bg_focus  = wx.Brush(self.BG_CL_FOCUS)
        self.brush_bg_default= wx.Brush(self.BG_CL_DEFAULT)
        self.Refresh()

    def setDefault(self, d, cur_d=[]):
        from copy import deepcopy
        assert len(d)==len(self.default)
        #Default
        for i in app.rgGRID:
            for j in app.rgGRID:
                self.default[i][j].val = d[i][j]
                self.default[i][j].isDefault  =  d[i][j]!=0
        self.num = deepcopy(self.default)
        pass
        
    def setCellSize(self, size):
        self.CELL_SIZE = int(size)
        self.font = wx.Font( self.CELL_SIZE*0.5, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Comic Sans MS' )
    
    def setVal(self, i, j, v):
        self.dirtyCell(i,j)
        self.num[i][j].val = v
        
    def pt2pos(self, x, y):
        _x, _y = int(x / self.CELL_SIZE), int(y / self.CELL_SIZE)
        if 0 <= _x < 3 or 0 <= _y < 3:
            return _x, _y
        else:
            return -1, -1
            
    def onMouseMove(self, evt):
        x,y = evt.GetPosition()
        pos = self.pt2pos(x,y)
        if pos != self.mouseOverPos:
            self.dirtyCell(*pos)
            self.dirtyCell(*self.mouseOverPos)
            self.mouseOverPos = pos
        evt.Skip()
        pass
        
    def onMouseDown(self, evt):
        x,y = evt.GetPosition()
        pos = self.pt2pos(x,y)
        self.dirtyCell(*self.focusPos)
        self.dirtyCell(*pos)
        self.focusPos = pos
        evt.Skip()
        pass
        
    def onMouseLeave(self, evt):
        self.dirtyCell(*self.mouseOverPos)
        self.mouseOverPos = (-1,-1)
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
        
        try:
            num_list = [wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3, wx.WXK_NUMPAD4, 
                        wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, wx.WXK_NUMPAD8, wx.WXK_NUMPAD9]
            num_idx = num_list.index(key) + 1
        except ValueError:
            pass
        logger.info('KeyDown key=%s, num_idx=%d', str(key), num_idx)
        
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
            
    def dirtyCell(self, i, j):
        if i == -1 or j == -1:
            return
        self.RefreshRect((i*self.CELL_SIZE, j*self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE))
        
    def onDraw(self, event):
        bpdc = wx.BufferedPaintDC(self)
        #bpdc = wx.GCDC(bpdc)#for alpha effect
        self.onDrawNums(bpdc)
        self.onDrawBorder(bpdc)
        pass
        
    def onDrawNums(self, dc):
        r = self.GetUpdateRegion()
        dirtyR = r.GetBox()
        
        dc.SetFont(self.font)
        dc.SetPen(self.penTrans) #Don't draw the border on BG rect
        for i in app.rgGRID:
            for j in app.rgGRID:
                num = self.num[i][j].val#i + j*App.nGRID +1
                _r = (i*self.CELL_SIZE, j*self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                if not dirtyR.Intersects(_r):
                    continue
                
                if (i,j) == self.mouseOverPos:
                    dc.SetBrush(self.brush_bg_over)
                elif (i,j) == self.focusPos:
                    dc.SetBrush(self.brush_bg_focus)
                elif self.default[i][j] != 0:
                    dc.SetBrush(self.brush_bg_default)
                else:
                    dc.SetBrush(self.brush_bg)
                
                dc.DrawRectangle(*_r)
                
                if num == 0: 
                    continue
                dc.SetTextForeground( self.CL_TEXT )
                dc.DrawLabel( str(num), _r, wx.ALIGN_CENTER )
                
        dc.SetPen(wx.NullPen)
        
    def onDrawBorder(self, dc):
        dc.SetBrush(wx.NullBrush)
        
        s  = self.CELL_SIZE
        sl = s * app.nGRID
        
        #Draw Dot Line
        dc.SetPen(wx.Pen(self.CL_LINE_DOT, 1, wx.DOT))
        dc.DrawLine( s,   0,   s,   sl )
        dc.DrawLine( s*2, 0,   s*2, sl )
        dc.DrawLine( 0,   s,   sl,  s   )
        dc.DrawLine( 0,   s*2, sl,  s*2 )
        dc.SetPen(wx.NullPen)
        
        dc.SetPen(wx.Pen(self.CL_LINE_SOLID, 2, wx.SOLID))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(0, 0, s*app.nGRID, s*app.nGRID)
        pass
        
class ChoiceNumberPanel(wx.Panel):
    def __init__(self, parent, *argv, **argd):
        wx.Panel.__init__(self, parent, *argv, **argd)
        self.mouseOverPos = (-1,-1)
        self.BG_CL         = '#EEEEEE'
        self.BG_CL_OVER    = '#8FD6FF'
        self.BG_CL_FOCUS   = '#C1DEA3'
        self.CL_TEXT       = '#000000'
        self.CL_LINE_DOT   = '#777777'
        self.CL_LINE_SOLID = '#333333'
        self.penTrans = wx.Pen('#000000', 1, wx.TRANSPARENT)
        self.brush_bg        = wx.Brush(self.BG_CL)
        self.brush_bg_over   = wx.Brush(self.BG_CL_OVER)
        self.brush_bg_focus  = wx.Brush(self.BG_CL_FOCUS)
        
        self.cellPos = (-1,-1)
        self.focusNums = []
        self.bindEvent()
        
    def bindEvent(self):
        self.Bind(wx.EVT_PAINT,        self.onDraw)
        self.Bind(wx.EVT_MOTION,       self.onMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN,    self.onMouseDown)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
    
    def setChoiceNums(self, nums):
        from copy import deepcopy
        self.focusNums = deepcopy(nums)
    
    def getChoiceNums(self):
        return sorted(self.focusNums)
        
    def setCellSize(self, size):
        self.CELL_SIZE = int(size)
        self.font = wx.Font( self.CELL_SIZE*0.5, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Comic Sans MS' )
    
    def setCellPos(self, i, j):
        self.cellPos = i,j
        
    def getCellPos(self):
        return self.cellPos
        
    def pt2pos(self, x, y):
        _x, _y = int(x / self.CELL_SIZE), int(y / self.CELL_SIZE)
        if 0 <= _x < 3 or 0 <= _y < 3:
            return _x, _y
        else:
            return -1, -1
    def onMouseMove(self, evt):
        x,y = evt.GetPosition()
        pos = self.pt2pos(x,y)
        if pos != self.mouseOverPos:
            self.dirtyCell(*pos)
            self.dirtyCell(*self.mouseOverPos)
            self.mouseOverPos = pos
        evt.Skip()
        pass
        
    def onMouseDown(self, evt):
        x,y = evt.GetPosition()
        pos = self.pt2pos(x,y)
        num = pos[0] + pos[1]*app.nGRID + 1
        if num in self.focusNums:
            self.focusNums.remove(num)
        else:
            self.focusNums.append(num)
        self.dirtyCell(*pos)
        evt.Skip()
        pass
        
    def onMouseLeave(self, evt):
        self.dirtyCell(*self.mouseOverPos)
        self.mouseOverPos = (-1,-1)
        evt.Skip()
        pass
        
    def dirtyCell(self, i, j):
        if i == -1 or j == -1:
            return
        self.RefreshRect((i*self.CELL_SIZE, j*self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE))
        
    def onDraw(self, event):
        bpdc = wx.BufferedPaintDC(self)
        dc = wx.GCDC(bpdc)#for alpha effect
        self.onDrawNums(dc)
        self.onDrawBorder(dc)
        pass
        
    def onDrawNums(self, dc):
        r = self.GetUpdateRegion()
        dirtyR = r.GetBox()
        
        dc.SetFont(self.font)
        dc.SetPen(self.penTrans) #Don't draw the border on BG rect
        for i in app.rgGRID:
            for j in app.rgGRID:
                num = i + j*app.nGRID +1
                _r = (i*self.CELL_SIZE, j*self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                if not dirtyR.Intersects(_r):
                    continue
                
                if num in self.focusNums:
                    dc.SetBrush(self.brush_bg_focus)
                elif (i,j) == self.mouseOverPos:
                    dc.SetBrush(self.brush_bg_over)
                else:
                    dc.SetBrush(self.brush_bg)
                
                dc.DrawRectangle(*_r)
                dc.SetBrush(wx.NullBrush)
                
                dc.SetTextForeground( self.CL_TEXT )
                dc.DrawLabel( str(num), _r, wx.ALIGN_CENTER )
                
        dc.SetPen(wx.NullPen)
        
    def onDrawBorder(self, dc):
        dc.SetBrush(wx.NullBrush)
        
        s  = self.CELL_SIZE
        sl = s * app.nGRID
        
        #Draw Dot Line
        dc.SetPen(wx.Pen(self.CL_LINE_DOT, 1, wx.DOT))
        dc.DrawLine( s,   0,   s,   sl )
        dc.DrawLine( s*2, 0,   s*2, sl )
        dc.DrawLine( 0,   s,   sl,  s   )
        dc.DrawLine( 0,   s*2, sl,  s*2 )
        dc.SetPen(wx.NullPen)
        
        dc.SetPen(wx.Pen(self.CL_LINE_SOLID, 2, wx.SOLID))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(0, 0, s*app.nGRID, s*app.nGRID)
        pass
        