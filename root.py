
def ParseArgument():
    import sys
    for arg in sys.argv:
        if arg.upper() in ['DEBUG_LOG']:
            f = open('debug.log', 'w+')
            sys.stderr = f
            sys.stdout = f


def SetDefaultLanguage():
    lang = util.config.get('LANG', 'language', 'ENU')
    App.locale.AddCatalogLookupPathPrefix('.\\lang')
    App.locale.AddCatalog(lang)
    #first launch
    if not os.path.exists(util.CONFIG_FILE):
        sup_lang = [ 'CHT', 'ENU' ]
        trans_sup_lang = [ _(w) for w in sup_lang ]
        dlg = wx.SingleChoiceDialog(None, _('Choice Language'), 'SudokuBoxer', trans_sup_lang, wx.OK)
        dlg.SetSelection(0)
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            lang = sup_lang[ dlg.GetSelection() ]
            App.locale.AddCatalog( lang )
            util.config.set('LANG', 'language', lang)
        dlg.Destroy()


if __name__ == '__main__':
    #parse argument first, for set debug_log
    ParseArgument()
    
    import wx
    import os
    import App
    import user
    import anim
    import util
    from SudokuBoxer import MainFrame
    _ = wx.GetTranslation
    
    app = wx.App(False)
    
    SetDefaultLanguage()
    
    #initial
    user.InitUserInfo() #user info
    
    mode = util.config.get('APP',  'level',    'easy')
    user = util.config.get('APP',  'user',     '')
    
    time = 0
    cur_puzzle = []
    if App.bRecordLastPuzzle and App.lastPuzzle:
        _id         = App.lastPuzzle['id']
        time        = App.lastPuzzle['time']
        puzzle      = util.Str2Puzzle(App.lastPuzzle['puzzleDefault'])
        cur_puzzle  = util.Str2Puzzle(App.lastPuzzle['puzzleCurrent'])
        print '[root] RecordLastPuzzle!\nid=%d\ntime=%s\n    puzzle=%s\ncur puzzle=%s' % (_id, util.Sec2TimeFormat(time), App.lastPuzzle['puzzleDefault'], App.lastPuzzle['puzzleCurrent'])
    else:
        #puzzle loader
        _id, puzzle = App.puzzleLoader.pick(mode)
    
    #anim
    anim.InitAnimManager()
    
    #frame
    frame = MainFrame(None, 'Sudoku Boxer')
    frame.setDefault(_id, puzzle, cur_puzzle)
    if user:
        frame._setUser(user)
    if time:
        frame.setSpendTime(time)
        
    app.MainLoop()
    
    App.SetConfig()
    util.WriteConfig()
    