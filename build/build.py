#!/usr/bin/env python
# @author: Falldog
#

import os
import sys
import shutil
import argparse
import subprocess
import build_util
from build_util import get_lang_path
from os.path import join, dirname, abspath

CUR_DIR = abspath(dirname(__file__))
ROOT_DIR = abspath(join(CUR_DIR, '..'))
DIST_DIR = join(CUR_DIR, 'dist')
PUZZLE_DIR = join(CUR_DIR, 'puzzle')
VERSION_PATH = join(ROOT_DIR, 'version')
SRC_DIR = join(ROOT_DIR, 'src')
LANG_DIR = join(ROOT_DIR, 'lang')
XRC_DIR = join(ROOT_DIR, 'resource', 'xrc')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--update-po', dest='update_po', default=False, action='store_true',
                        help='update language translating PO file')
    args = parser.parse_args()
    return args


class Builder():
    def __init__(self):
        self.ver_date = build_util.generate_version(VERSION_PATH)
        self.dist_dir = join(DIST_DIR, 'SudokuBoxer-%s' % self.ver_date)
        self.puzzle_dir = join(self.dist_dir, 'puzzle')
        self.lang_dir = join(self.dist_dir, 'lang')

        if not os.path.isdir(DIST_DIR):
            os.mkdir(DIST_DIR)
        if os.path.isdir(self.dist_dir):
            shutil.rmtree(self.dist_dir)
        if os.path.isdir(join(DIST_DIR, 'SudokuBoxer')):
            shutil.rmtree(join(DIST_DIR, 'SudokuBoxer'))

        self.gettext_dir = build_util.prepare_tool_gettext(CUR_DIR)
        self.libiconv2_dir = build_util.prepare_tool_libiconv2(CUR_DIR)
        self.pyinstaller_dir = build_util.prepare_tool_pyinstaller(CUR_DIR)

    def build(self):
        self.update_MUI_mo()
        self.process_pyinstaller()
        self.copy_resource()
        self.remove_redundant_files()

    def update_MUI_po(self):
        ''' update PO file for translating it '''
        py_list_path = 'py_list.txt'
        msgmerge_flags = '--backup=off --sort-output --no-fuzzy-matching --update'
        xrc_string_path = join(CUR_DIR, 'xrc_string.py')
        self.generate_xrc_translate_string(xrc_string_path)
        self.generate_py_list(py_list_path, [ROOT_DIR, SRC_DIR], [xrc_string_path])
        env = os.environ.copy()
        if sys.platform == 'win32':
            env['PATH'] += os.pathsep + self.gettext_dir
            env['PATH'] += os.pathsep + self.libiconv2_dir

        subprocess.check_call('xgettext -o "%s" --files-from=%s' % (join(LANG_DIR, 'base.po'),
                                                                    py_list_path),
                              env=env, shell=True)
        subprocess.check_call('msgmerge %s "%s" "%s"' % (msgmerge_flags,
                                                         get_lang_path(LANG_DIR, 'ENU', ext='.po'),
                                                         join(LANG_DIR, 'base.po')),
                              env=env, shell=True)
        subprocess.check_call('msgmerge %s "%s" "%s"' % (msgmerge_flags,
                                                         get_lang_path(LANG_DIR, 'CHT', ext='.po'),
                                                         join(LANG_DIR, 'base.po')),
                              env=env, shell=True)
        os.remove(py_list_path)
        os.remove(xrc_string_path)

    def update_MUI_mo(self):
        ''' convert .po(TEXT file) to .mo(Binary file) '''
        msgmerge_output_flags = '--output-file'
        env = os.environ.copy()
        if sys.platform == 'win32':
            env['PATH'] += os.pathsep + self.gettext_dir
            env['PATH'] += os.pathsep + self.libiconv2_dir
        
        subprocess.check_call('msgfmt %s "%s" "%s"' % (msgmerge_output_flags,
                                                       get_lang_path(LANG_DIR, 'CHT', ext='.mo'),
                                                       get_lang_path(LANG_DIR, 'CHT', ext='.po')),
                              env=env, shell=True)
        subprocess.check_call('msgfmt %s "%s" "%s"' % (msgmerge_output_flags,
                                                       get_lang_path(LANG_DIR, 'ENU', ext='.mo'),
                                                       get_lang_path(LANG_DIR, 'ENU', ext='.po')),
                              env=env, shell=True)

    def generate_py_list(self, output_file, search_dirs=(), extra_files=()):
        with open(output_file, 'w') as f:
            for d in search_dirs:
                for fname in os.listdir(d):
                    if os.path.splitext(fname)[1] != '.py' : continue
                    f.write(join(d, fname))
                    f.write('\n')

            for file in extra_files:
                f.write(file)
                f.write('\n')

    def generate_xrc_translate_string(self, filename=''):
        xrcList = os.listdir(XRC_DIR)
        strFiles = ''
        for xrc in xrcList:
            if xrc.lower() in ['.svn', '.git']: continue
            strFiles +=  ' ' + join(XRC_DIR, xrc)
        subprocess.check_call('python pywxrc.py -o %s -g %s' % (filename, strFiles), shell=True)

    def process_pyinstaller(self):
        cwd = os.getcwd()
        os.chdir(CUR_DIR)
        try:
            subprocess.check_call('python %s SudokuBoxer.spec' % join(self.pyinstaller_dir, 'pyinstaller.py'), shell=True)

            # rename to SudokuBoxer-[version]
            ori_dist_dir = join(DIST_DIR, 'SudokuBoxer')
            if os.path.exists(ori_dist_dir):
                os.rename(ori_dist_dir, self.dist_dir)

        finally:
            os.chdir(cwd)

    def copy_resource(self):
        shutil.copyfile(join(ROOT_DIR, 'version'), join(self.dist_dir, 'version'))

        os.mkdir(self.puzzle_dir)
        shutil.copyfile(join(ROOT_DIR, 'puzzle', 'PuzzleDB-1000'), join(self.puzzle_dir, 'PuzzleDB'))

        shutil.copytree(join(ROOT_DIR, 'img'), join(self.dist_dir, 'img'))

        # copy lang
        self.lang_dir = join(self.dist_dir, 'lang')
        os.mkdir(self.lang_dir)
        for d in os.listdir(LANG_DIR):
            if not os.path.isdir(join(LANG_DIR, d)):
                continue
            os.makedirs(join(self.lang_dir, d, 'LC_MESSAGES'))
            shutil.copyfile(join(LANG_DIR, d, 'LC_MESSAGES', 'default.mo'),
                            join(self.lang_dir, d, 'LC_MESSAGES', 'default.mo'))

        # copy XRC resource
        dist_xrc_dir = join(self.dist_dir, 'resource', 'xrc')
        os.makedirs(dist_xrc_dir)
        shutil.copyfile(join(XRC_DIR, 'PreferenceDialog.xrc'), join(dist_xrc_dir, 'PreferenceDialog.xrc'))

    def remove_redundant_files(self):

        # PyInstaller-1.5.1 will collect redundant files, include
        # * API-MS-Win-Core-Debug-L1-1-0.dll
        # * API-MS-Win-Core-ErrorHandling-L1-1-0
        # * ...
        # try to remove it
        for f in os.listdir(self.dist_dir):
            if f.startswith('API-MS-Win'):
                os.remove(join(self.dist_dir, f))

if __name__ == '__main__':
    args = parse_args()
    builder = Builder()
    if args.update_po:
        builder.update_MUI_po()
    else:
        builder.build()
