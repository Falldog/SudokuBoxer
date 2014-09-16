import wx
import weakref
import time
import math
from threading import Thread, RLock, Event

class AnimTimer(wx.Timer):
    def __init__(self, callback):
        wx.Timer.__init__(self)
        self.callback = callback
    def Notify(self):
        self.callback()

class AnimManager:
    def __init__(self):
        self.timer = AnimTimer(self.pooling)
        self.interval = 15 #for Timer interval
        self.task = []
        
    def addTask(self, task):
        if task not in self.task:
            self.task.append(task)
        
        #restart timer
        if not self.timer.IsRunning():
            self.timer.Start(self.interval)
        
    def pooling(self):
        ''' [WARNING!] May not thread safe.
        '''
        #print '---pooling--- task=', len(self.task)
        for task in self.task:
            task.update()
        self.task = [t for t in self.task if not t.stable()]
        
        if len(self.task) == 0 :
            self.timer.Stop()
        
class AnimBase:
    LINEAR = 'linear'
    DECAY  = 'decay'
    def __init__(self, parent, pos=0, type='linear'):
        self._from = pos
        self._to   = pos
        self._cur  = pos
        
        self._t      = 0
        self._startT = 0
        self.setType(type)
        
        self._stable = True
        self._parent = weakref.ref(parent)
    
    def get_parent(self):
        return self._parent()
    parent = property(get_parent)
    
    def __float__(self):
        return float(self._cur)
    
    def __int__(self):
        return int(float(self))
    
    def __nonzero__(self):
        return float(self) != 0
    
    def __long__(self):
        return long(float(self))
    
    def __neg__(self):
        return -float(self)
    
    def setType(self, type):
        assert type in [AnimBase.LINEAR, AnimBase.DECAY]
        self._type = type
    
    def reset(self, _sec, _to):
        self._to = _to
        self._t  = _sec
        self.dirty()
        
        global g_animManager
        g_animManager.addTask(self)
        self.start()
        
    def assign(self, _to):
        self._cur = self._from = self._to = _to
        self._t = 0
        self.dirty()
        
    def dirty(self):
        p = self.parent
        if p:
            p.Refresh()
    
    def val(self):
        return float(self)
    
    def target(self):
        return self._to
        
    def stable(self):
        return self._stable
    
    def start(self):
        self._startT = time.time()
        self._stable = False
        
    def update(self):
        t = time.time()
        #print 'update:diff=%f, t=%f' % (t-self._startT, self._t)
        if (t-self._startT) >= self._t:
            self._stable = True
            self._cur = self._from = self._to
        else:
            perc = (t-self._startT) / (self._t)
            if self._type == AnimBase.LINEAR:
                self._cur = self._from + (self._to-self._from)*perc
            elif self._type == AnimBase.DECAY:
                pos = math.sin( perc * math.pi/2 )#sin 0~math.pi/2 -> 0~1
                self._cur = self._from + (self._to-self._from)*pos
        self.dirty()


#global animation manager
g_animManager = None

def InitAnimManager():
    global g_animManager
    g_animManager = AnimManager()

