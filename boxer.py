import wx
import app
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)


class Step:
    def __init__(self, i, j, ori_val, val):
        self.pos = i,j
        self.val = val
        self.ori_val = ori_val
        
    def infoRedo(self):
        return self.pos[0], self.pos[1], self.val
    def infoUndo(self):
        return self.pos[0], self.pos[1], self.ori_val


class SudokuBoxer:
    def __init__(self, num):
        self.num = num
        from boxer_plugin.boxer_lv1 import BoxerLv1
        from boxer_plugin.boxer_lv2 import BoxerLv2
        from boxer_plugin.boxer_lv3 import BoxerLv3
        self.boxers = [BoxerLv1(num), BoxerLv2(num), BoxerLv3(num)]

    def checkValidInput(self, v, i, j):
        return self.boxers[0].checkValidInput(v,i,j)  # TODO : refine it

    def boxerNext(self, mode='easy'):
        for boxer in self.boxers:
            ret = boxer.run()
            if ret:
                return ret
        return None

    def boxerBrute(self, defaultNum, autoFill=True, bCheckFromDefault=True):
        '''
        bCheckFromDefault : False -> use self.num to check, should confirm self.num is correctly
        '''
        from boxer_plugin.boxer_brute import BoxerBrute
        self.boxer_brute = BoxerBrute(defaultNum, self.num)
        self.boxer_brute.run(autoFill, bCheckFromDefault)

