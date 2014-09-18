import os, sys


def GeneratePyList(output_file):
    PY_DIR = '..\\'
    f = open(output_file, 'w')
    files = os.listdir(PY_DIR)
    for fname in files:
        if os.path.splitext(fname)[1] != '.py' : continue
        f.write(PY_DIR+fname+'\n')
    
    _GenerateXRCTranslateString('.\\xrc_string.py')
    f.write('xrc_string.py')
    f.close()

def _GenerateXRCTranslateString(filename=''):
    XRC_Folder = r'..\resource\xrc'
    xrcList = os.listdir(XRC_Folder)
    strFiles = ''
    for xrc in xrcList:
        if xrc.lower() in ['.svn']: continue
        strFiles +=  ' ' + os.path.join(XRC_Folder, xrc)
    os.system('python pywxrc.py -o %s -g %s' % (filename, strFiles))
    
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

