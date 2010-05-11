#
#    SudokuBoxer is a Sudoku GUI game & solver
#
#    Copyright (C) 2010  Falldog
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import wx
import os
import App
import user
import anim
import util
from SudokuBoxer import MainFrame
_ = wx.GetTranslation



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
    import sys
    for arg in sys.argv:
        if arg.upper() in ['DEBUG_LOG']:
            f = open('debug.log', 'w+')
            sys.stderr = f
            sys.stdout = f
    
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
    