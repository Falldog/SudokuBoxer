import app
import logging
from copy import deepcopy
import boxer_util
from boxerbase import BoxerBase
from boxer_info import BoxerInfo

__author__ = 'Falldog'
logger = logging.getLogger(__name__)


class BoxerLv2(BoxerBase):
    def __init__(self, num):
        BoxerBase.__init__(self, num, level=2)

    def run(self):
        '''
        Check line/grid in soso way.
        Ex:
        line===12 456 89
                 X       -> check 3 & 7, if 3 exist, this X is 7
                     X   -> check 3 & 7, if 3 exist, this X is 7
        '''
        logger.info('-----------boxerNextSoSo-----------')
        boolNumFalse = [False for i in app.rgLINE]
        #check vertical
        for i in app.rgLINE:
            boolNum = deepcopy(boolNumFalse)
            #mark bool number
            for j in app.rgLINE:
                n = self.num[i][j]
                if n > 0 :
                    boolNum[n-1] = True

            #check non-value line
            for j in app.rgLINE:
                n = self.num[i][j]
                if n == 0:
                    numPosList = []
                    checkBoolNum = deepcopy(boolNum)
                    for line_i in app.rgLINE:
                        if line_i == i: continue
                        n = self.num[line_i][j]
                        if n > 0 and checkBoolNum[n-1]==False:
                            checkBoolNum[n-1] = True
                            numPosList.append( {'pos':(line_i,j), 'num':n} )
                    if self._countLineBoolNum(checkBoolNum,False) == 1:
                        logger.info('CheckVertical line=%s\n (i,j)=%s, checkBoolNum=%s',
                                    [int(self.num[i][n]) for n in app.rgLINE], (i,j), checkBoolNum)
                        num = checkBoolNum.index(False)+1

                        #set boxer info
                        bi = BoxerInfo()
                        bi.add('cell line', 'v', i)
                        conflitNumList = [num]
                        for _n in numPosList:
                            bi.add('cell', _n['pos'][0], _n['pos'][1])
                            conflitNumList.append(_n['num'])
                        for idx in app.rgLINE:
                            if self.num[i][idx] == 0 and idx != j:
                                bi.add('cell tips', i, idx, conflitNumList)
                        return (i,j), num, bi
            pass
        #check horizantol
        for j in app.rgLINE:
            boolNum = deepcopy(boolNumFalse)
            #mark bool number
            for i in app.rgLINE:
                n = self.num[i][j]
                if n > 0 :
                    boolNum[n-1] = True

            #check non-value line
            for i in app.rgLINE:
                n = self.num[i][j]
                if n == 0:
                    numPosList = []
                    checkBoolNum = deepcopy(boolNum)
                    for line_j in app.rgLINE:
                        if line_j == j: continue
                        n = self.num[i][line_j]
                        if n > 0 and checkBoolNum[n-1]==False:
                            checkBoolNum[n-1] = True
                            numPosList.append( {'pos':(line_i,j), 'num':n} )
                    if self._countLineBoolNum(checkBoolNum,False) == 1:
                        logger.info('CheckHorizantol line=%s\n (i,j)=%s, checkBoolNum=%s',
                                    [self.num[n][j] for n in app.rgLINE], (i,j), checkBoolNum)
                        num = checkBoolNum.index(False)+1

                        #set boxer info
                        bi = BoxerInfo()
                        bi.add('cell line', 'h', j)
                        conflitNumList = [num]
                        for _n in numPosList:
                            bi.add('cell', _n['pos'][0], _n['pos'][1])
                            conflitNumList.append(_n['num'])
                        for idx in app.rgLINE:
                            if self.num[idx][j] == 0 and idx != i:
                                bi.add('cell tips', idx, j, conflitNumList)
                        return (i,j), num, bi

        #check Grid
        for i in app.rgGRID:
            for j in app.rgGRID:
                boolNum = deepcopy(self._markBoolNumByGrid(i,j))   #represent 1~9

                g = boxer_util.grid(i,j, self.num)
                for x in app.rgGRID:
                    for y in app.rgGRID:
                        if g[x][y]!=0: continue
                        gx, gy = x + i*app.nGRID, y + j*app.nGRID #global x,y
                        conflitNumList = []
                        checkBoolNum = deepcopy(boolNum)
                        for num_idx in app.rgLINE:
                            if checkBoolNum[num_idx]: continue
                            num = num_idx+1
                            if self._countBoolNumByXY(gx,gy, num) > 0:
                                checkBoolNum[num_idx] = True
                                conflitNumList.append(num)

                        if self._countLineBoolNum(checkBoolNum, False) == 1:
                            num = checkBoolNum.index(False)+1
                            logger.info('CheckGrid (i,j)=%s checkBoolNum=%s', (gx,gy), checkBoolNum)

                            #set boxer info
                            bi = BoxerInfo()
                            bi.add('cell grid', i, j)
                            conflitNumList.append(num)
                            #mark the conflit cells out of grid
                            for _x in app.rgLINE:#vertical
                                if self.num[_x][gy] in conflitNumList:
                                    bi.add('cell', _x, gy)
                            for _y in app.rgLINE:#horizantol
                                if self.num[gx][_y] in conflitNumList:
                                    bi.add('cell', gx, _y)
                            #mark cell tips in grid
                            for _i in app.rgGRID:
                                for _j in app.rgGRID:
                                    _x, _y = _i + i*app.nGRID, _j + j*app.nGRID
                                    if self.num[_x][_y] == 0 and (_x,_y)!=(gx,gy):
                                        bi.add('cell tips', _x, _y, conflitNumList)
                            return (gx,gy), num, bi
        return None

