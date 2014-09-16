import wx
import sys
import app

def set_default_language():
    lang = util.config.get('LANG', 'language', 'ENU')
    app.locale.AddCatalogLookupPathPrefix('.\\lang')
    app.locale.AddCatalog(lang)
    #first launch
    if not os.path.exists(util.CONFIG_FILE):
        sup_lang = [ 'CHT', 'ENU' ]
        trans_sup_lang = [ _(w) for w in sup_lang ]
        dlg = wx.SingleChoiceDialog(None, _('Choice Language'), 'SudokuBoxer', trans_sup_lang, wx.OK)
        dlg.SetSelection(0)
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            lang = sup_lang[ dlg.GetSelection() ]
            app.locale.AddCatalog( lang )
            util.config.set('LANG', 'language', lang)
        dlg.Destroy()

class HookStdOut:
    def __init__(self, f, of):
        self.encoding = sys.getfilesystemencoding()
        self.f = f
        self.of = of
    def write(self, s):
        if isinstance(s, unicode):
            s = s.encode(self.encoding)
        self.f.write(s)
        self.of.write(s)

class MainApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, False)
        
        self.hookStdOutFile = None
    
    def close(self):
        #self.UnHookStdOut()
        pass
    
    def ParseArgument(self):
        #parse argument first, for set debug_log
        for arg in sys.argv:
            if arg.upper() in ['DEBUG_LOG']:
                self.HookStdOut()
    
    def HookStdOut(self):
        import sys
        self.hookStdOutFile = open('debug.log', 'w+')
        sys.stderr = HookStdOut(self.hookStdOutFile, sys.stderr)
        sys.stdout = HookStdOut(self.hookStdOutFile, sys.stdout)
    
    def UnHookStdOut(self):
        import sys
        if self.hookStdOutFile:
            self.hookStdOutFile.close()
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__


if __name__ == '__main__':
    import os
    import user
    import anim
    import util
    from main_frame import MainFrame
    _ = wx.GetTranslation
    
    mainApp = MainApp()
    mainApp.ParseArgument()
    
    set_default_language()
    
    #initial
    user.InitUserInfo() #user info
    
    mode = util.config.get('APP',  'level',    'easy')
    user = util.config.get('APP',  'user',     '')
    
    time = 0
    cur_puzzle = []
    if app.bRecordLastPuzzle and app.lastPuzzle:
        _id         = app.lastPuzzle['id']
        time        = app.lastPuzzle['time']
        puzzle      = util.str2puzzle(app.lastPuzzle['puzzleDefault'])
        cur_puzzle  = util.str2puzzle(app.lastPuzzle['puzzleCurrent'])
        print '[root] RecordLastPuzzle!\nid=%d\ntime=%s\n    puzzle=%s\ncur puzzle=%s' % (_id, util.time_format(time), app.lastPuzzle['puzzleDefault'], app.lastPuzzle['puzzleCurrent'])
    else:
        #puzzle loader
        _id, puzzle = app.puzzleLoader.pick(mode)
    
    #anim
    anim.InitAnimManager()
    
    #frame
    frame = MainFrame(None, 'Sudoku Boxer')
    frame.setDefault(_id, puzzle, cur_puzzle)
    if user:
        frame._setUser(user)
    if time:
        frame.setSpendTime(time)
        
    mainApp.MainLoop()
    mainApp.close()
    
    app.SetConfig()
    util.write_config()
    