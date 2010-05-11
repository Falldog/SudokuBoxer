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
    