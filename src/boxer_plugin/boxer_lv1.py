import boxer_util
from boxerbase import BoxerBase
from boxer_info import BoxerInfo
from src import app

__author__ = 'Falldog'

class BoxerLv1(BoxerBase):
    def __init__(self, num):
        BoxerBase.__init__(self, num, level=1)

    def run(self):
        for num in app.rgLINE:
            num += 1
            pos, info = self._checkLine(num)
            if pos != (-1, -1):
                return pos, num, info
        return None

    def _checkLine(self, num):
        self._initBoolNum()
        self._markBoolNoVal()
        numPosList = []
        #mark num in all grid
        for i in app.rgGRID:
            for j in app.rgGRID:
                g = boxer_util.grid(i,j, self.num)
                x, y = self._queryGridBoolNum(g, num)
                if (x,y) == (-1,-1):
                    continue
                pos = i*3+x, j*3+y
                self._markBoolNumByXY(*pos)
                numPosList.append( {'pos':pos, 'grid':(i,j)} ) #for boxerInfo

        #check all grid which only one space
        for i in app.rgGRID:
            for j in app.rgGRID:
                g = boxer_util.grid(i,j, self._boolNum)
                g_num = boxer_util.grid(i,j, self.num)
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
