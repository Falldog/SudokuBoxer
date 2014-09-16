import app
import util
import logging
from copy import deepcopy
import boxer_util
from boxerbase import BoxerBase
__author__ = 'Falldog'
logger = logging.getLogger(__name__)


class BoxerBrute(BoxerBase):
    def __init__(self, default_num, num):
        BoxerBase.__init__(self, num, level=0)
        self.default_num = default_num

    def run(self, autoFill=True, bCheckFromDefault=True):
        '''
        bCheckFromDefault : False -> use self.num to check, should confirm self.num is correctly
        '''
        if not autoFill:
            oriNum = deepcopy(self.num)

        if bCheckFromDefault:
            self.num = deepcopy(self.default_num)
        else:
            oriDefault = deepcopy(self.default_num)
            self.default_num = deepcopy(self.num) #set num to default


        #set validList
        for x in app.rgLINE:
            for y in app.rgLINE:
                if self.num[x][y] == 0:
                    self.num[x][y].validList = self.getValidNum(x,y)

        ret = self._brute(0, 0)
        logger.info('ret=%s puzzle=%s', ret, util.puzzle2str(self.num))
        answer = self.num


        if not autoFill:
            self.num = oriNum
        if not bCheckFromDefault:
            self.default_num = oriDefault
        return answer

    def _brute(self, i, j):
        if j*app.nLINE+i == app.nLINE*app.nLINE:  #the last cell
            return True

        if i==app.nLINE-1:
            next = 0, j+1
        else:
            next = i+1, j

        if self.default_num[i][j] != 0:  #default value
            return self._brute(*next)
        else:
            #try to put number in validList to try valid or not
            for n in self.num[i][j].validList:
                self.num[i][j].val = n
                if boxer_util.check_valid(self.num) and self._brute(*next):  #checkValid() define by class NumberBoard
                    return True

            self.num[i][j].val = 0  #set none
            return False
