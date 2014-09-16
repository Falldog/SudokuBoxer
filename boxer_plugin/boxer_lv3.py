import app
import logging
from copy import deepcopy
import boxer_util
from boxerbase import BoxerBase
from boxer_info import BoxerInfo

__author__ = 'Falldog'
logger = logging.getLogger(__name__)


class BoxerLv3(BoxerBase):
    def __init__(self, num):
        BoxerBase.__init__(self, num, level=3)

    def run(self):
        '''
        Check line/grid in soso2 way.
        Ex:
        line===12  56 89
                 XX  X   -> check 3, if 2*X has 3, the only 1X is 3
                 XX  X   -> check 4, if 2*X has 4, the only 1X is 4
                 XX  X   -> check 7, if 2*X has 7, the only 1X is 7
        '''
        logger.info('-----------boxerNextSoSo2-----------')
        boolNumFalse = [False for i in app.rgLINE]
        #check vertical
        for i in app.rgLINE:
            boolNum = deepcopy(boolNumFalse)
            lineBoolNum = deepcopy(boolNumFalse)
            #mark bool number
            for j in app.rgLINE:
                n = self.num[i][j]
                if n > 0 :
                    boolNum[n-1] = True
                    lineBoolNum[j] = True

            for num_idx in app.rgLINE:
                if boolNum[num_idx]: continue
                checkLineBoolNum = deepcopy(lineBoolNum)
                num = num_idx+1

                #check grid
                for j in app.rgGRID:
                    grid_i = int(i / 3)
                    g = boxer_util.grid(grid_i, j, self.num)
                    pos = self._queryGridBoolNum(g, num)
                    if pos != (-1,-1):
                        checkLineBoolNum[j*3] = checkLineBoolNum[j*3+1] = checkLineBoolNum[j*3+2] = True

                #check line
                for j in app.rgLINE:
                    if self.num[i][j] > 0: continue

                    for line_i in app.rgLINE:
                        if self.num[line_i][j] == num:
                            checkLineBoolNum[j] = True
                            break

                if self._countLineBoolNum(checkLineBoolNum, False) == 1:
                    logger.info('CheckVertical line=%s\n (i,j)=%s, checkLineBoolNum=%s',
                                [int(self.num[i][n]) for n in app.rgLINE], (i,j), checkLineBoolNum)
                    j = checkLineBoolNum.index(False)
                    return (i,j), num, None

        #check horizontal
        for j in app.rgLINE:
            boolNum = deepcopy(boolNumFalse)
            lineBoolNum = deepcopy(boolNumFalse)

            #mark bool number
            for i in app.rgLINE:
                n = self.num[i][j]
                if n > 0 :
                    boolNum[n-1] = True
                    lineBoolNum[i] = True

            for num_idx in app.rgLINE:
                if boolNum[num_idx]: continue
                checkLineBoolNum = deepcopy(lineBoolNum)
                num = num_idx+1

                #check grid
                for i in app.rgGRID:
                    grid_j = int(j / 3)
                    g = boxer_util.grid(i, grid_j, self.num)
                    pos = self._queryGridBoolNum(g, num)
                    if pos != (-1,-1):
                        checkLineBoolNum[i*3] = checkLineBoolNum[i*3+1] = checkLineBoolNum[i*3+2] = True

                #check line
                for i in app.rgLINE:
                    if self.num[i][j] > 0: continue

                    for line_j in app.rgLINE:
                        if self.num[i][line_j] == num:
                            checkLineBoolNum[i] = True
                            break
                if self._countLineBoolNum(checkLineBoolNum, False) == 1:
                    logger.info('CheckVertical line=%s\n (i,j)=%s, checkLineBoolNum=%s',
                                [int(self.num[n][j]) for n in app.rgLINE], (i,j), checkLineBoolNum)
                    i = checkLineBoolNum.index(False)
                    return (i,j), num, None

        #check Grid
        for i in app.rgGRID:
            for j in app.rgGRID:
                boolNum = deepcopy(self._markBoolNumByGrid(i,j)) #represent 1~9
                gridBoolNum = deepcopy(self._markGridBoolNum(i,j)) #Grid has value

                g = boxer_util.grid(i,j, self.num)
                for num_idx in app.rgLINE:
                    if boolNum[num_idx]: continue
                    num = num_idx + 1
                    checkGridBoolNum = deepcopy(gridBoolNum)

                    for pos in self._iterGridNoVal(g):
                        gx, gy = pos[0] + i*app.nGRID, pos[1] + j*app.nGRID #global x,y
                        if self._countBoolNumByXY(gx, gy, num) > 0:
                            checkGridBoolNum[pos[0]][pos[1]] = True
                    #only one
                    if self._countGridBoolNum(checkGridBoolNum, False) == 1:
                        pos = self._queryGridBoolNum(checkGridBoolNum, False)
                        gx, gy = pos[0] + i*app.nGRID, pos[1] + j*app.nGRID #global x,y
                        logger.info('CheckGrid (i,j)=%s, GridBoolNum=%s', pos, checkGridBoolNum)
                        return (gx,gy), num, None
        return None
