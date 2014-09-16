import wx
import sys
import app
import logging

logger = logging.getLogger(__name__)


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

class MainApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, False)
        
        self.hookStdOutFile = None
        self.InitLogging()

    def InitLogging(self):
        import util
        if util.is_dev():
            FORMAT = '%(asctime)s [%(levelname)s] [%(name)s::%(funcName)s] %(message)s'
            logging.basicConfig(format=FORMAT, level=logging.INFO)


if __name__ == '__main__':
    import os
    import user
    import anim
    import util
    from main_frame import MainFrame
    _ = wx.GetTranslation
    
    mainApp = MainApp()

    set_default_language()
    
    #initial
    user.InitUserInfo() #user info
    
    mode = util.config.get('APP', 'level', 'easy')
    user = util.config.get('APP', 'user', '')
    
    time = 0
    cur_puzzle = []
    if app.bRecordLastPuzzle and app.lastPuzzle:
        _id         = app.lastPuzzle['id']
        time        = app.lastPuzzle['time']
        puzzle      = util.str2puzzle(app.lastPuzzle['puzzleDefault'])
        cur_puzzle  = util.str2puzzle(app.lastPuzzle['puzzleCurrent'])
        logger.info('RecordLastPuzzle! id=%d, time=%s', _id, util.time_format(time))
        logger.info('puzzle=%s', app.lastPuzzle['puzzleDefault'])
        logger.info('cur puzzle=%s', app.lastPuzzle['puzzleCurrent'])
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

    app.SetConfig()
    util.write_config()
    