from copy import deepcopy

import boxer_util
from src import app

__author__ = 'Falldog'

class BoxerBase:
    def __init__(self, num, level):
        self.level = level
        self.num = num

        self.__lineBoolNum__ = [ False for j in app.rgLINE]
        self.__gridBoolNum__ = []
        for i in app.rgGRID:
            self.__gridBoolNum__.append( [ False for j in app.rgGRID] )

        self.__boolNum__     = []
        for i in app.rgLINE:
            self.__boolNum__.append( [ False for j in app.rgLINE] )
        pass

    def run(self):
        raise NotImplementedError

    def _initBoolNum(self):
        self._boolNum = deepcopy(self.__boolNum__)
    def _initGridBoolNum(self):
        self._gridBoolNum = deepcopy(self.__gridBoolNum__)
    def _initLineBoolNum(self):
        self._lineBoolNum = deepcopy(self.__lineBoolNum__)

    def _markBoolNum(self, _num):
        for i in app.rgLINE:
            for j in app.rgLINE:
                if self.num[i][j] == _num:
                    self._boolNum[i][j] = True
                else:
                    self._boolNum[i][j] = False
        pass

    def _markBoolNoVal(self):
        for i in app.rgLINE:
            for j in app.rgLINE:
                if self.num[i][j] != 0:
                    self._boolNum[i][j] = True

    def _markBoolNumByXY(self, x, y):
        '''
        0010             FFTF
        1022 -> (2,1) -> TFTT
        0030             FFTF
        '''
        for i in app.rgLINE:
            self._boolNum[i][y] = True
        for i in app.rgLINE:
            self._boolNum[x][i] = True

    def _markBoolNumByGrid(self, i, j):
        self._initLineBoolNum()
        g = boxer_util.grid(i,j, self.num)
        for x in app.rgGRID:
            for y in app.rgGRID:
                if g[x][y] != 0:
                    self._lineBoolNum[ g[x][y]-1 ] = True
        return self._lineBoolNum

    def _markGridBoolNum(self, i, j):
        self._initGridBoolNum()
        g = boxer_util.grid(i,j, self.num)
        for x in app.rgGRID:
            for y in app.rgGRID:
                if g[x][y] != 0:
                    #self._lineBoolNum[ g[x][y]-1 ] = True
                    self._gridBoolNum[x][y] = True
        return self._gridBoolNum

    def _queryGridBoolNum(self, grid, state):
        for x in app.rgGRID:
            for y in app.rgGRID:
                if grid[x][y]==state:
                    return x,y
        return -1, -1

    def _iterGridNoVal(self, grid):
        for x in app.rgGRID:
            for y in app.rgGRID:
                if grid[x][y]==0:
                    yield (x,y)
        pass

    def _countBoolNumByXY(self, x, y, num):
        c = 0
        for i in app.rgLINE:
            if self.num[i][y] == num:
                c += 1
        for i in app.rgLINE:
            if self.num[x][i] == num:
                c += 1
        return c

    def _countGridBoolNum(self, grid, state):
        c = 0
        for x in app.rgGRID:
            for y in app.rgGRID:
                if grid[x][y]==state:
                    c += 1
        return c

    def _countLineBoolNum(self, line, state):
        c = 0
        for n in line:
            if n == state:
                c += 1
        return c

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
            gridNum = boxer_util.grid(i,j, self.num)

        full = True
        for i in app.rgGRID:
            if direction == 'v':
                full = full and (gridNum[idx][i]!=0)
            else:
                full = full and (gridNum[i][idx]!=0)
        return full

    def checkValidInput(self, num, posX, posY):
        '''
        Check is grid valid, vertical/horizantol line valid
        '''
        g = boxer_util.grid(posX/3,posY/3, self.num)
        if self._countGridBoolNum(g,num) > 1:
            return False

        line = [self.num[posX][i] for i in app.rgLINE]
        if self._countLineBoolNum(line, num) > 1:
            return False

        line = [self.num[i][posY] for i in app.rgLINE]
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
        g = boxer_util.grid(posX/3,posY/3, self.num)
        for i in app.rgGRID:
            for j in app.rgGRID:
                if g[i][j] != 0:
                    self._lineBoolNum[ g[i][j]-1 ] = True
        #Check vertical line
        line = [self.num[posX][i] for i in app.rgLINE]
        for num in line:
            if num != 0:
                self._lineBoolNum[ num-1 ] = True
        #Check horizantol line
        line = [self.num[i][posY] for i in app.rgLINE]
        for num in line:
            if num != 0:
                self._lineBoolNum[ num-1 ] = True

        res = [ i for i in range(1, app.nLINE+1) if not self._lineBoolNum[i-1] ]
        return res
