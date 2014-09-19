import wx
import os
import sqlite3
import logging
import app
import util
from os.path import join

_ = util.get_translate
logger = logging.getLogger(__name__)


class UserInfoDB:
    def __init__(self):
        db_path = join(app.PUZZLE_PATH, 'PuzzleDB')
        if not os.path.exists(db_path):
            raise Exception("Puzzle DB doesn't exist!!!!")
        self.db = sqlite3.connect(os.path.relpath(db_path))  #[WARNING!] Use abs path will exception in Window XP Desktop
        self.cursor = self.db.cursor()
        self.curUserID   = -1
        self.curUserName = ''
        
    def initUserDB(self):
        try:
            self.cursor.execute("CREATE TABLE User (id INTEGER PRIMARY KEY, name CHAR(1024))")
        except:
            pass  # DB exist!
            
    def initRecordDB(self):
        try:
            self.cursor.execute("""CREATE TABLE Record (id INTEGER PRIMARY KEY,
                                                        user_id   INTEGER,
                                                        puzzle_id INTEGER,
                                                        time      INTEGER)""")
        except:
            pass  # DB exist!
    
    def getCurUser(self):
        return self.curUserName
    
    def getUserList(self):
        self.initUserDB()
        self.cursor.execute("SELECT name FROM User")
        users = []
        for row in self.cursor:
            users.append(row[0])
        return users
    
    def addUser(self, name):
        self.cursor.execute("INSERT INTO User VALUES(NULL, '%s')" % name)
        self.db.commit()
        
    def setUser(self, name):
        self.initUserDB()
        
        name = name.strip()
        
        self.cursor.execute("SELECT id FROM User WHERE name='%s'" % name)
        if self.cursor.rowcount == 0:
            logger.info('setUser ERROR! User=%s doesn\'t exist!', name)
            return
        row = self.cursor.fetchone()
        _id = row[0]
        self.curUserID   = _id
        self.curUserName = name
        pass
        
    def setRecord(self, puzzle_id, secs):
        ''' secs:total spend time '''
        self.initRecordDB()
        self.cursor.execute("SELECT id, time FROM Record WHERE user_id=%d and puzzle_id=%d" % (self.curUserID, puzzle_id))
        if self.cursor.rowcount == -1:
            self.cursor.execute("INSERT INTO Record VALUES(NULL, %d, %d, %d)" % (self.curUserID, puzzle_id, secs))
        else:
            row = self.cursor.fetchone()
            _id = row[0]
            _time = row[1]
            if _time >= secs:
                self.cursor.execute("UPDATE Record SET time=%d WHERE id=%d" % (_id))
        self.db.commit()
        pass
    def getRecordList(self, user=''):
#        if not user:
#            user = self.curUserName
        _id = self.curUserID
        self.cursor.execute("SELECT puzzle_id, time FROM Record WHERE user_id=%d ORDER BY puzzle_id" % (self.curUserID))
        records = []
        for row in self.cursor:
            records.append( {'id':row[0], 'time':row[1]} )
        return records
        
class UserDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE,
            useMetal=False,
            ):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        
        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)
        
        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle(wx.DIALOG_EX_METAL)
        
        b = wx.Button(self, -1, _('Create a new user'), (0,0))
        self.Bind(wx.EVT_BUTTON, self.onAddNewUser, b)
        
        global g_userInfo
        users = g_userInfo.getUserList()
        self.lb = wx.ListBox(self, 60, (10, 30), (90, 100), users, wx.LB_SINGLE)
        self.lb.SetStringSelection( g_userInfo.getCurUser() )
        
        btn = wx.Button(self, wx.ID_OK, _('OK'), (0, 130))
        btn.SetDefault()
        #btnsizer.AddButton(btn)
        self.Bind(wx.EVT_BUTTON, self.onOK, btn)
        
        
        self.name = u''
        # Now continue with the normal construction of the dialog
        # contents
#        sizer = wx.BoxSizer(wx.VERTICAL)
#
#        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
#
#        self.SetSizer(sizer)
#        sizer.Fit(self)
    
    def GetName(self):
        return self.name
    
    def onOK(self, evt):
        self.name = self.lb.GetStringSelection()
        self.EndModal(wx.ID_OK)
        
    def onAddNewUser(self, evt):
        dlg = wx.TextEntryDialog( self, message=_('Please input a user name'), 
                                        caption=_('Create a User') )
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            self.name = dlg.GetValue()
            global g_userInfo
            g_userInfo.addUser(self.name)
#            msg = wx.MessageDialog(None, _('Please input a correctly number!'), _('Information'), style=wx.OK)
#            msg.ShowModal()
#            msg.Destroy()
        dlg.Destroy()
        
        if ret == wx.ID_OK:
            self.EndModal(wx.ID_OK)

class RecordList(wx.ListCtrl):
    def __init__(self, parent, data, **argd):
        wx.ListCtrl.__init__(
            self, parent, -1, 
            style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES,
            **argd
            )
        
        self.data = data
        
        self.il = wx.ImageList(16, 16)
        
        self.InsertColumn(0, _('PuzzleID'))
        self.InsertColumn(2, _('Time'))
        self.SetColumnWidth(0, 100)
        self.SetColumnWidth(1, 100)

        self.SetItemCount(len(self.data))
        
        #self.attr1 = wx.ListItemAttr()
        #self.attr1.SetBackgroundColour("yellow")

        #self.attr2 = wx.ListItemAttr()
        #self.attr2.SetBackgroundColour("light blue")
        
    def OnGetItemText(self, idx, col):
        if col==0:
            return unicode(self.data[idx]['id'])
        elif col==1:
            return util.time_format(self.data[idx]['time'])
        
class RecordListDialog(wx.Dialog):
    def __init__(self, parent, ID, title, size=(100,500), pos=wx.DefaultPosition, 
                       style=wx.DEFAULT_DIALOG_STYLE,
                       useMetal=False,
                ):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        
        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)
        
        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle(wx.DIALOG_EX_METAL)
        
        global g_userInfo
        records = g_userInfo.getRecordList()
        self.recordList = RecordList(self, records, pos=(0,0), size=(200,500))
        


g_userInfo = None
def InitUserInfo():
    global g_userInfo
    g_userInfo = UserInfoDB()
def GetUserInfo():
    global g_userInfo
    return g_userInfo
