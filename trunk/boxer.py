import wx
import App
from copy import deepcopy

class Step:
    def __init__(self, i, j, ori_val, val):
        self.pos = i,j
        self.val = val
        self.ori_val = ori_val
        
    def infoRedo(self):
        return self.pos[0], self.pos[1], self.val
    def infoUndo(self):
        return self.pos[0], self.pos[1], self.ori_val


class BoxerInfo:
    ''' Control all info cells, create & draw '''
    def __init__(self, *argv):
        self.infos = []
        pass
    
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
            dc.DrawRectangle(0, self.idx*cellSize,  App.nLINE*cellSize, cellSize)
        else:
            dc.DrawRectangle(self.idx*cellSize, 0,  cellSize, App.nLINE*cellSize)

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
        
        
class SudokuBoxer:
    def __init__(self):
        self.__lineBoolNum__ = [ False for j in App.rgLINE]
        self.__gridBoolNum__ = []
        for i in App.rgGRID:
            self.__gridBoolNum__.append( [ False for j in App.rgGRID] )
            
        self.__boolNum__     = []
        for i in App.rgLINE:
            self.__boolNum__.append( [ False for j in App.rgLINE] )
        pass
        
    def _initBoolNum(self):
        self._boolNum = deepcopy(self.__boolNum__)
    def _initGridBoolNum(self):
        self._gridBoolNum = deepcopy(self.__gridBoolNum__)
    def _initLineBoolNum(self):
        self._lineBoolNum = deepcopy(self.__lineBoolNum__)
        
    def _markBoolNum(self, _num):
        for i in App.rgLINE:
            for j in App.rgLINE:
                if self.num[i][j] == _num:
                    self._boolNum[i][j] = True
                else:
                    self._boolNum[i][j] = False
        pass
    
    def _markBoolNoVal(self):
        for i in App.rgLINE:
            for j in App.rgLINE:
                if self.num[i][j] != 0:
                    self._boolNum[i][j] = True
                    
    def _markBoolNumByXY(self, x, y):
        '''
        0010             FFTF
        1022 -> (2,1) -> TFTT
        0030             FFTF
        '''
        for i in App.rgLINE:
            self._boolNum[i][y] = True
        for i in App.rgLINE:
            self._boolNum[x][i] = True
    
    def _markBoolNumByGrid(self, i, j):
        self._initLineBoolNum()
        g = self.grid(i,j)
        for x in App.rgGRID:
            for y in App.rgGRID:
                if g[x][y] != 0:
                    self._lineBoolNum[ g[x][y]-1 ] = True
        return self._lineBoolNum
    def _markGridBoolNum(self, i, j):
        self._initGridBoolNum()
        g = self.grid(i,j)
        for x in App.rgGRID:
            for y in App.rgGRID:
                if g[x][y] != 0:
                    #self._lineBoolNum[ g[x][y]-1 ] = True
                    self._gridBoolNum[x][y] = True
        return self._gridBoolNum
        
    def _queryGridBoolNum(self, grid, state):
        for x in App.rgGRID:
            for y in App.rgGRID:
                if grid[x][y]==state:
                    return x,y
        return -1, -1
    
    def _iterGridNoVal(self, grid):
        for x in App.rgGRID:
            for y in App.rgGRID:
                if grid[x][y]==0:
                    yield (x,y)
        pass
    
    def _countBoolNumByXY(self, x, y, num):
        c = 0
        for i in App.rgLINE:
            if self.num[i][y] == num:
                c += 1
        for i in App.rgLINE:
            if self.num[x][i] == num:
                c += 1
        return c
    
    def _countGridBoolNum(self, grid, state):
        c = 0
        for x in App.rgGRID:
            for y in App.rgGRID:
                if grid[x][y]==state:
                    c += 1
        return c
    def _countLineBoolNum(self, line, state):
        c = 0
        for n in line:
            if n == state:
                c += 1
        return c
        
    def _checkEasy(self, num):
        self._initBoolNum()
        self._markBoolNoVal()
        numPosList = []
        #mark num in all grid
        for i in App.rgGRID:
            for j in App.rgGRID:
                g = self.grid(i,j)
                x, y = self._queryGridBoolNum(g, num)
                if (x,y) == (-1,-1):
                    continue
                pos = i*3+x, j*3+y
                self._markBoolNumByXY(*pos)
                numPosList.append( {'pos':pos, 'grid':(i,j)} ) #for boxerInfo
                
        #check all grid which only one space
        for i in App.rgGRID:
            for j in App.rgGRID:
                g = self.grid(i,j, self._boolNum)
                g_num = self.grid(i,j)
                if self._countGridBoolNum(g,False) == 1 and self._countGridBoolNum(g_num,num) == 0:
                    x, y = self._queryGridBoolNum(g,False)
                    
                    #set boxer info
                    bi = BoxerInfo()
                    bi.add('cell grid', i, j)
                    for np in numPosList:
                        if np['grid'][0] == i and not self.checkGridLineFull(i,j,'v',np['pos'][0]%3,g_num):
                            if np['pos'][1]/3 < j:
                                start, end = np['pos'][1]+1, (j+1)*3
                            else:
                                start, end = j*3, np['pos'][1]
                            bi.add('line', 'v', np['pos'][0], start, end)
                            bi.add('cell', np['pos'][0], np['pos'][1])
                        elif np['grid'][1] == j and not self.checkGridLineFull(i,j,'h',np['pos'][1]%3,g_num):
                            if np['pos'][0]/3 < i:
                                start, end = np['pos'][0]+1, (i+1)*3
                            else:
                                start, end = i*3, np['pos'][0]
                            bi.add('line', 'h', np['pos'][1], start, end)
                            bi.add('cell', np['pos'][0], np['pos'][1])
                    return (i*3+x, j*3+y), bi
                    
        return (-1, -1), None
        
    def checkGridLineFull(self, i, j, direction, idx, gridNum=None):
        '''
        check the line is full or not in a grid
        Ex:
        grid (0,0) -> 010
                      203 -> check direction='h', idx=1 -> '203' -> not full (have 1 space)
                      864 -> check direction='h', idx=2 -> '864' -> full (no space)
        '''
        assert direction in ('v', 'h')
        if not gridNum:
            gridNum = self.grid(i,j)
            
        full = True
        for i in App.rgGRID:
            if direction == 'v':
                full = full and (gridNum[idx][i]!=0)
            else:
                full = full and (gridNum[i][idx]!=0)
        return full
        
    def checkValidInput(self, num, posX, posY):
        '''
        Check is grid valid, vertical/horizantol line valid
        '''
        g = self.grid(posX/3,posY/3)
        if self._countGridBoolNum(g,num) > 1:
            return False
            
        line = [self.num[posX][i] for i in App.rgLINE]
        if self._countLineBoolNum(line, num) > 1:
            return False
            
        line = [self.num[i][posY] for i in App.rgLINE]
        if self._countLineBoolNum(line, num) > 1:
            return False
            
        return True
    
    def getValidNum(self, posX, posY):
        '''
        get (posX,posY) valid number list
        Example:
        012045                         012045
        000090                            090
        000100   -> (posX=3,posY=0) ->    100   -> valid list = (3,6,7)
        000000                            0
        001000                            0
        200800                            8
        
        Return:
            number list : [1,2,3,...]
        '''
        #Check grid
        self._initLineBoolNum()
        g = self.grid(posX/3,posY/3)
        for i in App.rgGRID:
            for j in App.rgGRID:
                if g[i][j] != 0:
                    self._lineBoolNum[ g[i][j]-1 ] = True
        #Check vertical line
        line = [self.num[posX][i] for i in App.rgLINE]
        for num in line:
            if num != 0:
                self._lineBoolNum[ num-1 ] = True
        #Check horizantol line
        line = [self.num[i][posY] for i in App.rgLINE]
        for num in line:
            if num != 0:
                self._lineBoolNum[ num-1 ] = True
        
        res = [ i for i in range(1, App.nLINE+1) if not self._lineBoolNum[i-1] ]
        return res
        
    def boxerNextEasy(self):
        for num in App.rgLINE:
            num += 1
            pos, info = self._checkEasy(num)
            if pos != (-1, -1):
                return pos, num, info
        return None
    
    def boxerNextSoSo(self):
        '''
        Check line/grid in soso way.
        Ex:
        line===12 456 89
                 X       -> check 3 & 7, if 3 exist, this X is 7
                     X   -> check 3 & 7, if 3 exist, this X is 7
        '''
        print '-----------boxerNextSoSo-----------'
        boolNumFalse = [False for i in App.rgLINE]
        #check vertical
        for i in App.rgLINE:
            boolNum = deepcopy(boolNumFalse)
            #mark bool number
            for j in App.rgLINE:
                n = self.num[i][j]
                if n > 0 :
                    boolNum[n-1] = True
            
            #check non-value line
            for j in App.rgLINE:
                n = self.num[i][j]
                if n == 0:
                    numPosList = []
                    checkBoolNum = deepcopy(boolNum)
                    for line_i in App.rgLINE:
                        if line_i == i: continue
                        n = self.num[line_i][j]
                        if n > 0 and checkBoolNum[n-1]==False:
                            checkBoolNum[n-1] = True
                            numPosList.append( {'pos':(line_i,j), 'num':n} )
                    if self._countLineBoolNum(checkBoolNum,False) == 1:
                        print 'CheckVertical line=%s\n (i,j)=%s, checkBoolNum=%s' % ([int(self.num[i][n]) for n in App.rgLINE], (i,j), checkBoolNum)
                        num = checkBoolNum.index(False)+1
                        
                        #set boxer info
                        bi = BoxerInfo()
                        bi.add('cell line', 'v', i)
                        conflitNumList = [num]
                        for _n in numPosList:
                            bi.add('cell', _n['pos'][0], _n['pos'][1])
                            conflitNumList.append(_n['num'])
                        for idx in App.rgLINE:
                            if self.num[i][idx] == 0 and idx != j:
                                bi.add('cell tips', i, idx, conflitNumList)
                        return (i,j), num, bi
            pass
        #check horizantol
        for j in App.rgLINE:
            boolNum = deepcopy(boolNumFalse)
            #mark bool number
            for i in App.rgLINE:
                n = self.num[i][j]
                if n > 0 :
                    boolNum[n-1] = True
            
            #check non-value line
            for i in App.rgLINE:
                n = self.num[i][j]
                if n == 0:
                    numPosList = []
                    checkBoolNum = deepcopy(boolNum)
                    for line_j in App.rgLINE:
                        if line_j == j: continue
                        n = self.num[i][line_j]
                        if n > 0 and checkBoolNum[n-1]==False:
                            checkBoolNum[n-1] = True
                            numPosList.append( {'pos':(line_i,j), 'num':n} )
                    if self._countLineBoolNum(checkBoolNum,False) == 1:
                        print 'CheckHorizantol line=%s\n (i,j)=%s, checkBoolNum=%s' % ([self.num[n][j] for n in App.rgLINE], (i,j), checkBoolNum)
                        num = checkBoolNum.index(False)+1
                        
                        #set boxer info
                        bi = BoxerInfo()
                        bi.add('cell line', 'h', j)
                        conflitNumList = [num]
                        for _n in numPosList:
                            bi.add('cell', _n['pos'][0], _n['pos'][1])
                            conflitNumList.append(_n['num'])
                        for idx in App.rgLINE:
                            if self.num[idx][j] == 0 and idx != i:
                                bi.add('cell tips', idx, j, conflitNumList)
                        return (i,j), num, bi
        
        #check Grid
        for i in App.rgGRID:
            for j in App.rgGRID:
                boolNum = deepcopy(self._markBoolNumByGrid(i,j))   #represent 1~9
                
                g = self.grid(i,j)
                for x in App.rgGRID:
                    for y in App.rgGRID:
                        if g[x][y]!=0: continue
                        gx, gy = x + i*App.nGRID, y + j*App.nGRID #global x,y
                        conflitNumList = []
                        checkBoolNum = deepcopy(boolNum)
                        for num_idx in App.rgLINE:
                            if checkBoolNum[num_idx]: continue
                            num = num_idx+1
                            if self._countBoolNumByXY(gx,gy, num) > 0:
                                checkBoolNum[num_idx] = True
                                conflitNumList.append(num)
                                
                        if self._countLineBoolNum(checkBoolNum, False) == 1:
                            num = checkBoolNum.index(False)+1
                            print 'CheckGrid (i,j)=%s checkBoolNum=%s' % ((gx,gy), checkBoolNum)
                            
                            #set boxer info
                            bi = BoxerInfo()
                            bi.add('cell grid', i, j)
                            conflitNumList.append(num)
                            #mark the conflit cells out of grid
                            for _x in App.rgLINE:#vertical
                                if self.num[_x][gy] in conflitNumList:
                                    bi.add('cell', _x, gy)
                            for _y in App.rgLINE:#horizantol
                                if self.num[gx][_y] in conflitNumList:
                                    bi.add('cell', gx, _y)
                            #mark cell tips in grid
                            for _i in App.rgGRID:
                                for _j in App.rgGRID:
                                    _x, _y = _i + i*App.nGRID, _j + j*App.nGRID
                                    if self.num[_x][_y] == 0 and (_x,_y)!=(gx,gy):
                                        bi.add('cell tips', _x, _y, conflitNumList)
                            return (gx,gy), num, bi
        return None
        
    def boxerNextSoSo2(self):
        '''
        Check line/grid in soso2 way.
        Ex:
        line===12  56 89
                 XX  X   -> check 3, if 2*X has 3, the only 1X is 3
                 XX  X   -> check 4, if 2*X has 4, the only 1X is 4
                 XX  X   -> check 7, if 2*X has 7, the only 1X is 7
        '''
        print '-----------boxerNextSoSo2-----------'
        boolNumFalse = [False for i in App.rgLINE]
        #check vertical
        for i in App.rgLINE:
            boolNum = deepcopy(boolNumFalse)
            lineBoolNum = deepcopy(boolNumFalse)
            #mark bool number
            for j in App.rgLINE:
                n = self.num[i][j]
                if n > 0 :
                    boolNum[n-1] = True
                    lineBoolNum[j] = True
            
            for num_idx in App.rgLINE:
                if boolNum[num_idx]: continue
                checkLineBoolNum = deepcopy(lineBoolNum)
                num = num_idx+1
                
                #check grid
                for j in App.rgGRID:
                    grid_i = int(i / 3)
                    g = self.grid(grid_i, j)
                    pos = self._queryGridBoolNum(g, num)
                    if pos != (-1,-1):
                        checkLineBoolNum[j*3] = checkLineBoolNum[j*3+1] = checkLineBoolNum[j*3+2] = True
                
                #check line
                for j in App.rgLINE:
                    if self.num[i][j] > 0: continue
                    
                    for line_i in App.rgLINE:
                        if self.num[line_i][j] == num:
                            checkLineBoolNum[j] = True
                            break
                            
                if self._countLineBoolNum(checkLineBoolNum, False) == 1:
                    print 'CheckVertical line=%s\n (i,j)=%s, checkLineBoolNum=%s' % ([int(self.num[i][n]) for n in App.rgLINE], (i,j), checkLineBoolNum)
                    j = checkLineBoolNum.index(False)
                    return (i,j), num, None
            
        #check horizontal
        for j in App.rgLINE:
            boolNum = deepcopy(boolNumFalse)
            lineBoolNum = deepcopy(boolNumFalse)
            
            #mark bool number
            for i in App.rgLINE:
                n = self.num[i][j]
                if n > 0 :
                    boolNum[n-1] = True
                    lineBoolNum[i] = True
            
            for num_idx in App.rgLINE:
                if boolNum[num_idx]: continue
                checkLineBoolNum = deepcopy(lineBoolNum)
                num = num_idx+1
                
                #check grid
                for i in App.rgGRID:
                    grid_j = int(j / 3)
                    g = self.grid(i, grid_j)
                    pos = self._queryGridBoolNum(g, num)
                    if pos != (-1,-1):
                        checkLineBoolNum[i*3] = checkLineBoolNum[i*3+1] = checkLineBoolNum[i*3+2] = True
                
                #check line
                for i in App.rgLINE:
                    if self.num[i][j] > 0: continue
                    
                    for line_j in App.rgLINE:
                        if self.num[i][line_j] == num:
                            checkLineBoolNum[i] = True
                            break
                if self._countLineBoolNum(checkLineBoolNum, False) == 1:
                    print 'CheckVertical line=%s\n (i,j)=%s, checkLineBoolNum=%s' % ([int(self.num[n][j]) for n in App.rgLINE], (i,j), checkLineBoolNum)
                    i = checkLineBoolNum.index(False)
                    return (i,j), num, None
        
        #check Grid
        for i in App.rgGRID:
            for j in App.rgGRID:
                boolNum = deepcopy(self._markBoolNumByGrid(i,j)) #represent 1~9
                gridBoolNum = deepcopy(self._markGridBoolNum(i,j)) #Grid has value
                
                g = self.grid(i,j)
                for num_idx in App.rgLINE:
                    if boolNum[num_idx]: continue
                    num = num_idx + 1
                    checkGridBoolNum = deepcopy(gridBoolNum)
                    
                    for pos in self._iterGridNoVal(g):
                        gx, gy = pos[0] + i*App.nGRID, pos[1] + j*App.nGRID #global x,y
                        if self._countBoolNumByXY(gx, gy, num) > 0:
                            checkGridBoolNum[pos[0]][pos[1]] = True
                    #only one
                    if self._countGridBoolNum(checkGridBoolNum, False) == 1:
                        pos = self._queryGridBoolNum(checkGridBoolNum, False)
                        gx, gy = pos[0] + i*App.nGRID, pos[1] + j*App.nGRID #global x,y
                        print 'CheckGrid (i,j)=%s, GridBoolNum=%s' % (pos, checkGridBoolNum)
                        return (gx,gy), num, None
        return None
        
    def boxerNext(self, mode='easy'):
        if mode=='easy':
            return self.boxerNextEasy()
        elif mode=='medium':
            ret = self.boxerNextSoSo()
            if not ret:
                ret = self.boxerNextSoSo2()
            return ret
    
    def boxerBrute(self, autoFill=True, bCheckFromDefault=True):
        '''
        bCheckFromDefault : False -> use self.num to check, should confirm self.num is correctly
        '''
        import util
        if not autoFill:
            oriNum = deepcopy(self.num)
            
        if bCheckFromDefault:
            self.num = deepcopy(self.default)
        else:
            oriDefault = deepcopy(self.default)
            self.default = deepcopy(self.num) #set num to default
            
        
        #set validList
        for x in App.rgLINE:
            for y in App.rgLINE:
                if self.num[x][y] == 0:
                    self.num[x][y].validList = self.getValidNum(x,y)
        
        ret = self._brute(0, 0)
        print '[boxerBrute] ret=%s\npuzzle=%s' % (ret, util.Puzzle2Str(self.num))
        answer = self.num
        
        
        if not autoFill:
            self.num = oriNum
        if not bCheckFromDefault:
            self.default = oriDefault
        return answer
        
    def _brute(self, i, j):
        if j*App.nLINE+i == App.nLINE*App.nLINE: #the last cell
            return True
            
        if i==App.nLINE-1:
            next = 0, j+1
        else:
            next = i+1, j
            
        if self.default[i][j] != 0: #default value
            return self._brute(*next)
        else:
            #try to put number in validList to try valid or not
            for n in self.num[i][j].validList:
                self.num[i][j].val = n
                if self.checkValid() and self._brute(*next): #checkValid() define by class NumberBoard
                    return True
                    
            self.num[i][j].val = 0 #set none
            return False
    
    def _debugPrintBoolNum(self):
        print '------boolNum------'
        for i in App.rgLINE:
            for j in App.rgLINE:
                sys.stdout.write(str(self._boolNum[j][i])[0])
                if j in [2,5]:
                    sys.stdout.write(' ')
            sys.stdout.write('\n')
        print '-------------------'
        