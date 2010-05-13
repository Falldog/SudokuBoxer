import os, sys


def GeneratePyList(output_file):
    PY_DIR = '..\\'
    f = open(output_file, 'w')
    files = os.listdir(PY_DIR)
    for fname in files:
        if os.path.splitext(fname)[1] != '.py' : continue
        f.write(PY_DIR+fname+'\n')
    f.close()
    
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
    


if len(sys.argv) > 1:
    task = sys.argv[1]
    if task == 'generate_py_list':
        GeneratePyList( sys.argv[2] )
        
    elif task == 'generate_version':
        GenerateVersion( sys.argv[2] )
        