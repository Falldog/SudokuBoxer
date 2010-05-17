import wx
import App

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
        num = pos[0] + pos[1]*App.nGRID + 1
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
        for i in App.rgGRID:
            for j in App.rgGRID:
                num = i + j*App.nGRID +1
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
        sl = s * App.nGRID
        
        #Draw Dot Line
        dc.SetPen(wx.Pen(self.CL_LINE_DOT, 1, wx.DOT))
        dc.DrawLine( s,   0,   s,   sl )
        dc.DrawLine( s*2, 0,   s*2, sl )
        dc.DrawLine( 0,   s,   sl,  s   )
        dc.DrawLine( 0,   s*2, sl,  s*2 )
        dc.SetPen(wx.NullPen)
        
        dc.SetPen(wx.Pen(self.CL_LINE_SOLID, 2, wx.SOLID))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(0, 0, s*App.nGRID, s*App.nGRID)
        pass
        