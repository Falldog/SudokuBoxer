import wx

from src import app

__author__ = 'Falldog'


class BoxerInfo:
    ''' Control all info cells, create & draw '''
    def __init__(self, *argv):
        self.infos = []

    def add(self, _type, *argv):
        info = None
        if _type == 'cell grid':
            info = InfoCellGrid(*argv)
        elif _type == 'cell line':
            info = InfoCellLine(*argv)
        elif _type == 'cell tips':
            info = InfoCellTips(*argv)
        elif _type == 'line':
            info = InfoLine(*argv)
        elif _type == 'cell':
            info = InfoCell(*argv)

        if info:
            self.infos.append(info)

    def clear(self):
        ret = len(self.infos)>0
        self.infos = []
        return ret

    def draw(self, dc, cellSize):
        [ i.draw(dc, cellSize) for i in self.infos ]


class InfoCell:
    ''' Info about draw a single cell (1x1)'''
    def __init__(self, i, j):
        self.cellPos = i, j
    def draw(self, dc, cellSize):
        dc.SetPen(wx.Pen('#33BB33', 3, wx.DOT))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(self.cellPos[0]*cellSize, self.cellPos[1]*cellSize, cellSize, cellSize)

class InfoCellTips:
    ''' Info about draw tips(1~9) for a single cell (1x1)'''
    def __init__(self, i, j, nums=[]):
        self.cellPos = i, j
        self.nums = nums
    def draw(self, dc, cellSize):
        size = cellSize/3.0
        dc.SetFont(wx.Font( cellSize*0.2, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Comic Sans MS' ))
        dc.SetTextForeground( '#1111AA' )
        l, t = self.cellPos[0]*cellSize, self.cellPos[1]*cellSize
        for n in self.nums:
            r = (l + int((n-1)%3)*size, t + int((n-1)/3)*size,size,size)
            dc.DrawLabel(str(n), r, wx.ALIGN_CENTER)

class InfoCellGrid:
    ''' Info about draw a cell grid (3x3)'''
    def __init__(self, i, j):
        self.gridPos = i,j
    def draw(self, dc, cellSize):
        size = cellSize*3
        dc.SetPen(wx.Pen('#FF0000', 3, wx.SOLID))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(self.gridPos[0]*size, self.gridPos[1]*size, size, size)

class InfoCellLine:
    ''' Info about draw a cell line(1x9 or 9x1)'''
    def __init__(self, direction, idx):
        ''' direction : 'v', 'h' '''
        assert direction in ('v','h')
        self.direction = direction
        self.idx = idx
    def draw(self, dc, cellSize):
        dc.SetPen(wx.Pen('#FF0000', 3, wx.SOLID))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        if self.direction == 'h':
            dc.DrawRectangle(0, self.idx*cellSize,  app.nLINE*cellSize, cellSize)
        else:
            dc.DrawRectangle(self.idx*cellSize, 0,  cellSize, app.nLINE*cellSize)

class InfoLine:
    ''' Info about draw a line'''
    def __init__(self, direction, idx, start=-1, end=-1):
        '''
        direction : 'v', 'h'
        '''
        assert direction in ('v','h')
        self.direction = direction
        self.idx = idx
        self.start = 0
        self.end = 9
        if start >= 0:
            self.start = start
        if end >= 0:
            self.end = end
        pass
    def draw(self, dc, cellSize):
        half = cellSize/2
        quart = cellSize/4
        dc.SetPen(wx.Pen('#DD2222', 3, wx.DOT))
        if self.direction == 'v':
            dc.DrawLine(self.idx*cellSize+half, self.start*cellSize+quart, self.idx*cellSize+half, self.end*cellSize-quart)
        else:
            dc.DrawLine(self.start*cellSize+quart, self.idx*cellSize+half, self.end*cellSize-quart, self.idx*cellSize+half)
        pass

