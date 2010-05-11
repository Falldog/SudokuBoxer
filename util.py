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
import time
import ConfigParser


class FConfigParser(ConfigParser.ConfigParser):
    def __init__(self, *argv, **argd):
        ConfigParser.ConfigParser.__init__(self, *argv, **argd)
    
    def get(self, section, option, default='', raw=False, vars=''):
        try:
            return ConfigParser.ConfigParser.get(self, section, option)
        except ConfigParser.NoSectionError:
            self.add_section(section)
            self.set(section, option, default)
            return default
        except ConfigParser.NoOptionError:
            self.set(section, option, default)
            return default
config = None

CONFIG_FILE = 'config.ini'
def InitConfig():
    global config
    config = FConfigParser()
    config.read(CONFIG_FILE)
def WriteConfig():
    global config
    f = open(CONFIG_FILE, 'w')
    config.write(f)
    f.close()

InitConfig()



def Sec2TimeFormat(secs):
    h = secs/(60*60)
    m = secs/(60) % 60
    s = secs % 60
    return u'%d:%02d:%02d' % (h,m,s)

ori_unicode = unicode
def unicode(s):
    try:
        return ori_unicode(s)
    except UnicodeDecodeError:
        return ori_unicode(s,'mbcs')


def Puzzle2Str(puzzle):
    s = ''
    for i in range(9):
        for j in range(9):
            s += str(puzzle[j][i])
    return s
def Str2Puzzle(s):
    n = []
    for i in range(9):
        n.append([])
        for j in range(9):
            n[-1].append( int(s[i*9+j]) )
    return n
    
def print_exctime(f):
    def _f(*argv, **argd):
        t = time.time()
        f(*argv, **argd)
        print '[print_exctime] %s, time=%s' % (f.__name__, str(time.time()-t))
    return _f
    