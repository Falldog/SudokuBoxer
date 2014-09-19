import os
import sys
from os.path import join

def get_lang_path(basedir, lang, ext='.mo', domain='default'):
    lang_map = {'ENU': 'en_US', 'CHT': 'zh_TW'}
    return join(basedir, lang_map[lang], 'LC_MESSAGES', '%s%s' % (domain, ext))


def GenerateVersion(version_path):
    import datetime
    f = open(version_path, 'r')
    lines = f.readlines()
    f.close()
    
    ver = lines[0].strip()
    td = datetime.date.today()
    ver_date = '%02d%02d' % (td.month, td.day)
    
    f = open(version_path, 'w')
    f.write('%s\n%s' % (ver, ver_date))
    f.close()

    return '%s.%s' % (ver, ver_date)

