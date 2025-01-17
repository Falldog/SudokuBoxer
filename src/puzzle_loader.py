﻿import wx
import os
import util
import sqlite3
import logging
import app
from os.path import join

logger = logging.getLogger(__name__)
PUZZLE_EXT = '.sb'
_puzzle_loader = None

def get_puzzle_loader():
    global _puzzle_loader
    if _puzzle_loader is None:
        _puzzle_loader = PuzzleLoaderDB()
    return _puzzle_loader


'''
class PuzzleLoader:
    def __init__(self):
        self.folder = os.path.abspath(os.curdir) + u'\\puzzle'
        if not os.path.exists(self.folder):
            raise 'Puzzle Folder doesn\'t exist!!!!'
        
        #file list
        self.easy   = []
        self.medium = []
        self.hard   = []
        self.evil   = []
        
        self.parseFolder('easy')
        self.parseFolder('medium')
        self.parseFolder('hard')
        self.parseFolder('evil')
    
    def parseFolder(self, mode):
        fileList = os.listdir( self.folder+u'\\'+mode )
        for f in fileList:
            if os.path.splitext(f)[1].lower() != '.sb':
                continue
            if f.count('_') > 1:
                continue
            l = eval('self.'+mode)
            l.append(f)
        pass
        
    def parseFile(self, mode, file_name):
        path = self.folder + u'\\' + mode + u'\\' + file_name
        if not os.path.exists( path ):
            logger.error("[PuzzleLoader] File Doesn't exist! filename=%s", file_name)
            return []
        
        sudoku = []
        f = open(path, 'r')
        try:
            ls = f.readlines()
            ver = ls[0].split()
            if len(ver)==2 and ver[0]=='version':
                
                #version 1.0
                if float(ver[1])==1.0:
                    count = 1
                    while ls[count]!='\n':
                        count += 1
                    count += 1 #skip space line
                    if len(ls)-count < 9-1:
                        raise '[PuzzleLoader] Sudoku Line number wrong!!!'
                    num = ls[count:count+9]
                    
                    for n in num:
                        sudoku.append( [int(i) for i in n if i!='\n'] )
                        if len(sudoku[-1]) != 9:
                            raise '[PuzzleLoader] Sudoku number wrong!!! %s' % n
        except:
            logger.error('[PuzzleLoader] Load File fail!')
        
        f.close()
        return sudoku
    
    def pick(self, mode='easy'):
        assert mode in ['easy', 'medium', 'hard', 'evil']
        
        l = eval('self.%s'%mode)
        if len(l) == 0 :
            return []
        
        import random
        while True:
            r = random.random()
            idx = int(r*len(l))
            #print 'Pick=',r, idx
            puzzle = self.parseFile(mode, l[idx])
            if puzzle:
                return puzzle
'''

class PuzzleLoaderDB:
    def __init__(self):
        db_path = join(app.PUZZLE_PATH, 'PuzzleDB')
        if not os.path.exists(db_path):
            raise Exception("Puzzle DB doesn't exist!!!!")
        self.db = sqlite3.connect(os.path.relpath(db_path))  #[WARNING!] Use abs path will exception in Window XP Desktop
        self.cursor = self.db.cursor()
        
        #initial count
        self.count = {}
        for level in ['easy', 'medium', 'hard', 'evil']:
            res = self.cursor.execute('SELECT COUNT(*) FROM puzzle_%s' % (level))
            for r in res:
                self.count[level] = int(r[0])
                logger.info('COUNT: %s, %d', level, self.count[level])
                break
        pass
        
    def getCount(self, level):
        if not self.count.has_key(level):
            return 0
        else:
            return self.count[level]
            
    def __pickPuzzle(self, mode, _id):
        self.cursor.execute('SELECT puzzle FROM puzzle_%s WHERE id=%d' % (mode, _id))
        n = []
        p = ''
        for row in self.cursor:
            p = row[0]
            n = util.str2puzzle(p)
        return n, p
        
    def pick(self, mode='easy', _id=-1):
        assert mode in ['easy', 'medium', 'hard', 'evil']
        
        _count = self.count[mode]
        if _id > -1:
            if _id > _count:
                raise Exception('ID Number Error!')
            puzzle, row_data = self.__pickPuzzle(mode, _id)
            
        else:
            import random
            while True:
                r = random.random()
                _id = int(r*_count)
                puzzle, row_data = self.__pickPuzzle(mode, _id)
                if puzzle:
                    break
        
        logger.info('mode=%s, id=%d, puzzle=%s', mode, _id, row_data)
        return _id, puzzle
    