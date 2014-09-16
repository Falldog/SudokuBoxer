from copy import deepcopy

from src import app

__author__ = 'Falldog'

def grid(x, y, num):
    g = []
    for i in app.rgGRID:
        g.append( [0 for j in app.rgGRID] )

    for i in app.rgGRID:
        for j in app.rgGRID:
            g[i][j] = num[x* app.nGRID+i][y* app.nGRID+j]
    return g

def check_valid(num):
    '''
    Check the board is valid or not.
    Check is the line/grid is any number duplicate.
    Ex: 123456788 -> False, 8 duplicate
        123456789 -> True
    '''
    boolNumFalse = [False for i in app.rgLINE]
    #Check vertical & horizontal
    query_hor = lambda x,y: num[x][y]
    query_ver = lambda y,x: num[x][y]
    for query in [query_hor, query_ver]:
        for x in app.rgLINE:
            boolNum = deepcopy(boolNumFalse)
            for y in app.rgLINE:
                n = query(x,y)
                if n == 0: continue
                if boolNum[n-1]:  #duplicate
                    return False
                boolNum[n-1] = True
    #Check grid
    for i in app.rgGRID:
        for j in app.rgGRID:
            boolNum = deepcopy(boolNumFalse)
            g = grid(i,j, num)
            for x in app.rgGRID:
                for y in app.rgGRID:
                    n = g[x][y]
                    if n == 0: continue
                    if boolNum[n-1]:  #duplicate
                        return False
                    boolNum[n-1] = True
    return True

def check_finish(num):
    boolNumFalse = [False for i in app.rgLINE]
    for i in app.rgLINE:
        for j in app.rgLINE:
            if num[i][j]==0:
                return False
    return True


