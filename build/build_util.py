import os
import sys
import urllib2
from os.path import join
from zipfile import ZipFile


def get_lang_path(basedir, lang, ext='.mo', domain='default'):
    lang_map = {'ENU': 'en_US', 'CHT': 'zh_TW'}
    return join(basedir, lang_map[lang], 'LC_MESSAGES', '%s%s' % (domain, ext))


def generate_version(version_path):
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


def download_zip_extract_to(url, extract_dir):
    zip_tmp_file = join(extract_dir, 'tmp.zip')
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    response = urllib2.urlopen(url)
    with open(zip_tmp_file, 'wb') as f:
        f.write(response.read())

    zip = ZipFile(zip_tmp_file)
    zip.extractall(extract_dir)
    zip.close()
    os.remove(zip_tmp_file)


def prepare_tool_libiconv2(CUR_DIR):
    if sys.platform != 'win32':
        return

    print 'prepare - libiconv2'
    url = 'https://sourceforge.net/projects/gnuwin32/files/libiconv/1.9.2-1/libiconv-1.9.2-1-bin.zip/download'
    bin_dir = join(CUR_DIR, 'bin')
    libiconv2_dir = join(bin_dir, 'libiconv-1.9.2-1')
    libiconv2_bin_dir = join(libiconv2_dir, 'bin')
    if not os.path.exists(libiconv2_dir):
        download_zip_extract_to(url, libiconv2_dir)
    return libiconv2_bin_dir


def prepare_tool_gettext(CUR_DIR):
    if sys.platform != 'win32':
        return

    print 'prepare - gettext'
    url = 'https://sourceforge.net/projects/gnuwin32/files/gettext/0.14.4/gettext-0.14.4-bin.zip/download'
    gettext_dir = join(CUR_DIR, 'bin', 'gettext-0.14.4')
    gettext_bin_dir = join(gettext_dir, 'bin')
    if not os.path.exists(gettext_dir):
        download_zip_extract_to(url, gettext_dir)
    return gettext_bin_dir


def prepare_tool_pyinstaller(CUR_DIR):
    print 'prepare - PyInstaller'
    url = 'https://sourceforge.net/projects/pyinstaller/files/1.5/pyinstaller-1.5.1.zip/download'
    bin_dir = join(CUR_DIR, 'bin')
    pyinstaller_dir = join(bin_dir, 'pyinstaller-1.5.1')
    if not os.path.exists(pyinstaller_dir):
        download_zip_extract_to(url, bin_dir)
    return pyinstaller_dir

