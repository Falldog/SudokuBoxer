import os
import sys
import time
import gettext
import ConfigParser
from os.path import join
import app

#===============================================================================================
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
def init_config():
    global config
    config = FConfigParser()
    config.read(CONFIG_FILE)

def write_config():
    global config
    f = open(CONFIG_FILE, 'w')
    config.write(f)
    f.close()

init_config()

#===============================================================================================
class DbgViewStream(object):
    ''' stream debug message to OutputDebugString '''
    def __init__(self):
        import ctypes
        self.output = ctypes.windll.Kernel32.OutputDebugStringW
    def write(self, s):
        self.output(to_unicode(s))
    def flush(self):
        pass


#===============================================================================================
translate_gettext = None
def init_translate(lang):
    # looking for MO file : <app.LANG_PATH>/@lang/LC_MESSAGES/@domain.mo
    domain = 'default'
    t = gettext.translation(domain, app.LANG_PATH, languages=[lang])

    global translate_gettext
    translate_gettext = t.ugettext

def get_translate(*argv):
    global translate_gettext
    return translate_gettext(*argv)


#===============================================================================================
def is_dev():
    if not hasattr(sys, 'frozen'):  # source code
        return True
    else:  # PyInstaller frozen state
        return os.getenv('SB_DEBUG', False)


def time_format(secs):
    h = secs/(60*60)
    m = secs/(60) % 60
    s = secs % 60
    return u'%d:%02d:%02d' % (h,m,s)


def get_img_path(img_file):
    return join(app.ROOT_PATH, 'img', img_file)


def to_unicode(s):
    try:
        return unicode(s)
    except UnicodeDecodeError:
        return unicode(s, sys.getfilesystemencoding())

def puzzle2str(puzzle):
    s = ''
    for i in range(9):
        for j in range(9):
            s += str(puzzle[j][i])
    return s

def str2puzzle(s):
    n = []
    for i in range(9):
        n.append([])
        for j in range(9):
            n[-1].append( int(s[j*9+i]) )
    return n

def print_exctime(f):
    def _f(*argv, **argd):
        t = time.time()
        f(*argv, **argd)
        print '[print_exctime] %s, time=%s' % (f.__name__, str(time.time()-t))
    return _f
